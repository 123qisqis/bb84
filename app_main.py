import streamlit as st
import time
import numpy as np

from bb84_protocol import BB84Protocol, EveConfig
from ml import MLDetector
from visualizer import BB84Visualizer
from game import BB84Game
from analyzer import BB84Analyzer


# Page
st.set_page_config(
    page_title="BB84 QKD Implementation",
    layout="wide",
    page_icon="Q",
    initial_sidebar_state="expanded",
)

if "game_state" not in st.session_state:
    st.session_state.game_state = None
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "ml_detector" not in st.session_state:
    st.session_state.ml_detector = None

st.title("BB84 Quantum Key Distribution")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    mode = st.radio(
        "Choose Mode:",
        ["Live Animation", "Interactive Game", "ML Detection", "Tutorial", "Analysis"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### About")
    st.info(
        """
    **BB84 QKD Protocol**
    - Watch live protocol animation
    - Play as Eve (eavesdropper)
    - ML-based detection
    - Statistical analysis
    """
    )


# LIVE simulation of bb84
if mode == "Live Animation":
    st.header("Live BB84 Protocol Animation")

    st.markdown("Watch the BB84 protocol in action with quantum circuits.")

    # Settings
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Protocol Settings")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            n_qubits_anim = st.slider(
                "Number of Qubits", 20, 100, 50, 10, key="anim_qubits"
            )
        with col_b:
            noise_anim = st.slider(
                "Channel Noise", 0.0, 0.1, 0.02, 0.01, key="anim_noise"
            )
        with col_c:
            animation_speed = st.slider(
                "Animation Speed (s)", 0.02, 0.2, 0.05, 0.01, key="anim_speed"
            )

    st.subheader("Eve Settings")
    col_eve1, col_eve2 = st.columns(2)

    with col_eve1:
        eve_enabled_anim = st.checkbox(
            "Enable Eve (Eavesdropper)", value=False, key="anim_eve"
        )
    with col_eve2:
        eve_intercept_anim = (
            st.slider("Eve Intercept Rate", 0.0, 1.0, 0.5, 0.1, key="anim_eve_rate")
            if eve_enabled_anim
            else 0.0
        )

    st.markdown("---")

    # Run button
    if st.button(
        "Run BB84 Protocol", type="primary", use_container_width=True, key="run_anim"
    ):
        bb84_anim = BB84Protocol(n_qubits_anim)

        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        st.markdown("### Quantum Channel")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("#### Alice")
            alice_container = st.container()
        with col_b:
            st.markdown("#### Eve" if eve_enabled_anim else "#### Channel")
            eve_container = st.container()
        with col_c:
            st.markdown("#### Bob")
            bob_container = st.container()

        st.markdown("---")
        st.markdown("### Real-time Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

        kept_count = 0
        error_count = 0

        # Animate rounds
        for i in range(min(50, n_qubits_anim)):
            progress = (i + 1) / min(50, n_qubits_anim)
            progress_bar.progress(progress)
            status_placeholder.info(f"Sending qubit {i+1}/{min(50, n_qubits_anim)}...")

            eve_intercepts_now = eve_enabled_anim and (
                np.random.rand() < eve_intercept_anim
            )
            eve_basis_now = np.random.choice(["Z", "X"]) if eve_intercepts_now else None

            alice_bit, alice_basis, bob_bit, bob_basis = bb84_anim.send_qubit(
                eve_intercepts=eve_intercepts_now, eve_basis=eve_basis_now
            )

            with alice_container:
                st.markdown(f"**Round {i+1}**")
                st.markdown(f"Basis: `{alice_basis}`")
                st.markdown(f"Bit: `{alice_bit}`")

            with eve_container:
                if eve_intercepts_now:
                    st.markdown("**INTERCEPTED**")
                    st.markdown(f"Measured: `{eve_basis_now}`")
                else:
                    st.markdown("Passed through")

            with bob_container:
                st.markdown(f"**Round {i+1}**")
                st.markdown(f"Basis: `{bob_basis}`")
                st.markdown(f"Measured: `{bob_bit}`")

            bases_match = alice_basis == bob_basis
            bits_match = alice_bit == bob_bit

            if bases_match:
                kept_count += 1
                if not bits_match:
                    error_count += 1

            with stats_col1:
                st.metric("Qubits Sent", i + 1)
            with stats_col2:
                st.metric("Sifted Key", kept_count)
            with stats_col3:
                st.metric("Errors", error_count)
            with stats_col4:
                qber = error_count / kept_count if kept_count > 0 else 0
                st.metric("QBER", f"{qber:.3f}")

            time.sleep(animation_speed)

        # Complete remaining qubits
        if n_qubits_anim > 50:
            status_placeholder.info(
                f"Fast-forwarding remaining {n_qubits_anim - 50} qubits..."
            )
            for _ in range(50, n_qubits_anim):
                eve_intercepts_now = eve_enabled_anim and (
                    np.random.rand() < eve_intercept_anim
                )
                eve_basis_now = (
                    np.random.choice(["Z", "X"]) if eve_intercepts_now else None
                )
                bb84_anim.send_qubit(
                    eve_intercepts=eve_intercepts_now, eve_basis=eve_basis_now
                )

        progress_bar.empty()
        status_placeholder.empty()

        final_qber, final_key_len = bb84_anim.calculate_qber()

        st.success("Protocol Complete")
        st.markdown("### Final Statistics")

        final_col1, final_col2, final_col3 = st.columns(3)
        with final_col1:
            st.metric("Total Qubits", n_qubits_anim)
            st.metric("Final Key Length", final_key_len)
        with final_col2:
            st.metric("Sift Ratio", f"{final_key_len/n_qubits_anim:.2%}")
            st.metric("QBER", f"{final_qber:.3f}")
        with final_col3:
            threshold = 0.11
            if final_qber > threshold:
                st.error("High error rate detected - Possible eavesdropping")
            else:
                st.success("Error rate acceptable - Channel appears secure")

        st.markdown("### QBER Analysis")
        fig_gauge = BB84Visualizer.plot_qber_gauge(final_qber, threshold, "Final QBER")
        st.pyplot(fig_gauge)


# INTERACTIVE GAME
elif mode == "Interactive Game":
    st.header("Interactive Game: Play as Eve")

    if not st.session_state.game_active:
        st.markdown(
            """
        **Your Mission:** Intercept qubits without being detected.
        - Choose which qubits to measure
        - Select measurement basis (Z or X)
        - Keep QBER below threshold to win
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Game Settings")
            difficulty = st.selectbox(
                "Difficulty",
                [
                    "Easy (15% threshold)",
                    "Medium (12% threshold)",
                    "Hard (10% threshold)",
                ],
            )
            n_qubits = st.slider("Number of Qubits", 10, 30, 20)

        with col2:
            st.subheader("Difficulty Info")
            if "Easy" in difficulty:
                threshold = 0.15
                st.success("More tolerance for errors")
            elif "Hard" in difficulty:
                threshold = 0.10
                st.error("Very low error tolerance")
            else:
                threshold = 0.12
                st.warning("Moderate difficulty")

            st.metric("QBER Threshold", f"{threshold:.0%}")
            st.metric("Qubits to Send", n_qubits)

        if st.button("Start Game", type="primary", use_container_width=True):
            st.session_state.game_state = BB84Game(n_qubits, threshold)
            st.session_state.game_active = True
            st.rerun()

    else:
        game = st.session_state.game_state

        if not game.is_game_over():
            stats = game.get_current_stats()

            st.subheader(f"Round {stats['current_round'] + 1} / {game.n_qubits}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Intercepted", stats["intercepted"])
            with col2:
                st.metric("Score", stats["intercepted"] * 10)
            with col3:
                if stats["current_round"] > 0 and stats["key_len"] > 0:
                    color_indicator = (
                        "Red" if stats["qber"] > game.threshold else "Green"
                    )
                    st.metric("Current QBER", f"{stats['qber']:.2%}")
                    st.caption(color_indicator)
                else:
                    st.metric("Current QBER", "Pending")
            with col4:
                st.metric("Progress", f"{stats['progress']:.0%}")

            if stats["current_round"] > 0 and len(game.qber_history) > 0:
                st.markdown("### Real-time QBER Tracking")
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    fig = BB84Visualizer.plot_qber_evolution(
                        game.qber_history, game.threshold
                    )
                    st.pyplot(fig)

                with col_right:
                    fig_gauge = BB84Visualizer.plot_qber_gauge(
                        game.qber_history[-1], game.threshold
                    )
                    st.pyplot(fig_gauge)

            st.markdown("---")

            if stats["current_round"] > 0:
                with st.expander(
                    f"Transmission History ({stats['current_round']} rounds completed)",
                    expanded=False,
                ):
                    history = game.get_transmission_history()
                    for h in history:
                        st.markdown(
                            f"**Round {h['round']}:** Alice ({h['alice_basis']}, {h['alice_bit']}) -> Bob ({h['bob_basis']}, {h['bob_bit']}) | {h['status']} | {h['result']}"
                        )

            st.markdown("---")
            st.markdown("### Qubit Incoming")

            col_choice1, col_choice2 = st.columns(2)

            with col_choice1:
                if st.button("INTERCEPT", use_container_width=True, type="primary"):
                    st.session_state.awaiting_basis = True
                    st.rerun()

            with col_choice2:
                if st.button("LET PASS", use_container_width=True):
                    result = game.let_pass_qubit()
                    st.markdown(f"#### Round {stats['current_round'] + 1} - LET PASS")
                    st.markdown(
                        f"Alice ({result['alice_basis']}, {result['alice_bit']}) -> Bob ({result['bob_basis']}, {result['bob_bit']})"
                    )
                    st.rerun()

            if st.session_state.get("awaiting_basis", False):
                st.markdown("### Choose Measurement Basis")
                col_z, col_x = st.columns(2)

                with col_z:
                    if st.button("Z Basis", use_container_width=True):
                        result = game.intercept_qubit("Z")
                        st.markdown(
                            f"#### Round {stats['current_round'] + 1} - INTERCEPTED (Z Basis)"
                        )
                        st.markdown(
                            f"Alice ({result['alice_basis']}, {result['alice_bit']}) -> Eve (Z) -> Bob ({result['bob_basis']}, {result['bob_bit']})"
                        )
                        st.session_state.awaiting_basis = False
                        st.rerun()

                with col_x:
                    if st.button("X Basis", use_container_width=True):
                        result = game.intercept_qubit("X")
                        st.markdown(
                            f"#### Round {stats['current_round'] + 1} - INTERCEPTED (X Basis)"
                        )
                        st.markdown(
                            f"Alice ({result['alice_basis']}, {result['alice_bit']}) -> Eve (X) -> Bob ({result['bob_basis']}, {result['bob_bit']})"
                        )
                        st.session_state.awaiting_basis = False
                        st.rerun()

        else:
            results = game.get_final_results()

            st.markdown("## GAME OVER")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Qubits Sent", game.n_qubits)
                st.metric("Intercepted", results["intercepted"])
            with col2:
                st.metric("Final Key Length", results["final_key_len"])
                st.metric("Sift Ratio", f"{results['final_key_len']/game.n_qubits:.1%}")
            with col3:
                color_text = "Red" if results["detected"] else "Green"
                st.metric("Final QBER", f"{results['final_qber']:.2%}")
                st.caption(f"{color_text} - Threshold: {results['threshold']:.0%}")

            st.markdown("---")

            if results["detected"]:
                st.error(f"### DETECTED - Alice and Bob abort the protocol")
                st.markdown(
                    f"**YOU LOSE** - QBER ({results['final_qber']:.2%}) exceeded threshold ({results['threshold']:.0%})"
                )
            else:
                st.success(f"### UNDETECTED - Alice and Bob proceed with the key")
                if results["intercepted"] > 0:
                    st.markdown(
                        f"**YOU WIN** - Intercepted {results['intercepted']} qubits without detection"
                    )
                else:
                    st.markdown("You didn't intercept anything")

            st.metric("Final Score", results["final_score"])

            if len(game.qber_history) > 0:
                st.markdown("### Game Statistics")
                fig = BB84Visualizer.plot_game_statistics(
                    game.qber_history, game.key_len_history, game.threshold
                )
                st.pyplot(fig)

            if st.button("Play Again", type="primary"):
                st.session_state.game_active = False
                st.session_state.game_state = None
                st.session_state.awaiting_basis = False
                st.rerun()


# ML DETECTION
elif mode == "ML Detection":
    st.header("Machine Learning Attack Detection")

    if st.button("Train & Test ML Detector", type="primary"):
        with st.spinner("Training ML model on 40 BB84 sessions..."):
            detector = MLDetector()
            detector.train(n_sessions=20, n_qubits=40)
            st.session_state.ml_detector = detector

        st.success("Model trained")

        st.markdown("### Testing Scenarios")

        scenarios = [
            ("No Eve", EveConfig(active=False)),
            ("Light Attack (30%)", EveConfig(active=True, intercept_rate=0.3)),
            ("Heavy Attack (80%)", EveConfig(active=True, intercept_rate=0.8)),
        ]

        results_df = detector.evaluate_scenarios(scenarios, n_qubits=40)
        st.dataframe(results_df, use_container_width=True, hide_index=True)

        st.markdown("### ML Confidence Levels")
        fig = BB84Visualizer.plot_ml_confidence(results_df)
        st.pyplot(fig)


# MODE 4: TUTORIAL
elif mode == "Tutorial":
    st.header("BB84 Protocol Tutorial")

    tab1, tab2, tab3 = st.tabs(["Protocol", "Eavesdropping", "Game Strategy"])

    with tab1:
        st.markdown(
            """
        ### BB84 Quantum Key Distribution
        
        **Step 1: Alice prepares qubits**
        - Randomly chooses bits (0 or 1)
        - Randomly chooses bases (Z or X)
        - Encodes qubits: |0>, |1> (Z basis) or |+>, |-> (X basis)
        
        **Step 2: Bob measures qubits**
        - Randomly chooses measurement bases
        - Measures received qubits
        
        **Step 3: Sifting**
        - Alice and Bob compare bases (public channel)
        - Keep only bits where bases matched
        - Approximately 50% of bits are kept
        
        **Step 4: Error checking**
        - Calculate QBER (Quantum Bit Error Rate)
        - If QBER > threshold -> Eavesdropper detected
        - If QBER <= threshold -> Proceed with key
        """
        )

        st.info(
            """
        **Why is it secure?**
        - Measuring a qubit changes its state
        - Eve cannot measure without introducing errors
        - No-cloning theorem: cannot copy quantum states
        """
        )

    with tab2:
        st.markdown(
            """
        ### How Eavesdropping Works
        
        **Eve's Intercept-Resend Attack:**
        
        1. **Intercept**: Eve measures the qubit
        2. **Problem**: Eve doesn't know Alice's basis
        3. **Guess**: Eve chooses a basis randomly (50% wrong)
        4. **Resend**: Eve prepares a new qubit in her basis
        5. **Result**: If wrong basis, Bob has 50% error chance
        
        **Detection:**
        - Normal channel noise: 1-2% QBER
        - Eve intercepts 100%: 25% QBER
        - Eve intercepts 50%: 12-13% QBER
        - Threshold: 11% QBER
        """
        )

    with tab3:
        st.markdown(
            """
        ### Strategy Guide
        
        **Difficulty Levels:**
        - **Easy (15%)**: Can intercept ~40% of qubits
        - **Medium (12%)**: Can intercept ~25% of qubits
        - **Hard (10%)**: Can intercept ~15% of qubits
        
        **Tips:**
        1. Be selective - don't intercept every qubit
        2. Watch QBER - real-time tracking shows risk
        3. Random is better - don't follow patterns
        4. Early game - more aggressive (no data yet)
        5. Late game - conservative (QBER accumulates)
        """
        )


# ANALYSIS
elif mode == "Analysis":
    st.header("Statistical Analysis")

    st.markdown(
        "Generate datasets to analyze BB84 performance under different conditions."
    )

    col1, col2 = st.columns(2)

    with col1:
        n_sessions = st.slider("Number of Sessions", 10, 100, 20)
        n_qubits_analysis = st.slider("Qubits per Session", 20, 100, 40)

    with col2:
        noise_level = st.slider("Channel Noise", 0.0, 0.1, 0.02, 0.01)
        eve_rate = st.slider("Eve Intercept Rate", 0.0, 1.0, 0.5, 0.1)

    if st.button("Generate Analysis", type="primary"):
        with st.spinner(f"Running {n_sessions} BB84 sessions..."):
            df = BB84Analyzer.generate_dataset(
                n_sessions, n_qubits_analysis, noise_level, eve_rate
            )

        st.success(f"Generated {len(df)} sessions")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### QBER Distribution")
            fig = BB84Visualizer.plot_qber_distribution(df)
            st.pyplot(fig)

        with col2:
            st.markdown("### Feature Space")
            fig = BB84Visualizer.plot_feature_space(df)
            st.pyplot(fig)

        st.markdown("### Summary Statistics")
        summary = BB84Analyzer.compute_summary_statistics(df)
        st.dataframe(summary, use_container_width=True)
