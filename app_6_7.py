# streamlit-langchain-app プログラム 6.7章
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

# 確認
#print("model_name  : ", os.environ["OPENAI_API_MODEL"])
#print("temperature : ", os.environ["OPENAI_API_TEMPERATURE"])

st.title("langchain-streamlit-app")

if "messages" not in st.session_state:  # st.session_stateにmessagesが無い場合
    st.session_state.messages = []      # 空のリストで初期化
    response = ""                       # 初期化処理を追加

for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # ロールごとに
        st.markdown(message["content"])     # 会話履歴(保存されているテキスト)を表示
        
prompt = st.chat_input("What is up?")

# 6.5 入力内容と応答をブラウザに表示
if prompt:  # 入力された文字列がある
    # ユーザの入力内容を会話履歴(st.session_state.messages)に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):       # ユーザのアイコンで
        st.markdown(prompt)             # promptをマークダウンとして表示
        
    with st.chat_message("assistant"):  # AIのアイコンで
        chat = ChatOpenAI(
            model_name=os.environ["OPENAI_API_MODEL"],
            temperature=os.environ["OPENAI_API_TEMPERATURE"],
            streaming=True
        )
        messages = [HumanMessage(content=prompt)]
        response = chat.invoke(messages).content
        st.markdown(response)           # 応答をマークダウンとして表示