import streamlit as st
import pyrebase
import uuid
import time

# Firebase config with Realtime Database secret
firebaseConfig = {
    "apiKey": "AIzaSyCumR68sCbY032ecgg-yhKPDgC15Q22G9E",
    "authDomain": "dynamic-game-79aa7.firebaseapp.com",
    "databaseURL": "https://dynamic-game-79aa7-default-rtdb.firebaseio.com/",
    "projectId": "dynamic-game-79aa7",
    "storageBucket": "dynamic-game-79aa7.appspot.com",
    "messagingSenderId": "774660982535",
    "appId": "1:774660982535:web:be6e8d2b041bfaccd727a2",
    "databaseSecret": "0jzX8xvTaFHjTD9ohG8ovnMiMYMfL2MIqMik8Meq"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# App UI
st.title("🎲 Multiplayer 2-Period Dynamic Game")
st.markdown("Please enter your full name to join the game. You’ll be matched as Player 1 or Player 2 automatically.")

# Player login
name = st.text_input("Enter your full name:")

if st.button("Join Game"):
    if not name:
        st.warning("❗ Please enter your name.")
        st.stop()

    # Check current players
    players = db.child("players").get().val()
    if players is None:
        players = {}

    # Assign player role
    if len(players) == 0:
        player_role = "Player 1"
    elif len(players) == 1:
        player_role = "Player 2"
    else:
        st.error("❌ Two players already joined. Please wait for the next game.")
        st.stop()

    # Generate a unique ID
    player_id = str(uuid.uuid4())
    db.child("players").child(player_id).set({"name": name, "role": player_role, "choice": None})

    st.success(f"✅ Welcome {name}, you are **{player_role}**!")

    # Wait for second player
    while True:
        players = db.child("players").get().val()
        if players and len(players) == 2:
            break
        with st.spinner("⏳ Waiting for another player to join..."):
            time.sleep(1)

    # Show game matrix
    st.markdown("### 🎯 Payoff Matrix")
    st.table({
        "": {"X": "(4,3)", "Y": "(0,0)", "Z": "(1,4)"},
        "A": {"X": "(4,3)", "Y": "(0,0)", "Z": "(1,4)"},
        "B": {"X": "(0,0)", "Y": "(2,1)", "Z": "(0,0)"}
    })

    # Game choices
    if player_role == "Player 1":
        choice = st.radio("Choose A or B:", ["A", "B"])
    else:
        choice = st.radio("Choose X, Y, or Z:", ["X", "Y", "Z"])

    if st.button("Submit Move"):
        db.child("players").child(player_id).update({"choice": choice})
        st.success("✅ Move submitted. Waiting for your partner...")

        # Wait for other player
        while True:
            players = db.child("players").get().val()
            choices = [v["choice"] for v in players.values()]
            if all(c is not None for c in choices):
                break
            time.sleep(1)

        # Show results
        other = [v for k, v in players.items() if k != player_id][0]
        your_move = choice
        their_move = other["choice"]
        your_role = player_role
        their_role = other["role"]

        st.markdown("### 🎉 Results")
        st.markdown(f"🧑‍🤝‍🧑 You were **{your_role}**, chose **{your_move}**")
        st.markdown(f"👤 {other['name']} was **{their_role}**, chose **{their_move}**")

        st.balloons()

        # Cleanup after game
        db.child("players").remove()
