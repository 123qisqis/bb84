import numpy as np
import pandas as pd
from bb84_protocol import BB84Protocol, EveConfig


class BB84Analyzer:

    @staticmethod
    def generate_dataset(n_sessions=50, n_qubits=50, noise_level=0.02, eve_rate=0.5):
        data = []

        # Sessions without Eve
        for _ in range(n_sessions // 2):
            bb84 = BB84Protocol(n_qubits)
            for _ in range(n_qubits):
                bb84.send_qubit(eve_intercepts=False)
                if np.random.rand() < noise_level:
                    bb84.bob_bits[-1] ^= 1

            qber, key_len = bb84.calculate_qber()
            data.append(
                {
                    "QBER": qber,
                    "Key Length": key_len,
                    "Sift Ratio": key_len / n_qubits,
                    "Eve Present": "No",
                }
            )

        for _ in range(n_sessions // 2):
            bb84 = BB84Protocol(n_qubits)
            for _ in range(n_qubits):
                eve_intercepts = np.random.rand() < eve_rate
                eve_basis = np.random.choice(["Z", "X"]) if eve_intercepts else None
                bb84.send_qubit(eve_intercepts=eve_intercepts, eve_basis=eve_basis)
                if np.random.rand() < noise_level:
                    bb84.bob_bits[-1] ^= 1

            qber, key_len = bb84.calculate_qber()
            data.append(
                {
                    "QBER": qber,
                    "Key Length": key_len,
                    "Sift Ratio": key_len / n_qubits,
                    "Eve Present": "Yes",
                }
            )

        return pd.DataFrame(data)

    @staticmethod
    def compute_summary_statistics(df):
        summary = (
            df.groupby("Eve Present")
            .agg(
                {
                    "QBER": ["mean", "std", "min", "max"],
                    "Sift Ratio": ["mean", "std"],
                    "Key Length": ["mean", "std"],
                }
            )
            .round(4)
        )

        return summary

    @staticmethod
    def test_scenarios(scenarios, n_qubits=50):
        results = []

        for name, eve_cfg, noise in scenarios:
            bb84 = BB84Protocol(n_qubits)
            qber, key_len = bb84.run_session(eve_cfg, noise)

            results.append(
                {
                    "Scenario": name,
                    "QBER": f"{qber:.3f}",
                    "Key Length": key_len,
                    "Sift Ratio": f"{key_len/n_qubits:.2%}",
                    "Detection": "High risk" if qber > 0.11 else "Acceptable",
                }
            )

        return pd.DataFrame(results)
