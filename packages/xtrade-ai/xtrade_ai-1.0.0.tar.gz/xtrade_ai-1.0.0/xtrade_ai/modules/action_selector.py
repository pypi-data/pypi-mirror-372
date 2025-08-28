from typing import Dict, List, Optional

import numpy as np

try:
    from ..data_structures import (
        ActionType,
        CloseOrderDecision,
        RiskAssessment,
        TradingDecision,
    )
except ImportError:
    from data_structures import (
        ActionType,
        CloseOrderDecision,
        RiskAssessment,
        TradingDecision,
    )


class ActionSelector:
    """Combine multiple model predictions to choose final action."""

    def __init__(self):
        pass

    def select(
        self,
        policy_action: int,
        policy_confidence: float,
        close_decision: CloseOrderDecision,
        technical_signal_logits: np.ndarray,
        risk: RiskAssessment,
        ensemble_weights: Optional[Dict[str, float]] = None,
    ) -> TradingDecision:
        if close_decision and close_decision.should_close:
            return TradingDecision(
                action=ActionType.CLOSE, confidence=0.9, reasons=["close_priority"]
            )

        if technical_signal_logits is not None and technical_signal_logits.size == 3:
            exp = np.exp(technical_signal_logits - np.max(technical_signal_logits))
            probs = exp / exp.sum()
            ta_action = int(np.argmax(probs))  # 0 buy,1 sell,2 hold
            ta_conf = float(probs[ta_action])
        else:
            ta_action, ta_conf = 2, 0.33

        # Determine weights
        if (
            ensemble_weights
            and "policy" in ensemble_weights
            and "ta" in ensemble_weights
        ):
            w_policy = max(0.0, float(ensemble_weights["policy"]))
            w_ta = max(0.0, float(ensemble_weights["ta"]))
            if w_policy + w_ta <= 1e-12:
                w_policy, w_ta = 0.5, 0.5
            weights = np.array([w_policy, w_ta], dtype=np.float32)
        else:
            c1, c2 = max(1e-6, float(policy_confidence)), max(1e-6, float(ta_conf))
            weights = np.array([c1, c2])
            weights = weights / (weights.sum() + 1e-12)

        votes = np.array([policy_action, ta_action])

        if votes[0] == votes[1]:
            final_action = int(votes[0])
            final_conf = float(weights.max())
        else:
            if risk and risk.is_high_risk():
                final_action = ActionType.HOLD.value
                final_conf = 0.6
            else:
                idx = int(weights.argmax())
                final_action = int(votes[idx])
                final_conf = float(weights[idx])

        position_size = float(risk.position_size_adjustment) if risk else 0.0
        reasons = []
        if ensemble_weights:
            reasons.append(
                f"ensemble_weights=policy:{weights[0]:.2f},ta:{weights[1]:.2f}"
            )
        return TradingDecision(
            action=ActionType(final_action),
            confidence=final_conf,
            position_size=position_size,
            reasons=reasons,
        )
