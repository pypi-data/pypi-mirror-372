"""
Gym to Gymnasium Monkey Patch
This module intercepts gym imports and redirects them to gymnasium
to eliminate deprecation warnings from dependencies like stable-baselines3
"""

import sys
import warnings


def patch_gym_imports():
    """
    Monkey patch gym imports to use gymnasium instead
    """

    # Suppress all warnings first
    warnings.filterwarnings("ignore")

    try:
        # Import gymnasium first
        import gymnasium as gym_replacement

        # Create a fake gym module that's actually gymnasium
        class GymModule:
            def __getattr__(self, name):
                return getattr(gym_replacement, name)

            def __dir__(self):
                return dir(gym_replacement)

            @property
            def __version__(self):
                return getattr(
                    gym_replacement, "__version__", "0.26.2"
                )  # Fake version to satisfy checks

        # Replace gym in sys.modules before it can be imported
        fake_gym = GymModule()
        sys.modules["gym"] = fake_gym
        sys.modules["gym.spaces"] = gym_replacement.spaces
        sys.modules["gym.envs"] = getattr(gym_replacement, "envs", None)

        # Also patch the actual import mechanism
        import builtins

        original_import = builtins.__import__

        def patched_import(name, *args, **kwargs):
            if name == "gym" or name.startswith("gym."):
                # Redirect gym imports to gymnasium
                new_name = name.replace("gym", "gymnasium", 1)
                try:
                    return original_import(new_name, *args, **kwargs)
                except ImportError:
                    # If gymnasium doesn't have the module, return our fake gym
                    if name == "gym":
                        return fake_gym
                    else:
                        raise
            return original_import(name, *args, **kwargs)

        builtins.__import__ = patched_import

        # print("✅ Gym → Gymnasium monkey patch applied successfully")

    except ImportError as e:
        # print(f"⚠️ Could not apply gym patch: {e}")
        # Fallback to just suppressing warnings
        warnings.filterwarnings("ignore")


def setup_comprehensive_warning_suppression():
    """
    Set up the most comprehensive warning suppression possible
    """

    import logging
    import os

    # Environment variables for all libraries
    env_vars = {
        # Python warnings
        "PYTHONWARNINGS": "ignore",
        "PYTHONDONTWRITEBYTECODE": "1",
        # Gym/Gymnasium warnings
        "GYMNASIUM_NO_DEPRECATION_WARNINGS": "1",
        "GYM_IGNORE_DEPRECATION_WARNINGS": "1",
        "GYM_DEPRECATION_WARNINGS": "0",
        # TensorFlow warnings (comprehensive)
        "TF_CPP_MIN_LOG_LEVEL": "3",  # Only errors
        "TF_ENABLE_ONEDNN_OPTS": "0",  # Disable oneDNN warnings
        "TF_ENABLE_DEPRECATION_WARNINGS": "0",
        "TF_ENABLE_GPU_GARBAGE_COLLECTION": "0",
        "TF_DISABLE_SEGMENT_REDUCTION_OP_DETERMINISM_EXCEPTIONS": "1",
        "TF_DETERMINISTIC_OPS": "0",
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "CUDA_VISIBLE_DEVICES": "",  # Force CPU to avoid CUDA warnings
        # PyTorch warnings
        "PYTORCH_DISABLE_PER_WORKER_INIT": "1",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    # Python warnings
    warnings.simplefilter("ignore")
    warnings.filterwarnings("ignore")

    # Suppress all warning categories
    warning_categories = [
        UserWarning,
        FutureWarning,
        DeprecationWarning,
        PendingDeprecationWarning,
        ImportWarning,
        ResourceWarning,
    ]

    for category in warning_categories:
        warnings.filterwarnings("ignore", category=category)

    # TensorFlow specific logging suppression
    try:
        # Disable TensorFlow and related library logging
        tf_loggers = [
            "tensorflow",
            "tensorflow.python",
            "tensorflow.python.util.deprecation",
            "absl",
            "absl.logging",
            "tensorboard",
            "keras",
        ]

        for logger_name in tf_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.ERROR)
            logger.disabled = True

        # Early TensorFlow configuration
        try:
            import tensorflow as tf

            tf.get_logger().setLevel("ERROR")
            tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

            # Disable specific TensorFlow optimizations that cause warnings
            try:
                tf.config.optimizer.set_experimental_options(
                    {"disable_meta_optimizer": True}
                )
            except (AttributeError, RuntimeError):
                pass

        except ImportError:
            pass

    except ImportError:
        pass

    # Specific message patterns to ignore
    message_patterns = [
        # Gym warnings
        ".*Gym has been unmaintained.*",
        ".*upgrade to Gymnasium.*",
        ".*maintained drop-in replacement.*",
        ".*gymnasium.farama.org.*",
        ".*support NumPy 2.*",
        ".*Please upgrade to Gymnasium.*",
        ".*unmaintained since 2022.*",
        ".*contact the authors.*",
        ".*simply replace.*import gym.*",
        # TensorFlow warnings
        ".*oneDNN custom operations.*",
        ".*slightly different numerical results.*",
        ".*floating-point round-off errors.*",
        ".*TF_ENABLE_ONEDNN_OPTS.*",
        ".*tf.losses.sparse_softmax_cross_entropy is deprecated.*",
        ".*tf.compat.v1.losses.sparse_softmax_cross_entropy.*",
        ".*deprecated.*",
        # pkg_resources warnings
        ".*pkg_resources is deprecated.*",
        ".*setuptools.pypa.io.*",
        ".*slated for removal.*",
        ".*Refrain from using.*",
    ]

    for pattern in message_patterns:
        for category in warning_categories:
            warnings.filterwarnings("ignore", message=pattern, category=category)

    # Suppress by module patterns
    module_patterns = [
        ".*gym.*",
        ".*stable_baselines3.*",
        ".*tensorflow.*",
        ".*keras.*",
        ".*absl.*",
        ".*tensorboard.*",
        ".*pkg_resources.*",
        ".*setuptools.*",
    ]

    for module_pattern in module_patterns:
        for category in warning_categories:
            warnings.filterwarnings("ignore", category=category, module=module_pattern)


# Apply patches immediately when imported
setup_comprehensive_warning_suppression()
patch_gym_imports()
