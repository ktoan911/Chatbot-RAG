import together_api
import streamlit as st
import VectorSearch
from text_process import process_query


# Streamlit app title
st.set_page_config(page_title="Phone Chatbot", page_icon=":robot:")
st.title("Phone Sales Assistant Chatbot")

# Khởi tạo vector search
vector_search = VectorSearch.VectorSearch()
llm = together_api.TogetherLLM()


# Tạo bộ nhớ seesion statecho lịch sử chat và query
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."}
    ]
# Initialize raw querry in session state
if 'query_list' not in st.session_state:
    st.session_state.query_list = []


# In lịch sử chat
if (st.session_state.messages[-1]['role'] == 'assistant'):
    cnt = 0
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message(message["role"]):
                st.write(st.session_state.query_list[cnt])
                cnt += 1
        
        elif message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])


# Khi đầu vào từ người dùng
if prompt := st.chat_input("Can I help you with anything?"):
    # Hiển thị query
    with st.chat_message("user"):
        st.session_state.query_list.append(prompt)
        st.markdown(prompt)

    # vector search db
    clean_query, get_infor = process_query(prompt)
    if (get_infor):
        clean_query = vector_search.get_search_result(clean_query)
    st.session_state.messages.append(
        {"role": "user", "content": clean_query})

    # Generate assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Checking the warehouse..."):
            response = llm.call(st.session_state.messages)
            st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
