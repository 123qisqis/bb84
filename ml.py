import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from bb84_protocol import BB84Protocol


class MLDetector:
    """Machine learning based eavesdropping detector"""

    def __init__(self):
        self.model = None
        self.is_trained = False

    def generate_training_data(self, n_sessions=50, n_qubits=50):
        """Generate training dataset from BB84 sessions"""
        data = []

        # Generate sessions without eavesdropper
        for _ in range(n_sessions):
            bb84 = BB84Protocol(n_qubits)
            for _ in range(n_qubits):
                bb84.send_qubit(eve_intercepts=False)
            qber, key_len = bb84.calculate_qber()
            data.append(
                {"error_rate": qber, "sift_ratio": key_len / n_qubits, "eve": 0}
            )

        # Generate sessions with eavesdropper
        for _ in range(n_sessions):
            bb84 = BB84Protocol(n_qubits)
            intercept_rate = np.random.uniform(0.3, 1.0)
            for _ in range(n_qubits):
                eve_intercepts = np.random.rand() < intercept_rate
                eve_basis = np.random.choice(["Z", "X"]) if eve_intercepts else None
                bb84.send_qubit(eve_intercepts=eve_intercepts, eve_basis=eve_basis)
            qber, key_len = bb84.calculate_qber()
            data.append(
                {"error_rate": qber, "sift_ratio": key_len / n_qubits, "eve": 1}
            )

        return pd.DataFrame(data)

    def train(self, n_sessions=50, n_qubits=50):
        """Train the ML model"""
        df = self.generate_training_data(n_sessions, n_qubits)

        X = df[["error_rate", "sift_ratio"]]
        y = df["eve"]

        self.model = LogisticRegression(random_state=42)
        self.model.fit(X, y)
        self.is_trained = True

        return self.model

    def predict(self, qber, sift_ratio):
        """Predict if eavesdropper is present"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        features = [[qber, sift_ratio]]
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0, 1]

        return prediction, probability

    def evaluate_scenarios(self, scenarios, n_qubits=50):
        """Evaluate multiple attack scenarios"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        results = []

        for name, eve_cfg in scenarios:
            bb84 = BB84Protocol(n_qubits)
            for _ in range(n_qubits):
                eve_intercepts = eve_cfg.active and (
                    np.random.rand() < eve_cfg.intercept_rate
                )
                eve_basis = np.random.choice(["Z", "X"]) if eve_intercepts else None
                bb84.send_qubit(eve_intercepts=eve_intercepts, eve_basis=eve_basis)

            qber, key_len = bb84.calculate_qber()
            prediction, probability = self.predict(qber, key_len / n_qubits)

            results.append(
                {
                    "Scenario": name,
                    "QBER": qber,
                    "Sift Ratio": key_len / n_qubits,
                    "ML Confidence": probability,
                    "Prediction": "EVE DETECTED" if prediction == 1 else "SECURE",
                }
            )

        return pd.DataFrame(results)
