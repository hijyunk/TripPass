import openai
import deepl
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

def extract_query(user_input):
    
    # 사용자 입력을 영어로 번역
    translated_input = translator.translate_text(user_input, target_lang="EN-US").text
    
    # 장소 유형 추출
    messages = [
        {"role": "system", "content": "You are an assistant that extracts the type of place from search queries. Respond only with the type of place."},
        {"role": "user", "content": f"Extract the type of place from this query: '{translated_input}'. If you cannot extract a place, respond with 'None'."}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.3
    )
    
    place_type = response.choices[0].message['content'].strip()
    
    if place_type == "None":
        return None
    return place_type