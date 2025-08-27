from typing import Any


class PolicyValidator:
    """Validate policy and environment compatibility."""

    def validate_observation(self, obs, expected_dim: int) -> None:
        if not hasattr(obs, "shape"):
            raise ValueError("Observation has no shape")
        if obs.shape[-1] != expected_dim:
            raise ValueError(
                f"Unexpected observation shape {obs.shape}, expected last dim {expected_dim}"
            )

    def validate_action(self, action: int, action_space_n: int) -> None:
        if not (0 <= int(action) < int(action_space_n)):
            raise ValueError(
                f"Action {action} out of bounds for Discrete({action_space_n})"
            )
