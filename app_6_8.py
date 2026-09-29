# streamlit-langchain-app プログラム 6.8章
# Agentを使って外部情報を検索させる
#  注)今日の天気を聞くと2025年10月25日の天気を回答する。
# DuckDuckGoを検索で正解の「今日」が検索されるが、LLMが検索結果を解釈すると
# 「今日」が認識できないため、GPTの情報である2025年10月25日に置き換えられてしまう誤動作が起きる
# 今日の日付をLLMに事前に通知するようにプログラムを行う
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent, load_tools
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks import StreamlitCallbackHandler
import wikipedia
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

def create_agent_chain():
    chat = ChatOpenAI(
        model_name=os.environ["OPENAI_API_MODEL"],
        temperature=os.environ["OPENAI_API_TEMPERATURE"],
        streaming=True
    )

    # 現在の日本時間を取得
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    current_datetime = now.strftime("%Y年%m月%d日 %H:%M")

    #
    wikipedia.set_lang("ja")
    wikipedia.set_user_agent("MyStreamlitApp/1.0 (contact@example.com)")

    # wikipedia アクセスのため、wikipedia toolを明示的に作成する
    tools = load_tools(["ddg-search", "wikipedia"])

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
    あなたは有能なAIアシスタントです。
    現在の日本日時は {current_datetime} です。
    必要に応じてツールを使用してください。
    回答は日本語で行ってください。
        """
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(chat, tools, prompt)
    agent_chain = AgentExecutor(agent=agent, tools=tools, max_iterations=5, verbose=True)
    
    return agent_chain


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
        callback = StreamlitCallbackHandler(st.container())
        agent_chain = create_agent_chain()
        response = agent_chain.invoke(
            {"input": prompt},
            {"callbacks": [callback]}
        )
        #st.markdown(response)           # 応答をマークダウンとして表示
        st.markdown(response["output"])





