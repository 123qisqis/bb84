import matplotlib.pyplot as plt
import numpy as np


class BB84Visualizer:

    @staticmethod
    def plot_qber_gauge(qber, threshold, title="Current QBER"):
        fig, ax = plt.subplots(figsize=(6, 3))

        values = [threshold * 0.5, threshold * 0.5, 0.3 - threshold]
        colors = ["green", "yellow", "red"]

        ax.barh(0, values[0], color=colors[0], alpha=0.3)
        ax.barh(0, values[1], left=values[0], color=colors[1], alpha=0.3)
        ax.barh(0, values[2], left=values[0] + values[1], color=colors[2], alpha=0.3)

        ax.plot([qber, qber], [0, 0.5], "k-", linewidth=3)
        ax.plot(qber, 0.5, "ko", markersize=10)

        ax.set_xlim(0, 0.3)
        ax.set_ylim(-0.2, 1)
        ax.set_yticks([])
        ax.set_xlabel("QBER")
        ax.set_title(title)
        ax.axvline(
            threshold, color="orange", linestyle="--", linewidth=2, label="Threshold"
        )
        ax.legend()

        return fig

    @staticmethod
    def plot_qber_evolution(qber_history, threshold):
        fig, ax = plt.subplots(figsize=(8, 3))
        rounds = list(range(1, len(qber_history) + 1))

        ax.plot(rounds, qber_history, "b-", linewidth=2, label="QBER")
        ax.axhline(
            threshold, color="red", linestyle="--", linewidth=2, label="Threshold"
        )
        ax.fill_between(
            rounds, 0, threshold, alpha=0.2, color="green", label="Safe Zone"
        )
        ax.fill_between(
            rounds, threshold, 0.3, alpha=0.2, color="red", label="Danger Zone"
        )

        ax.set_xlabel("Round")
        ax.set_ylabel("QBER")
        ax.set_title("Quantum Bit Error Rate Evolution")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    @staticmethod
    def plot_key_length_growth(key_len_history):
        fig, ax = plt.subplots(figsize=(8, 3))
        rounds = list(range(1, len(key_len_history) + 1))

        ax.plot(rounds, key_len_history, "g-", linewidth=2)
        ax.set_xlabel("Round")
        ax.set_ylabel("Sifted Key Length")
        ax.set_title("Key Length Growth")
        ax.grid(True, alpha=0.3)

        return fig

    @staticmethod
    def plot_game_statistics(qber_history, key_len_history, threshold):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        rounds = list(range(1, len(qber_history) + 1))

        # QBER evolution
        ax1.plot(rounds, qber_history, "b-", linewidth=2)
        ax1.axhline(
            threshold, color="red", linestyle="--", linewidth=2, label="Threshold"
        )
        ax1.fill_between(rounds, 0, threshold, alpha=0.2, color="green")
        ax1.fill_between(
            rounds, threshold, max(qber_history + [0.3]), alpha=0.2, color="red"
        )
        ax1.set_xlabel("Round")
        ax1.set_ylabel("QBER")
        ax1.set_title("QBER Evolution")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Key length growth
        ax2.plot(rounds, key_len_history, "g-", linewidth=2)
        ax2.set_xlabel("Round")
        ax2.set_ylabel("Sifted Key Length")
        ax2.set_title("Key Length Growth")
        ax2.grid(True, alpha=0.3)

        return fig

    @staticmethod
    def plot_qber_distribution(df, threshold=0.11):
        fig, ax = plt.subplots(figsize=(6, 4))

        no_eve = df[df["Eve Present"] == "No"]["QBER"]
        eve = df[df["Eve Present"] == "Yes"]["QBER"]

        ax.hist(no_eve, alpha=0.6, bins=20, label="No Eve", color="green")
        ax.hist(eve, alpha=0.6, bins=20, label="Eve", color="red")
        ax.axvline(
            threshold, color="orange", linestyle="--", linewidth=2, label="Threshold"
        )
        ax.set_xlabel("QBER")
        ax.set_ylabel("Frequency")
        ax.set_title("Error Rate Distribution")
        ax.legend()

        return fig

    @staticmethod
    def plot_feature_space(df):
        fig, ax = plt.subplots(figsize=(6, 4))

        no_eve_df = df[df["Eve Present"] == "No"]
        eve_df = df[df["Eve Present"] == "Yes"]

        ax.scatter(
            no_eve_df["QBER"],
            no_eve_df["Sift Ratio"],
            alpha=0.6,
            label="No Eve",
            color="green",
            s=50,
        )
        ax.scatter(
            eve_df["QBER"],
            eve_df["Sift Ratio"],
            alpha=0.6,
            label="Eve",
            color="red",
            s=50,
        )
        ax.set_xlabel("QBER")
        ax.set_ylabel("Sift Ratio")
        ax.set_title("2D Feature Space")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    @staticmethod
    def plot_ml_confidence(results_df):
        fig, ax = plt.subplots(figsize=(10, 4))

        scenarios = results_df["Scenario"].tolist()
        confidences = results_df["ML Confidence"].tolist()
        colors = ["green" if c < 0.5 else "red" for c in confidences]

        ax.barh(scenarios, confidences, color=colors, alpha=0.7)
        ax.axvline(
            0.5, color="black", linestyle="--", linewidth=2, label="Decision Threshold"
        )
        ax.set_xlabel("ML Confidence (Probability of Eve)")
        ax.set_title("Eavesdropping Detection Confidence")
        ax.legend()
        ax.grid(axis="x", alpha=0.3)

        return fig
