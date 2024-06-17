import streamlit as st
from text_process import process_query
import model
import VectorSearch
import torch

# Ensure CUDA memory is cleared
torch.cuda.empty_cache()

# Streamlit app title
st.title("Phone Sales Assistant Chatbot")

# Initialize vector search object
vector_search = VectorSearch.VectorSearch()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."}
        # {"role": "user", "content": "Hello, I'm looking for a phone with a great camera. Can you suggest a few models?"},
        # {"role": "assistant", "content": "Hello! For great camera quality, I would recommend the following models: iPhone 14 Pro, Samsung Galaxy S23 Ultra, and Google Pixel 7 Pro. These phones all have high-quality cameras and advanced photography features. Do you have any other specific requirements, such as battery life or storage capacity?"}
    ]

# Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What phone do you need?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process user prompt and get search result
    combined_information = vector_search.get_search_result(process_query(prompt))
    st.session_state.messages.append({"role": "user", "content": combined_information})

    # Generate assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = model.generate_text(st.session_state.messages)
            print(response)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
