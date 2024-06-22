import together_api
import streamlit as st
import RAG
from query_process import classification_query, process_query
import os
from dotenv import load_dotenv

load_dotenv()


# Streamlit app title
st.set_page_config(page_title="Hedspi Phone Store", page_icon=":iphone:")
st.title("Hedspi Phone Store Chatbot")

# Khởi tạo vector search
vector_search = RAG.RAG()
llm = together_api.TogetherLLM()


# Tạo bộ nhớ seesion statecho lịch sử chat và query
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là một nhân viên bán hàng điện thoại trong cửa hàng điện thoại di động Hedspi. Nhiệm vụ của bạn là giúp khách hàng tìm chiếc điện thoại tốt nhất phù hợp với nhu cầu của họ."}
    ]

# Initialize raw querry in session state
if 'query_list' not in st.session_state:
    st.session_state.query_list = []


col1, col2 = st.columns([3, 7])  # chia tỉ lệ  2 cột 25% và 75%
with col1:
    if st.button("Làm mới cuộc trò chuyện"):
        st.session_state.messages = [
            {"role": "system", "content": "Bạn là một nhân viên bán hàng điện thoại trong cửa hàng điện thoại di động Hedspi. Nhiệm vụ của bạn là giúp khách hàng tìm chiếc điện thoại tốt nhất phù hợp với nhu cầu của họ."}
        ]

        st.session_state.query_list = []
        st.experimental_rerun()  # chạy lại chatbot

with col2:
    if st.button("Đến website bán hàng"):
        website_url = os.environ.get('WEBSITE', 'https://www.example.com')
        st.write(f'<a href={website_url} target="_blank">Bấm vào để quay lại cửa hàng</a>',
                 unsafe_allow_html=True)


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
if prompt := st.chat_input("Bạn cần chúng tôi hỗ trợ gì?"):
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
