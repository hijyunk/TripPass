# main.py
import streamlit as st
from streamlit_chat import message
from chatbot import generate_response as chatbot_generate_response
from serp import generate_response as serpapi_generate_response

st.header("🤖 여행 계획 챗봇")

# 세션 상태 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# 사용자 입력을 받는 폼 설정
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('You: ', '', key='input')
    submitted = st.form_submit_button('Send')

# 사용자 입력 처리 및 응답 생성
if submitted and user_input:
    # 사용자 입력 먼저 출력
    st.session_state.past.append(user_input)
    
    # AI 응답 생성
    ai_response = chatbot_generate_response(user_input)
    st.session_state.generated.append("챗봇 응답: " + (ai_response or "응답을 생성하는 데 실패했습니다."))

    # 진위 검사
    verification_response = serpapi_generate_response(ai_response)
    st.session_state.generated.append("검증된 응답: " + (verification_response or "진위를 확인할 수 없습니다."))

    # 최종 업데이트를 위해 다시 렌더링
    st.experimental_rerun()

# 대화 히스토리 출력
for i in range(len(st.session_state['past']) - 1, -1, -1):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    if len(st.session_state['generated']) > i:
        message(st.session_state['generated'][i], key=str(i))