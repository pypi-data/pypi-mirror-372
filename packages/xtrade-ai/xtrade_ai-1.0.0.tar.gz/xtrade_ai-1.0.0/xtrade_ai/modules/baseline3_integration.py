from typing import Optional, Tuple

try:
    from ..config import XTradeAIConfig
    from ..utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

    from ..config import XTradeAIConfig


try:
    from stable_baselines3 import A2C, DQN, PPO, SAC, TD3

    except_import_error = None
except Exception as e:
    PPO = DQN = SAC = A2C = TD3 = None
    except_import_error = e

# sb3-contrib for TRPO, QRDQN
try:
    from sb3_contrib import QRDQN, TRPO

    sb3c_error = None
except Exception as e:
    TRPO = QRDQN = None
    sb3c_error = e


class Baseline3Integration:
    """Wrapper around Stable-Baselines3 algorithms with safe fallbacks."""

    def __init__(self, config: Optional[XTradeAIConfig] = None):
        self.config = config or XTradeAIConfig()
        self.logger = get_logger(__name__)
        self.algorithm_name: Optional[str] = None
        self.model = None

    def create(self, algorithm: str, env) -> None:
        self.algorithm_name = algorithm.upper()
        if all(x is None for x in [PPO, DQN, SAC, A2C, TD3]) and all(
            y is None for y in [TRPO, QRDQN]
        ):
            self.logger.warning(
                f"Stable-Baselines3 not available: {except_import_error}; contrib: {sb3c_error}"
            )
            self.model = None
            return
        algo_cfg = self.config.get_algorithm_config(self.algorithm_name)
        if self.algorithm_name == "PPO":
            self.model = PPO("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "DQN":
            self.model = DQN("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "SAC":
            self.model = SAC("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "A2C" and A2C is not None:
            self.model = A2C("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "TD3" and TD3 is not None:
            self.model = TD3("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "TRPO" and TRPO is not None:
            self.model = TRPO("MlpPolicy", env, **algo_cfg)
        elif self.algorithm_name == "QRDQN" and QRDQN is not None:
            self.model = QRDQN("MlpPolicy", env, **algo_cfg)
        else:
            raise ValueError(f"Unsupported or unavailable algorithm: {algorithm}")

    def load(self, algorithm: str, env, path: str) -> None:
        """Load a saved SB3 model for fine-tuning."""
        self.algorithm_name = algorithm.upper()
        try:
            if self.algorithm_name == "PPO" and PPO is not None:
                self.model = PPO.load(path, env=env)
            elif self.algorithm_name == "DQN" and DQN is not None:
                self.model = DQN.load(path, env=env)
            elif self.algorithm_name == "SAC" and SAC is not None:
                self.model = SAC.load(path, env=env)
            elif self.algorithm_name == "A2C" and A2C is not None:
                self.model = A2C.load(path, env=env)
            elif self.algorithm_name == "TD3" and TD3 is not None:
                self.model = TD3.load(path, env=env)
            elif self.algorithm_name == "TRPO" and TRPO is not None:
                self.model = TRPO.load(path, env=env)
            elif self.algorithm_name == "QRDQN" and QRDQN is not None:
                self.model = QRDQN.load(path, env=env)
            else:
                raise ValueError(
                    f"Unsupported or unavailable algorithm for load: {algorithm}"
                )
        except Exception as e:
            self.logger.error(f"Failed to load model from {path}: {e}")
            raise

    def train(self, total_timesteps: int) -> None:
        if self.model is None:
            self.logger.info("SB3 model is None; skipping training.")
            return
        self.model.learn(
            total_timesteps=total_timesteps,
            log_interval=self.config.training.log_interval,
        )

    def predict_action(self, observation) -> Tuple[int, float]:
        if self.model is None:
            return 2, 0.25
        action, state = self.model.predict(observation, deterministic=True)
        return int(action), 0.8

    def get_model(self):
        return self.model

    def save_model(self, path: str) -> None:
        """Save the SB3 model to a file."""
        if self.model is None:
            self.logger.warning("No model to save")
            return

        try:
            self.model.save(path)
            self.logger.info(f"SB3 model saved to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save SB3 model: {e}")
            raise

    def __getstate__(self):
        """Custom pickle method to handle file handles and logger objects."""
        state = self.__dict__.copy()

        # Remove logger to avoid pickle issues
        if "logger" in state:
            del state["logger"]

        # Remove model if it contains file handles
        if "model" in state and state["model"] is not None:
            # Instead of the actual model, store metadata
            state["model"] = {
                "type": "sb3_model",
                "algorithm": self.algorithm_name,
                "policy_type": "MlpPolicy",
                "config": (
                    self.config.get_algorithm_config(self.algorithm_name)
                    if self.algorithm_name
                    else {}
                ),
            }

        return state

    def __setstate__(self, state):
        """Custom unpickle method to restore the object."""
        self.__dict__.update(state)

        # Restore logger
        self.logger = get_logger(__name__)

        # Model will need to be recreated when needed
        if (
            "model" in state
            and isinstance(state["model"], dict)
            and state["model"].get("type") == "sb3_model"
        ):
            self.model = None  # Will be recreated when create() is called
