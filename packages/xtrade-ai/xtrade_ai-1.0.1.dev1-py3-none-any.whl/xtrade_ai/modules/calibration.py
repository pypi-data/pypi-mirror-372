from typing import Any, Dict, Optional

import numpy as np


class TemperatureScaler:
    """Temperature scaling for logits calibration."""

    def __init__(self, temperature: float = 1.0):
        self.temperature = max(1e-6, float(temperature))

    def fit(self, logits: np.ndarray, labels: np.ndarray) -> None:
        # Simple search over a small grid (placeholder)
        best_t = self.temperature
        best_loss = float("inf")
        for t in np.linspace(0.5, 5.0, 20):
            p = self._softmax(logits / t)
            loss = -np.mean(np.log(p[np.arange(len(labels)), labels] + 1e-12))
            if loss < best_loss:
                best_loss, best_t = loss, float(t)
        self.temperature = best_t

    def transform(self, logits: np.ndarray) -> np.ndarray:
        return logits / self.temperature

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        x = x - x.max(axis=1, keepdims=True)
        exp = np.exp(x)
        return exp / (exp.sum(axis=1, keepdims=True) + 1e-12)


class PlattScaler:
    """Platt scaling for binary probabilities (sigmoid)."""

    def __init__(self):
        self.a = 1.0
        self.b = 0.0

    def fit(self, scores: np.ndarray, labels: np.ndarray) -> None:
        # Logistic regression fit (very simple gradient steps)
        a, b = 1.0, 0.0
        lr = 0.01
        for _ in range(200):
            z = a * scores + b
            p = 1.0 / (1.0 + np.exp(-z))
            grad_a = np.mean((p - labels) * scores)
            grad_b = np.mean(p - labels)
            a -= lr * grad_a
            b -= lr * grad_b
        self.a, self.b = float(a), float(b)

    def transform(self, scores: np.ndarray) -> np.ndarray:
        z = self.a * scores + self.b
        return 1.0 / (1.0 + np.exp(-z))


class EnsembleCalibrator:
    """Calibrate ensemble weights based on validation performance."""

    def __init__(self):
        self.weights: Dict[str, float] = {"policy": 0.5, "ta": 0.5}

    def fit(
        self, policy_conf: np.ndarray, ta_conf: np.ndarray, labels: np.ndarray
    ) -> None:
        # Grid over weights
        best = None
        best_acc = -1
        for w in np.linspace(0.0, 1.0, 21):
            combo = w * policy_conf + (1 - w) * ta_conf
            pred = (combo >= 0.5).astype(int)
            acc = (pred == labels).mean()
            if acc > best_acc:
                best_acc = acc
                best = w
        self.weights["policy"] = float(best)
        self.weights["ta"] = float(1 - best)

    def get_weights(self) -> Dict[str, float]:
        return dict(self.weights)
