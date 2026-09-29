# streamlit-langchain-app プログラム 6.9章
# Agentを使って外部情報を検索させる
#  注)今日の天気を聞くと2025年10月25日の天気を回答する。
# DuckDuckGoを検索で正解の「今日」が検索されるが、LLMが検索結果を解釈すると
# 「今日」が認識できないため、GPTの情報である2025年10月25日に置き換えられてしまう誤動作が起きる
# 今日の日付をLLMに事前に通知するようにプログラムを行う
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent, load_tools
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#from langchain_classic.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
import wikipedia
from datetime import datetime
from zoneinfo import ZoneInfo
# wikipedia アクセスのため、wikipedia toolを明示的に作成する
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

load_dotenv()

def create_agent_chain():
    chat = ChatOpenAI(
        model_name=os.environ["OPENAI_API_MODEL"],
        temperature=os.environ["OPENAI_API_TEMPERATURE"],
        streaming=True
    )

    # OpenAI Function Agent のプロンプトにMemory の会話履歴を追加設定
    #agent_kwargs = {
    #    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    #}
    # OpenAI Function Agent が使える設定でMemory の初期化
    #memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    
    # 現在の日本時間を取得
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    current_datetime = now.strftime("%Y年%m月%d日 %H:%M")

    tools = load_tools(["ddg-search"])
    wiki = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            lang="ja",
            top_k_results=3,
            doc_content_chars_max=3000,
            load_all_available_meta=True,
            user_agent="MyStreamlitApp/1.0 (contact@example.com)"
        )
    )
    tools.append(wiki)


    # 現在の日本時間をLLMに与えることで、「今日」の認識の誤動作を改善させる
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
    あなたは有能なAIアシスタントです。
    現在の日本日時は {current_datetime} です。
    必要に応じてツールを使用してください。
    
    「今日」「現在」「最新」などの表現が含まれる質問では、
    現在の日本日時を基準に検索してください。

    検索結果の日付を確認し、古い情報を今日の情報として回答しないでください。
    回答は日本語で行ってください。
        """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(chat, tools, prompt)
    agent_chain = AgentExecutor(agent=agent, tools=tools, max_iterations=5, verbose=True)
    
    return agent_chain


st.title("langchain-streamlit-app")

#if "messages" not in st.session_state:  # st.session_stateにmessagesが無い場合
#    st.session_state.messages = []      # 空のリストで初期化
#    response = ""                       # 初期化処理を追加

if "chat_history" not in st.session_state:  # st.session_stateにchat_historyが無い場合
    st.session_state.chat_history = []  # 空のリストで初期化
    response = ""                       # 初期化処理を追加

if "agent_chain" not in st.session_state:
    st.session_state.agent_chain = create_agent_chain()
    #print("★create_agent_chain")

#for message in st.session_state.messages:
#    with st.chat_message(message["role"]):  # ロールごとに
#        st.markdown(message["content"])     # 会話履歴(保存されているテキスト)を表示
# 会話履歴(保存されているテキスト)を表示
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    else:
        continue

    with st.chat_message(role):
        st.markdown(message.content)

prompt = st.chat_input("What is up?")

# 6.5 入力内容と応答をブラウザに表示
if prompt:  # 入力された文字列がある
    # ユーザの入力内容を会話履歴(st.session_state.messages)に追加
    #st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):       # ユーザのアイコンで
        st.markdown(prompt)             # promptをマークダウンとして表示
        
    with st.chat_message("assistant"):  # AIのアイコンで
        callback = StreamlitCallbackHandler(st.container())
        #agent_chain = create_agent_chain()

        response = st.session_state.agent_chain.invoke(
            {
                "input": prompt, 
                "chat_history": st.session_state.chat_history
            },
            {"callbacks": [callback]}
        )
        #st.markdown(response)           # 応答をマークダウンとして表示
        st.markdown(response["output"])
        
        # ユーザの入力内容を会話履歴(st.session_state.chat_history)に追加
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        st.session_state.chat_history.append(AIMessage(content=response["output"]))

