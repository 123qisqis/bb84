# %%
from bb84_protocol import BB84Protocol


class BB84Game:

    def __init__(self, n_qubits=20, threshold=0.12):
        self.bb84 = BB84Protocol(n_qubits)
        self.threshold = threshold
        self.n_qubits = n_qubits
        self.score = {"intercepted": 0, "detected": 0}
        self.current_round = 0
        self.qber_history = []
        self.key_len_history = []

    def reset(self):
        self.bb84.reset()
        self.score = {"intercepted": 0, "detected": 0}
        self.current_round = 0
        self.qber_history = []
        self.key_len_history = []

    def intercept_qubit(self, basis):
        alice_bit, alice_basis, bob_bit, bob_basis = self.bb84.send_qubit(
            eve_intercepts=True, eve_basis=basis
        )
        self.score["intercepted"] += 1
        self._update_stats()
        self.current_round += 1

        return {
            "alice_bit": alice_bit,
            "alice_basis": alice_basis,
            "bob_bit": bob_bit,
            "bob_basis": bob_basis,
            "eve_basis": basis,
        }

    def let_pass_qubit(self):
        alice_bit, alice_basis, bob_bit, bob_basis = self.bb84.send_qubit(
            eve_intercepts=False
        )
        self._update_stats()
        self.current_round += 1

        return {
            "alice_bit": alice_bit,
            "alice_basis": alice_basis,
            "bob_bit": bob_bit,
            "bob_basis": bob_basis,
            "eve_basis": None,
        }

    def _update_stats(self):
        qber, key_len = self.bb84.calculate_qber(self.current_round + 1)
        if key_len > 0:
            self.qber_history.append(qber)
            self.key_len_history.append(key_len)

    def is_game_over(self):
        return self.current_round >= self.n_qubits

    def get_final_results(self):
        final_qber, final_key_len = self.bb84.calculate_qber()

        detected = final_qber > self.threshold

        if detected:
            final_score = -100
            verdict = "DETECTED"
        else:
            if self.score["intercepted"] > 0:
                final_score = self.score["intercepted"] * 10
                verdict = "UNDETECTED"
            else:
                final_score = 0
                verdict = "SAFE"

        return {
            "final_qber": final_qber,
            "final_key_len": final_key_len,
            "threshold": self.threshold,
            "detected": detected,
            "final_score": final_score,
            "verdict": verdict,
            "intercepted": self.score["intercepted"],
        }

    def get_current_stats(self):
        if self.current_round > 0:
            qber, key_len = self.bb84.calculate_qber(self.current_round)
        else:
            qber, key_len = 0.0, 0

        return {
            "current_round": self.current_round,
            "qber": qber,
            "key_len": key_len,
            "intercepted": self.score["intercepted"],
            "progress": self.current_round / self.n_qubits,
        }

    def get_transmission_history(self):
        history = []

        for i in range(self.current_round):
            alice_bit = self.bb84.alice_bits[i]
            alice_basis = self.bb84.alice_bases[i]
            bob_bit = self.bb84.bob_bits[i]
            bob_basis = self.bb84.bob_bases[i]
            eve_interception = self.bb84.eve_interceptions[i]

            basis_match = alice_basis == bob_basis
            bit_match = alice_bit == bob_bit

            if eve_interception:
                status = f"INTERCEPTED (Eve: {eve_interception['eve_basis']} basis)"
            else:
                status = "LET PASS"

            if basis_match:
                if bit_match:
                    result = "Match - Kept"
                else:
                    result = "ERROR - Kept but wrong"
            else:
                result = "Different bases - Discarded"

            history.append(
                {
                    "round": i + 1,
                    "alice_basis": alice_basis,
                    "alice_bit": alice_bit,
                    "bob_basis": bob_basis,
                    "bob_bit": bob_bit,
                    "status": status,
                    "result": result,
                }
            )

        return history


# %%
import numpy as np

np.random.seed(42)
game = BB84Game(n_qubits=20, threshold=0.11)

# Test no interception
game.reset()
while not game.is_game_over():
    game.let_pass_qubit()
results = game.get_final_results()
assert (
    abs(results["final_qber"]) < 1e-6
), f"expected qber 0, got {results['final_qber']}"
assert not results["detected"], "should not be detected"
print("Test 1 passed, no iterception, qber0")

# Test with interception
game.reset()
while not game.is_game_over():
    game.intercept_qubit(basis="X")
results = game.get_final_results()
assert results["detected"], f"expected detection, qber={results['final_qber']}"
print("Test 2 passed")

# %%
