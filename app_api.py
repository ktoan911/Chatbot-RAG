import os
from litellm import completion
import streamlit as st
import VectorSearch
from text_process import process_query


os.environ["TOGETHER_API_KEY"] = "22c9252460f6056c47ca857f02593e552a2da989b625c29da8bc54022a404af6"


class TogetherLLM:
    def __init__(self,
                 model: str = "together_ai/meta-llama/Llama-3-70b-chat-hf",
                 together_api_key: str = os.environ["TOGETHER_API_KEY"],
                 temperature: float = 0.7,
                 max_tokens: int = 512):
        self.model = model
        self.together_api_key = together_api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(
        self,
        messages: list,
    ):
        """Call to Together endpoint."""

        output = completion(
            messages=messages,
            model=self.model,
            together_api_key=self.together_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        text = output['choices'][0]['message']['content']
        return text


# Streamlit app title
st.title("Phone Sales Assistant Chatbot")

# Initialize vector search object
vector_search = VectorSearch.VectorSearch()
llm = TogetherLLM()


# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."}
    ]

if (st.session_state.messages[-1]['role'] == 'assistant'):
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])


# Accept user input
if prompt := st.chat_input("Can I help you with anything?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # vector search db
    clean_query, get_infor = process_query(prompt)
    if (get_infor):
        clean_query = vector_search.get_search_result(clean_query)
    st.session_state.messages.append(
        {"role": "user", "content": clean_query})

    # Generate assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = llm.call(st.session_state.messages)
            st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
