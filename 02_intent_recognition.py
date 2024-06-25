import openai
import os

## 사용자의 발화 의도를 파악하는 챗봇.
## 장소 검색, 일정 추가, 일정 조회 등...

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def recognize_intent(user_input):
    messages = [
        {"role": "system", "content": "You are an assistant that classifies user intents into categories: search, add_to_schedule, show_schedule."},
        {"role": "user", "content": f"What is the intent of this input? '{user_input}'"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        temperature=0.3
    )
    intent = response.choices[0].message['content'].strip().lower()
    return intent