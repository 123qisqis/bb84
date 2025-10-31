# %%
import numpy as np
from qiskit import QuantumCircuit, transpile
from dataclasses import dataclass

try:
    from qiskit_aer import AerSimulator

    SIMULATOR = AerSimulator()
except ImportError:
    from qiskit.providers.basic_provider import BasicProvider

    SIMULATOR = BasicProvider().get_backend("basic_simulator")

# %%
@dataclass
class EveConfig:
    active: bool = False
    intercept_rate: float = 1.0


class BB84Protocol:
    def __init__(self, n_qubits=20):
        self.n_qubits = n_qubits
        self.simulator = SIMULATOR
        self.reset()

    def reset(self):
        # New protocol session
        self.alice_bits = np.random.randint(0, 2, self.n_qubits)
        self.alice_bases = np.random.choice(["Z", "X"], self.n_qubits)
        self.bob_bases = np.random.choice(["Z", "X"], self.n_qubits)
        self.bob_bits = []
        self.eve_interceptions = []
        self.current_round = 0

    def prepare_qubit(self, bit, basis):
        qc = QuantumCircuit(1, 1)
        if bit == 1: 
            qc.x(0) # not gate
        if basis == "X":
            qc.h(0) # hadamard to change basis
        return qc

    def measure_qubit(self, qc, basis):
        qc_copy = qc.copy() # copy not to disturb the original
        if basis == "X":
            qc_copy.h(0)
        qc_copy.measure(0, 0)

        qc_transpiled = transpile(qc_copy, self.simulator)
        result = self.simulator.run(qc_transpiled, shots=1).result()
        measured_bit = int(list(result.get_counts().keys())[0])
        return measured_bit

    def send_qubit(self, eve_intercepts=False, eve_basis=None):
        alice_bit = self.alice_bits[self.current_round]
        alice_basis = self.alice_bases[self.current_round]
        bob_basis = self.bob_bases[self.current_round]

        qc = self.prepare_qubit(alice_bit, alice_basis)

        if eve_intercepts:
            eve_bit = self.measure_qubit(qc, eve_basis)
            qc = self.prepare_qubit(eve_bit, eve_basis)
            self.eve_interceptions.append(
                {
                    "round": self.current_round,
                    "eve_basis": eve_basis,
                    "eve_bit": eve_bit,
                }
            )
        else:
            self.eve_interceptions.append(None)

        bob_bit = self.measure_qubit(qc, bob_basis)
        self.bob_bits.append(bob_bit)

        self.current_round += 1
        return alice_bit, alice_basis, bob_bit, bob_basis

    def calculate_qber(self, up_to_round=None):
        if up_to_round is None:
            up_to_round = self.current_round

        matching_bases = self.alice_bases[:up_to_round] == self.bob_bases[:up_to_round]
        alice_sifted = self.alice_bits[:up_to_round][matching_bases]
        bob_sifted = np.array(self.bob_bits[:up_to_round])[matching_bases]

        if len(alice_sifted) == 0:
            return 0.0, 0

        errors = np.sum(alice_sifted != bob_sifted)
        qber = errors / len(alice_sifted)
        return qber, len(alice_sifted)

    def run_session(self, eve_config=None, noise_prob=0.0):
        if eve_config is None:
            eve_config = EveConfig(active=False)

        for i in range(self.n_qubits):
            eve_intercepts = eve_config.active and (
                np.random.rand() < eve_config.intercept_rate
            )
            eve_basis = np.random.choice(["Z", "X"]) if eve_intercepts else None
            self.send_qubit(eve_intercepts=eve_intercepts, eve_basis=eve_basis)

            if np.random.rand() < noise_prob:
                self.bob_bits[-1] ^= 1

        return self.calculate_qber()

# %%

protocol = BB84Protocol(n_qubits=50)

# No Eve, no noise, qber 0
qber_no_eve, sifted_len_no_eve = protocol.run_session()
print(f"sifted bits: {sifted_len_no_eve}, qber: {qber_no_eve:.2%}")

# All qubits intercepted
protocol.reset()
qber_with_eve, sifted_len_with_eve = protocol.run_session(
    eve_config=EveConfig(active=True, intercept_rate=1.0)
)
print(f"\nintercepting all qubits:")
print(f"  sifted bits: {sifted_len_with_eve}, qber: {qber_with_eve:.2%}")

# expecting higher qber with evesdropper
if qber_with_eve > qber_no_eve:
    print("pass")
else:
    print("fail")

# %%
