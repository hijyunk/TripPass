# chatbot.py
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory

def generate_response(prompt):
    try:
        # 대화 맥락을 저장하기 위한 메모리 생성
        if 'memory' not in st.session_state:
            st.session_state.memory = ConversationBufferMemory()
        # ConversationChain을 초기화합니다.
        conversation_chain = ConversationChain(
            llm=ChatOpenAI(
            model_name="gpt-4",
        ),
            memory=st.session_state.memory
        )
        response = conversation_chain.run(prompt)
        
        return response
    except Exception as e:
        st.error(f"error: {e}")