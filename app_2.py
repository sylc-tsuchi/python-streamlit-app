# 6.6 会話履歴を表示する
# streamlit-langchain-app プログラム 6章
# 6.3 ブラウザにタイトル表示
import os

import streamlit as st
st.title("langchain-streamlit-app")

if "messages" not in st.session_state:  # st.session_stateにmessagesが無い場合
    st.session_state.messages = []      # 空のリストで初期化
    response = ""                       # 初期化処理を追加

for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # ロールごとに
        st.markdown(message["content"])     # 会話履歴(保存されているテキスト)を表示

# 6.4 ブラウザからユーザ入力値を取得してterminalに取得値を表示
prompt = st.chat_input("What is up?")
#print(prompt)

# 6.5 入力内容と応答をブラウザに表示
if prompt:  # 入力された文字列がある
    # ユーザの入力内容を会話履歴(st.session_state.messages)に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):       # ユーザのアイコンで
        st.markdown(prompt)             # promptをマークダウンとして表示

    with st.chat_message("assistant"):  # AIのアイコンで
        response = "こんにちは"          # 固定の応答文の
        st.markdown(response)           # 応答をマークダウンとして表示

    # 応答を会話履歴(st.session_state.messages)に追加
    st.session_state.messages.append({"role": "assistant", "content": response})