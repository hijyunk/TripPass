from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 장소명을 추출하는 함수
def extract_location(prompt):
    try:
        # LLMChain을 초기화합니다.
        llm = OpenAI(
            model_name="gpt-3.5-turbo-instruct",
        )
        
        template = "다음 문장에서 장소명만 추출해줘. 지역명 말고 장소명만 추출해. 장소명만 반환하고 다른 텍스트는 포함하지 말아줘.\n{prompt}"
        prompt_template = PromptTemplate(template=template, input_variables=["prompt"])
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # 응답 생성
        response = chain.run(prompt=prompt)
        
        # 응답에서 장소명 추출
        location = response.strip()  # 불필요한 공백 제거
        
        return location
    except Exception as e:
        print(f"Error: {e}")
        return None
