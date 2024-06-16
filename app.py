# chatbot_interface.py
import streamlit as st
import requests

# Streamlit app layout
st.title("Chatbot Interface")
st.write("Type your query below and hit 'Send' to get a response from the chatbot.")

# User input
query = st.text_input("Your Query", "")

# Define the Flask API endpoint
api_url = "http://127.0.0.1:5000/api/chatbot"

if st.button("Send"):
    if query:
        # Send the query to the Flask API
        response = requests.post(api_url, json={'content': query})

        # Handle the response from the Flask API
        if response.status_code == 200:
            response_data = response.json()
            st.write("Chatbot Response:")
            st.write(response_data.get('content', ''))
        else:
            st.write("Error:", response.status_code)
            st.write(response.json().get('error', 'Unknown error'))
    else:
        st.write("Please enter a query to send to the chatbot.")
