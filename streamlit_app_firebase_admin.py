import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os

st.set_page_config(page_title="🎮 2-Period Dynamic Game", layout="centered")
st.title("🎲 Multiplayer 2-Period Dynamic Game")

# Firebase initialization
cred_path = "dynamic-game-79aa7-firebase-adminsdk-fbsvc-ad7b67faad.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://dynamic-game-79aa7-default-rtdb.firebaseio.com/'
        })
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")
        st.stop()

# Player registration
name = st.text_input("Enter your name to join the game:")
if name:
    st.success(f"👋 Welcome, {name}!")
    player_ref = db.reference(f"players/{name}")
    player_ref.set({"joined": True})

    # Game description
    with st.expander("📜 Game Description"):
        st.markdown("""
        - The game has **two players** and **two periods**.
        - In each period, Player 1 chooses between **A** or **B**.
        - Player 2 chooses between **X**, **Y**, or **Z**.
        - Payoffs depend on the combination chosen, and are **known to both players**.
        - Period 2 decisions can depend on Period 1 results.
        """)

    # Match players in pairs (simple logic: alphabetical)
    players = db.reference("players").get()
    sorted_players = sorted(players.keys()) if players else []

    if name in sorted_players:
        idx = sorted_players.index(name)
        pair_idx = idx + 1 if idx % 2 == 0 else idx - 1
        if 0 <= pair_idx < len(sorted_players):
            partner_name = sorted_players[pair_idx]
            is_p1 = idx % 2 == 0
            role = "Player 1" if is_p1 else "Player 2"
            st.info(f"You are **{role}**, paired with **{partner_name}**.")

            # Period 1
            st.subheader("🕹 Period 1")
            choice1 = st.radio("Choose your action:", ["A", "B"] if is_p1 else ["X", "Y", "Z"], key="period1")
            if st.button("Submit Period 1 Move"):
                db.reference(f"moves/period1/{name}").set(choice1)
                st.success(f"✅ {role} move submitted: {choice1}")

            # Fetch and show result
            all_moves = db.reference("moves/period1").get()
            if all_moves and name in all_moves and partner_name in all_moves:
                p1_move = all_moves[name] if is_p1 else all_moves[partner_name]
                p2_move = all_moves[partner_name] if is_p1 else all_moves[name]
                matrix = {
                    ("A", "X"): (4, 3),
                    ("A", "Y"): (0, 0),
                    ("A", "Z"): (1, 4),
                    ("B", "X"): (0, 0),
                    ("B", "Y"): (2, 1),
                    ("B", "Z"): (0, 0),
                }
                payoff = matrix.get((p1_move, p2_move), (0, 0))
                st.success(f"🎯 Period 1 Outcome: P1 = {p1_move}, P2 = {p2_move} → Payoffs = {payoff}")

                # Period 2
                st.subheader("🕹 Period 2")
                choice2 = st.radio("Choose your action for Period 2:", ["A", "B"] if is_p1 else ["X", "Y", "Z"], key="period2")
                if st.button("Submit Period 2 Move"):
                    db.reference(f"moves/period2/{name}").set(choice2)
                    st.success(f"✅ Period 2 move submitted: {choice2}")

                all_moves2 = db.reference("moves/period2").get()
                if all_moves2 and name in all_moves2 and partner_name in all_moves2:
                    p1_2 = all_moves2[name] if is_p1 else all_moves2[partner_name]
                    p2_2 = all_moves2[partner_name] if is_p1 else all_moves2[name]
                    payoff2 = matrix.get((p1_2, p2_2), (0, 0))
                    st.success(f"🎯 Period 2 Outcome: P1 = {p1_2}, P2 = {p2_2} → Payoffs = {payoff2}")
        else:
            st.warning("Waiting for another student to join so we can pair you.")
    else:
        st.warning("Player not matched yet.")