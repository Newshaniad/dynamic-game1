import streamlit as st
import pyrebase
import time

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyCumR68sCbY032ecgg-yhKPDgC15Q22G9E",
    "authDomain": "dynamic-game-79aa7.firebaseapp.com",
    "databaseURL": "https://dynamic-game-79aa7-default-rtdb.firebaseio.com",
    "projectId": "dynamic-game-79aa7",
    "storageBucket": "dynamic-game-79aa7.firebasestorage.app",
    "messagingSenderId": "774660982535",
    "appId": "1:774660982535:web:be6e8d2b041bfaccd727a2",
    "measurementId": "G-10Q5XB1G36"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

st.set_page_config(page_title="Dynamic Game Multiplayer", layout="centered")
st.title("🎮 2-Period Dynamic Game")

# Player login
name = st.text_input("Enter your name to join the game:")
if name:
    db.child("players").child(name).set({"joined": True})
    st.success(f"Welcome {name}! Waiting for matching...")

    all_players = db.child("players").get().val()
    if all_players and len(all_players) >= 2:
        names = list(all_players.keys())
        names.sort()  # ensure deterministic assignment
        p1, p2 = names[0], names[1]
        if name == p1:
            role = "Player 1"
            choice_key = "P1"
            my_options = ["A", "B"]
        elif name == p2:
            role = "Player 2"
            choice_key = "P2"
            my_options = ["X", "Y", "Z"]
        else:
            role = None

        if role:
            st.info(f"You are {role}. Your opponent is {p2 if name == p1 else p1}.")

            # Period 1
            st.subheader("🔁 Period 1")
            move1 = st.radio(f"{role}, choose your action:", my_options, key=f"p1_{name}")
            if st.button("Submit Period 1 Move"):
                db.child("period1").child(choice_key).set(move1)
                st.success(f"Move submitted: {move1}")

            period1_moves = db.child("period1").get().val()
            if period1_moves and "P1" in period1_moves and "P2" in period1_moves:
                matrix = {
                    ("A", "X"): (4, 3),
                    ("A", "Y"): (0, 0),
                    ("A", "Z"): (1, 4),
                    ("B", "X"): (0, 0),
                    ("B", "Y"): (2, 1),
                    ("B", "Z"): (0, 0),
                }
                outcome1 = matrix.get((period1_moves["P1"], period1_moves["P2"]), (0, 0))
                st.info(f"🎯 Period 1: P1 = {period1_moves['P1']}, P2 = {period1_moves['P2']} → Payoffs = {outcome1}")

                # Period 2
                st.subheader("🔁 Period 2")
                move2 = st.radio(f"{role}, choose your action:", my_options, key=f"p2_{name}")
                if st.button("Submit Period 2 Move"):
                    db.child("period2").child(choice_key).set(move2)
                    st.success(f"Move submitted: {move2}")

                period2_moves = db.child("period2").get().val()
                if period2_moves and "P1" in period2_moves and "P2" in period2_moves:
                    outcome2 = matrix.get((period2_moves["P1"], period2_moves["P2"]), (0, 0))
                    st.info(f"🎯 Period 2: P1 = {period2_moves['P1']}, P2 = {period2_moves['P2']} → Payoffs = {outcome2}")
    else:
        st.warning("Waiting for another player to join...")