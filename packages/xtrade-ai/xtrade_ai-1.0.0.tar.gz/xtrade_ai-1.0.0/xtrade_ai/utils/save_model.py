"""
XTrade-AI Model Save/Load Module

Handles model persistence with compression and encryption.
"""

import base64
import hashlib
import json
import pickle
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from ..config import XTradeAIConfig
    from ..utils.logger import get_logger
except ImportError:
    from config import XTradeAIConfig
    from utils.logger import get_logger


class ModelSaver:
    """Save models with compression and encryption"""

    def __init__(
        self,
        save_dir: Optional[str] = None,
        encrypt: Optional[bool] = None,
        password: Optional[str] = None,
        config: Optional[XTradeAIConfig] = None,
    ):
        """Initialize model saver

        Args:
                save_dir: Directory to save models (defaults to config.persistence.save_dir)
                encrypt: Whether to encrypt models (defaults to config.persistence.encrypt_models)
                password: Password for encryption (defaults to config.persistence.password)
                config: Optional XTradeAIConfig to source defaults from
        """
        self.logger = get_logger(__name__)
        self.config = config or XTradeAIConfig()
        persistence = getattr(self.config, "persistence", None)
        self.save_dir = Path(
            save_dir or (persistence.save_dir if persistence else "models")
        )
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.encrypt = (
            bool(encrypt)
            if encrypt is not None
            else (bool(persistence.encrypt_models) if persistence else True)
        )
        self.password = (
            password
            if password is not None
            else (persistence.password if persistence else None)
        )

        # Setup encryption
        self.cipher = None
        if self.encrypt:
            if self.password:
                self.cipher = self._create_cipher_from_password(self.password)
            else:
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
                self._save_key(key)

    def save_framework(
        self,
        models: Dict[str, Any],
        metadata: Dict[str, Any],
        name: str = "xtrade_ai_framework",
    ) -> str:
        """Save entire framework with all models

        Args:
                models: Dictionary of model_name -> model object
                metadata: Framework metadata
                name: Framework name

        Returns:
                Path to saved framework file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        framework_name = f"{name}_{timestamp}"
        framework_dir = self.save_dir / framework_name
        framework_dir.mkdir(parents=True, exist_ok=True)

        # Save each model
        model_info = {}
        for model_name, model in models.items():
            try:
                model_path = self._save_model(model, model_name, framework_dir)
                model_info[model_name] = {
                    "path": str(model_path.relative_to(framework_dir)),
                    "type": type(model).__name__,
                }
            except Exception as e:
                self.logger.warning(f"Failed to save model {model_name}: {e}")
                # Create a placeholder for failed models
                model_info[model_name] = {
                    "path": f"{model_name}_failed.txt",
                    "type": "failed",
                    "error": str(e),
                }
                # Save error info
                error_path = framework_dir / f"{model_name}_failed.txt"
                with open(error_path, "w") as f:
                    f.write(f"Model {model_name} failed to save: {e}\n")

        # Merge metadata with config if requested
        meta = dict(metadata or {})
        try:
            if getattr(self.config.persistence, "include_config_in_metadata", True):
                meta.setdefault("config", {})
                meta["config"].update(
                    {
                        "model": self.config._dataclass_to_dict(self.config.model),
                        "trading": self.config._dataclass_to_dict(self.config.trading),
                        "environment": self.config._dataclass_to_dict(
                            self.config.environment
                        ),
                        "training": self.config._dataclass_to_dict(
                            self.config.training
                        ),
                        "indicators": self.config._dataclass_to_dict(
                            self.config.indicators
                        ),
                        "persistence": self.config._dataclass_to_dict(
                            self.config.persistence
                        ),
                    }
                )
        except Exception:
            pass

        # Save metadata
        meta["timestamp"] = timestamp
        meta["models"] = model_info
        meta["framework_version"] = "1.0.0"

        metadata_path = framework_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(meta, f, indent=2)

        # Compress to zip
        zip_path = self.save_dir / f"{framework_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in framework_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(framework_dir)
                    zipf.write(file_path, arcname)

        # Encrypt if enabled
        if self.encrypt:
            encrypted_path = self._encrypt_file(zip_path)
            zip_path.unlink()  # Remove unencrypted zip
            final_path = encrypted_path.with_suffix(".models")
            encrypted_path.rename(final_path)
            self.logger.info(f"Framework saved and encrypted: {final_path}")
        else:
            final_path = zip_path.with_suffix(".models")
            zip_path.rename(final_path)
            self.logger.info(f"Framework saved: {final_path}")

        # Clean up original framework directory and files
        self._cleanup_original_files(framework_dir)

        return str(final_path)

    def _save_model(self, model: Any, name: str, save_dir: Path) -> Path:
        """Save individual model with pickle error handling"""
        model_path = save_dir / f"{name}.pkl"

        # Handle different model types
        if hasattr(model, "state_dict"):
            # PyTorch model
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "model_class": type(model).__name__,
                    "model_config": getattr(model, "config", {}),
                },
                model_path,
            )
        elif hasattr(model, "save"):
            # Keras/TensorFlow model or SB3 model
            if hasattr(model, "predict") and hasattr(model, "learn"):
                # This is likely an SB3 model - use native save method
                sb3_path = save_dir / f"{name}_sb3.zip"
                try:
                    model.save(str(sb3_path))
                    model_path = sb3_path
                except Exception as e:
                    self.logger.warning(f"Failed to save SB3 model {name}: {e}")
                    # Fall back to pickle with clean copy
                    clean_model = self._create_clean_copy(model)
                    with open(model_path, "wb") as f:
                        pickle.dump(clean_model, f)
            else:
                # Keras/TensorFlow model
                model_keras_dir = save_dir / f"{name}_keras"
                model.save(model_keras_dir)
                model_path = model_keras_dir
        elif hasattr(model, "save_model"):
            # XGBoost model
            model_path = save_dir / f"{name}.xgb"
            model.save_model(model_path)
        else:
            # Generic model - try to create a clean copy
            try:
                clean_model = self._create_clean_copy(model)
                with open(model_path, "wb") as f:
                    pickle.dump(clean_model, f)
            except Exception as e:
                self.logger.warning(f"Failed to pickle model {name}: {e}")
                # Create a minimal representation
                minimal_model = {
                    "type": type(model).__name__,
                    "attributes": self._get_safe_attributes(model),
                    "error": f"Original model could not be pickled: {e}",
                }
                with open(model_path, "wb") as f:
                    pickle.dump(minimal_model, f)

        return model_path

    def _create_clean_copy(self, obj: Any) -> Any:
        """Create a clean copy of an object without file handles"""
        if hasattr(obj, "__dict__"):
            # Create a new instance of the same class
            new_obj = type(obj)()

            # Copy safe attributes
            for attr_name, attr_value in obj.__dict__.items():
                if self._is_safe_to_pickle(attr_value):
                    try:
                        setattr(new_obj, attr_name, attr_value)
                    except Exception:
                        # Skip problematic attributes
                        pass

            return new_obj
        else:
            # For objects without __dict__, return a minimal representation
            return {"type": type(obj).__name__, "repr": str(obj)}

    def _is_safe_to_pickle(self, obj: Any) -> bool:
        """Check if an object is safe to pickle"""
        unsafe_types = [
            "TextIOWrapper",
            "BufferedReader",
            "BufferedWriter",
            "FileIO",
            "SocketIO",
            "StreamReader",
            "StreamWriter",
        ]

        obj_type = type(obj).__name__
        if obj_type in unsafe_types:
            return False

        # Check for logger objects (they often contain file handles)
        if "logger" in str(type(obj)).lower() or "logging" in str(type(obj)).lower():
            return False

        # Check for file-like objects
        if hasattr(obj, "read") or hasattr(obj, "write") or hasattr(obj, "close"):
            return False

        return True

    def _get_safe_attributes(self, obj: Any) -> Dict[str, Any]:
        """Get safe attributes from an object"""
        safe_attrs = {}

        if hasattr(obj, "__dict__"):
            for attr_name, attr_value in obj.__dict__.items():
                if self._is_safe_to_pickle(attr_value):
                    try:
                        # Try to convert to a basic type
                        if isinstance(
                            attr_value, (int, float, str, bool, list, dict, tuple)
                        ):
                            safe_attrs[attr_name] = attr_value
                        elif isinstance(attr_value, np.ndarray):
                            safe_attrs[attr_name] = attr_value.tolist()
                        elif hasattr(attr_value, "tolist"):
                            safe_attrs[attr_name] = attr_value.tolist()
                        else:
                            safe_attrs[attr_name] = str(attr_value)
                    except Exception:
                        safe_attrs[attr_name] = f"<{type(attr_value).__name__}>"

        return safe_attrs

    def _encrypt_file(self, file_path: Path) -> Path:
        with open(file_path, "rb") as f:
            data = f.read()
        enc = self.cipher.encrypt(data)
        enc_path = file_path.with_suffix(".enc")
        with open(enc_path, "wb") as f:
            f.write(enc)
        return enc_path

    def _create_cipher_from_password(self, password: str) -> Fernet:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"xtrade_ai_salt",  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _save_key(self, key: bytes):
        key_path = self.save_dir / ".key"
        with open(key_path, "wb") as f:
            f.write(key)
        self.logger.warning(f"Encryption key saved to {key_path}. Keep this secure!")

    def _cleanup_original_files(self, framework_dir: Path):
        """Clean up original framework directory and files after successful save"""
        try:
            if framework_dir.exists():
                # Remove all files and subdirectories
                for item in framework_dir.rglob("*"):
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        # Remove empty directories
                        try:
                            item.rmdir()
                        except OSError:
                            # Directory not empty, skip
                            pass

                # Remove the main framework directory
                framework_dir.rmdir()
                self.logger.info(
                    f"Cleaned up original framework directory: {framework_dir}"
                )
            else:
                self.logger.warning(
                    f"Framework directory not found for cleanup: {framework_dir}"
                )
        except Exception as e:
            self.logger.error(f"Error during cleanup of original files: {e}")
            # Don't raise the exception to avoid breaking the save process


class ModelLoader:
    """Load models with decompression and decryption"""

    def __init__(self, password: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.password = password

    def load_framework(self, model_path: str) -> Dict[str, Any]:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        # Decrypt if encrypted
        if model_path.suffix == ".models":
            try:
                with zipfile.ZipFile(model_path, "r") as _:
                    is_encrypted = False
            except:
                is_encrypted = True
            if is_encrypted:
                decrypted_path = self._decrypt_file(model_path)
                zip_path = decrypted_path
            else:
                zip_path = model_path
        else:
            zip_path = model_path
        # Extract zip
        extract_dir = model_path.parent / f"extracted_{model_path.stem}"
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(extract_dir)
        # Load metadata
        metadata_path = extract_dir / "metadata.json"
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        # Load models
        models = {}
        successful_loads = 0
        failed_loads = 0

        for model_name, model_info in metadata["models"].items():
            if model_info.get("type") == "failed":
                self.logger.warning(
                    f"Model {model_name} failed to load: {model_info.get('error', 'Unknown error')}"
                )
                failed_loads += 1
                continue

            mpath = extract_dir / model_info["path"]
            try:
                loaded_model = self._load_model(mpath, model_info["type"])
                models[model_name] = loaded_model

                # Check if it's a placeholder (failed load)
                if hasattr(loaded_model, "loaded") and not loaded_model.loaded:
                    failed_loads += 1
                    self.logger.warning(
                        f"Model {model_name} loaded as placeholder due to: {loaded_model.error}"
                    )
                else:
                    successful_loads += 1
                    self.logger.debug(f"Successfully loaded model {model_name}")

            except Exception as e:
                self.logger.warning(f"Failed to load model {model_name}: {e}")
                failed_loads += 1
                # Create a placeholder for failed models
                models[model_name] = self._create_placeholder_model(
                    model_info["type"], str(e)
                )
        # Cleanup
        try:
            if is_encrypted and zip_path != model_path:
                zip_path.unlink()
        except Exception:
            pass
        self.logger.info(
            f"Framework loaded: {len(models)} models ({successful_loads} successful, {failed_loads} failed)"
        )
        return {"models": models, "metadata": metadata}

    def _load_model(self, model_path: Path, model_type: str) -> Any:
        """Load individual model with enhanced error handling"""
        try:
            if model_path.suffix == ".pkl":
                # Try PyTorch loading first
                try:
                    checkpoint = torch.load(
                        model_path, map_location="cpu", weights_only=False
                    )
                    if "state_dict" in checkpoint:
                        return checkpoint
                except Exception as torch_error:
                    self.logger.debug(
                        f"PyTorch loading failed for {model_path}: {torch_error}"
                    )
                    # Fall back to pickle loading
                    pass

                # Try pickle loading with enhanced error handling
                try:
                    with open(model_path, "rb") as f:
                        return pickle.load(f)
                except Exception as pickle_error:
                    self.logger.warning(
                        f"Pickle loading failed for {model_path}: {pickle_error}"
                    )
                    # Return a placeholder object
                    return self._create_placeholder_model(model_type, str(pickle_error))

            elif model_path.suffix == ".xgb":
                # Handle XGBoost models with graceful fallback
                try:
                    import xgboost as xgb

                    model = xgb.XGBClassifier()
                    model.load_model(model_path)
                    return model
                except ImportError:
                    self.logger.warning("XGBoost not available, creating placeholder")
                    return self._create_placeholder_model(
                        "XGBoostModule", "XGBoost module not available"
                    )
                except Exception as xgb_error:
                    self.logger.warning(f"XGBoost loading failed: {xgb_error}")
                    return self._create_placeholder_model(
                        "XGBoostModule", str(xgb_error)
                    )

            elif model_path.is_dir() and (model_path / "saved_model.pb").exists():
                # Handle TensorFlow/Keras models
                try:
                    import tensorflow as tf

                    return tf.keras.models.load_model(model_path)
                except ImportError:
                    self.logger.warning(
                        "TensorFlow not available, creating placeholder"
                    )
                    return self._create_placeholder_model(
                        "TensorFlowModel", "TensorFlow not available"
                    )
                except Exception as tf_error:
                    self.logger.warning(f"TensorFlow loading failed: {tf_error}")
                    return self._create_placeholder_model(
                        "TensorFlowModel", str(tf_error)
                    )
            else:
                # Generic pickle loading with error handling
                try:
                    with open(model_path, "rb") as f:
                        return pickle.load(f)
                except Exception as generic_error:
                    self.logger.warning(
                        f"Generic loading failed for {model_path}: {generic_error}"
                    )
                    return self._create_placeholder_model(
                        model_type, str(generic_error)
                    )

        except Exception as e:
            self.logger.error(f"Unexpected error loading {model_path}: {e}")
            return self._create_placeholder_model(model_type, str(e))

    def _create_placeholder_model(self, model_type: str, error_message: str) -> Any:
        """Create a placeholder model when loading fails"""

        class PlaceholderModel:
            def __init__(self, model_type: str, error: str):
                self.model_type = model_type
                self.error = error
                self.loaded = False

            def __repr__(self):
                return f"PlaceholderModel({self.model_type}, error='{self.error}')"

            def __str__(self):
                return f"<PlaceholderModel: {self.model_type} (failed to load: {self.error})>"

        return PlaceholderModel(model_type, error_message)

    def _decrypt_file(self, file_path: Path) -> Path:
        key_path = file_path.parent / ".key"
        if key_path.exists() and not self.password:
            with open(key_path, "rb") as f:
                key = f.read()
            cipher = Fernet(key)
        elif self.password:
            cipher = self._create_cipher_from_password(self.password)
        else:
            raise ValueError("No decryption key or password provided")
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_path = file_path.with_suffix(".zip")
        with open(decrypted_path, "wb") as f:
            f.write(decrypted_data)
        return decrypted_path

    def _create_cipher_from_password(self, password: str) -> Fernet:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"xtrade_ai_salt",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
