import streamlit as st
from text_process import process_query
import model
import VectorSearch

st.title("Phone SalesAssistant Chatbot")
vector_search = VectorSearch.VectorSearch()

# Initialize chat history
if "messages" not in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."},
            {"role": "user", "content": "Hello, I'm looking for a phone with a great camera. Can you suggest a few models?"},
            {"role": "assistant", "content": "Hello! For great camera quality, I would recommend the following models: iPhone 14 Pro, Samsung Galaxy S23 Ultra, and Google Pixel 7 Pro. These phones all have high-quality cameras and advanced photography features. Do you have any other specific requirements, such as battery life or storage capacity?"}
        ]

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What phone do you need?"):

    # Display user message in chat message container

    combined_information = vector_search.get_search_result(
        process_query(prompt))

    st.session_state.messages.append(
        {"role": "user", "content": combined_information})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            print('Start generating response')
            response = model.generate_text(st.session_state.messages)
            print(response)
            st.write(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
