from __future__ import annotations
import src.infrastructure.prompt as prompt
from dotenv import load_dotenv
from src.common.query_process import classification_query, process_query, extension_query
import src.infrastructure.RAG as RAG
import streamlit as st
import src.infrastructure.API_LLM as LLM

import os
import sys
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))


load_dotenv()


# Streamlit app title
st.set_page_config(page_title='Markat', page_icon='	:smiley_cat:')
st.title('Markat Assistant Chatbot')

# Khởi tạo vector search
vector_search = RAG.RAG()
llm = LLM.GroqLLM()


# Tạo bộ nhớ seesion statecho lịch sử chat và query
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {'role': 'system', 'content': prompt.model_instructions()},
    ]

# Initialize raw querry in session state
if 'query_list' not in st.session_state:
    st.session_state.query_list = []


col1, col2 = st.columns([3, 7])  # chia tỉ lệ  2 cột 25% và 75%
with col1:
    if st.button('Làm mới cuộc trò chuyện'):
        st.session_state.messages = [
            {'role': 'system', 'content': prompt.model_instructions()},
        ]

        st.session_state.query_list = []
        st.experimental_rerun()  # chạy lại chatbot

with col2:
    if st.button('Đến website bán hàng'):
        website_url = os.environ.get('WEBSITE', 'https://www.example.com')
        st.write(
            f'<a href={website_url} target="_blank">Bấm vào để quay lại cửa hàng</a>',
            unsafe_allow_html=True,
        )


# In lịch sử chat
if (st.session_state.messages[-1]['role'] == 'assistant'):
    cnt = 0
    for message in st.session_state.messages:
        if message['role'] == 'user':
            with st.chat_message(message['role']):
                st.write(st.session_state.query_list[cnt])
                # st.write(message["content"])
                cnt += 1

        elif message['role'] != 'system':
            with st.chat_message(message['role']):
                st.write(message['content'])


# Khi đầu vào từ người dùng
if prompt := st.chat_input('Bạn cần chúng tôi hỗ trợ gì?'):
    # Hiển thị query
    with st.chat_message('user'):
        st.session_state.query_list.append(prompt)
        st.markdown(prompt)

    # vector search db
    is_needRAG = classification_query([prompt])
    if is_needRAG:
        historyChat = st.session_state.messages + \
            [{'role': 'user', 'content': process_query(prompt)}]
        reflected_query = extension_query(llm, historyChat)
        clean_query = vector_search.get_search_result(reflected_query)
    else:
        clean_query = process_query(prompt)

    st.session_state.messages.append(
        {'role': 'user', 'content': clean_query},
    )

    # Generate assistant's response
    with st.chat_message('assistant'):
        placeholder = st.empty()
        stream = llm.call(st.session_state.messages, stream=True)
        response = ''
        for chunk in stream:
            ans_next = chunk.choices[0].delta.content or ''
            if ans_next is not None:
                response += ans_next
                placeholder.write(response)
    st.session_state.messages.append(
        {'role': 'assistant', 'content': response},
    )
