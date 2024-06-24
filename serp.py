from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler

# 커스텀 콜백 핸들러를 사용하여 최대 시도 횟수를 설정
class MaxAttemptsCallbackHandler(BaseCallbackHandler):
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts
        self.attempts = 0

    def on_tool_start(self, tool_name, *args, **kwargs):
        self.attempts += 1
        if self.attempts > self.max_attempts:
            raise Exception("Maximum number of attempts exceeded")

# OpenAI를 사용하여 AI 응답 생성하는 함수
def generate_response(prompt, region, place):
    try:
        # 대화 맥락을 저장하기 위한 메모리 생성
        memory = ConversationBufferMemory()

        tools = load_tools(["serpapi"], llm=OpenAI(
            model_name="gpt-3.5-turbo-instruct",
            temperature=0,
            max_tokens=150  # max_tokens 값을 줄여서 응답 길이를 제한
        ))

        agent = initialize_agent(
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            llm=OpenAI(
                model_name="gpt-3.5-turbo-instruct",
                temperature=0,
                max_tokens=150  # max_tokens 값을 줄여서 응답 길이를 제한
            ),
            tools=tools,
            verbose=True,
            memory=memory,
            callbacks=[MaxAttemptsCallbackHandler(max_attempts=3)]  # 최대 시도 횟수를 3으로 설정
        )

        # 검색 결과 확인을 위한 프롬프트 실행
        response = agent.run(prompt)

        # 응답에서 "Final Answer"를 확인하여 결과 반환
        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
            return final_answer

        # 응답에서 "None" 또는 "region"이 없으면 None 반환
        if "None" in response or region not in response:
            return None

        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# 테스트용 코드
if __name__ == "__main__":
    region = '뉴욕'
    place = "The Best Pizza"
    test_prompt = f"Find information specifically about '{place}' in {region}. If you find the exact match, provide its address in the following format: [{{'place': '{place}', 'address': 'address'}}]. If you can't find an exact match, just return 'None'."
    response = generate_response(test_prompt, region, place)
    print(response)
