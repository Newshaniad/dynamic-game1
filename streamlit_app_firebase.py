import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate("your_admin_sdk_file.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://dynamic-game-79aa7-default-rtdb.firebaseio.com/'
    })

# Game UI
st.title("🎮 2-Period Dynamic Game")

name = st.text_input("Enter your full name:")
if name:
    st.success(f"Hello, {name}! You're in the game.")
    
    choice1 = st.radio("Choose for Period 1", ['A', 'B'])
    choice2 = st.radio("Choose for Period 2", ['A', 'B'])

    if st.button("Submit Choices"):
        db.reference(f'players/{name}').set({
            'period1': choice1,
            'period2': choice2
        })
        st.success("Choices submitted!")

        # Show data
        data = db.reference('players').get()
        st.write("📊 All Players So Far:")
        st.json(data)
