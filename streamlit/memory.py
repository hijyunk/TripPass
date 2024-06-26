import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryBufferMemory

def generate_response(prompt):
    try:
        # 대화 맥락을 저장하기 위한 메모리 생성
        if 'memory' not in st.session_state:
            st.session_state.memory = ConversationSummaryBufferMemory(
                llm=ChatOpenAI(model="gpt-3.5-turbo"),
                max_token_limit=1000  # 필요한 토큰 제한 설정
            )

        # ConversationChain을 초기화합니다.
        conversation_chain = ConversationChain(
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
            ),
            memory=st.session_state.memory
        )
        
        response = conversation_chain.run(prompt)
        
        # 대화 요약 업데이트를 위해 입력과 출력을 저장
        st.session_state.memory.save_context({"input": prompt}, {"output": response})
        memory_variables = st.session_state.memory.load_memory_variables({})
        
        summary = memory_variables.get('summary', 'No summary available')
        
        return response, summary, memory_variables
    except Exception as e:
        st.error(f"error: {e}")

def show():
    # Streamlit 애플리케이션 설정
    st.header("🤖기억하는 세영이2 (요약가능)")

    # 세션 상태 초기화
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'summary' not in st.session_state:
        st.session_state['summary'] = "No summary available"

    # 사용자 입력을 받는 폼 설정
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

    # 사용자 입력 처리 및 응답 생성
    if submitted and user_input:
        # 사용자 입력 먼저 출력
        st.session_state.past.append(user_input)
        
        # AI 응답 생성 및 요약 업데이트
        ai_response, summary, _ = generate_response(user_input)
        st.session_state.generated.append(ai_response or "응답을 생성하는 데 실패했습니다.")
        st.session_state.summary = summary

    # 대화 히스토리 출력
    for i in range(len(st.session_state['past']) - 1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        if len(st.session_state['generated']) > i:
            message(st.session_state['generated'][i], key=str(i))

    # 대화 요약 출력
    st.subheader("대화 요약")
    show_debug_button = st.button("요약 보기")
    if show_debug_button:
        ai_response, summary, memory_variables = generate_response(user_input)
        st.text_area("디버깅 출력", value=str(memory_variables), height=200)    