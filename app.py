import together_api
import streamlit as st
import VectorSearch
from query_process import process_query, classification_query


# Streamlit app title
st.set_page_config(page_title="Phone Chatbot", page_icon=":iphone:")
st.title("Phone Sales Assistant Chatbot")

# Khởi tạo vector search
vector_search = VectorSearch.VectorSearch()
llm = together_api.TogetherLLM()


# Tạo bộ nhớ seesion statecho lịch sử chat và query
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a phone sales representative in Hedspi mobile phone store. Your task is to help customers find the best phone that suits their needs."}
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
                # st.write(message["content"])
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
    need_db = classification_query(prompt, llm)
    clean_query, get_infor = process_query(prompt)
    if get_infor and need_db:
        clean_query = vector_search.get_search_result(clean_query)
    st.session_state.messages.append(
        {"role": "user", "content": clean_query})

    # Generate assistant's response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        stream = llm.call(st.session_state.messages)
        response = ""
        for part in stream:
            ans_next = part.choices[0].delta.content
            if ans_next != None:
                response += ans_next
                placeholder.write(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})