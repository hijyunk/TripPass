import openai
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def default_chatbot_response(user_input):
    messages = [
        {"role": "system", "content": "당신은 여행 도우미입니다. 여행에 관한 이야기를 자유롭게 해주세요."},
        {"role": "user", "content": f"{user_input}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    reply = response.choices[0].message['content'].strip()
    return reply
