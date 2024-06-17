import openai
import streamlit as st
import VectorSearch
from text_process import process_query

# from dotenv import load_dotenv
# load_dotenv()

TOGETHER_API_KEY = "22c9252460f6056c47ca857f02593e552a2da989b625c29da8bc54022a404af6"

client = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)


def get_code_completion(messages, max_tokens=512, model="meta-llama/Llama-3-70b-chat-hf", retries=5, delay=2):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        stop=["<step>"],
        frequency_penalty=1,
        presence_penalty=1,
        top_p=0.7,
        n=1,
        temperature=0.7,
    )
    return chat_completion
# except openai.error.OpenAIError as e:
#     if attempt < retries - 1:
#         time.sleep(delay)
#         delay *= 2  # Exponential backoff
#     else:
#         raise e


# Streamlit app title
st.title("Phone Sales Assistant Chatbot")

# Initialize vector search object
vector_search = VectorSearch.VectorSearch()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."},
        {"role": "user", "content": "Hello, I'm looking for a phone with a great camera. Can you suggest a few models?"},
        {"role": "assistant", "content": "Hello! For great camera quality, I would recommend the following models: iPhone 14 Pro, Samsung Galaxy S23 Ultra, and Google Pixel 7 Pro. These phones all have high-quality cameras and advanced photography features. Do you have any other specific requirements, such as battery life or storage capacity?"}
    ]


# Accept user input
if prompt := st.chat_input("Can I help you with anything?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # vector search db
    combined_information = vector_search.get_search_result(
        process_query(prompt))
    st.session_state.messages.append(
        {"role": "user", "content": combined_information})

    # Generate assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            chat_completion = get_code_completion(st.session_state.messages)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
