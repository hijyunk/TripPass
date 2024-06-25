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
    
    # GPT-3.5-turbo 모델을 사용하여 위치와 장소 유형 추출
    messages = [
        {"role": "system", "content": "You are an assistant that extracts location and type of place from search queries. Ensure to keep the full location details exactly as mentioned in the input and respond in the format 'Location: [location], Type: [place type]'."},
        {"role": "user", "content": f"Extract the nouns for location and type of place from this query: '{translated_input}'. Ensure to respond in the format 'Location: [location], Type: [place type]'."}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.3
    )
    
    extracted_info = response.choices[0].message['content'].strip()
    #print(f"Extracted Info: {extracted_info}")  # Debugging line to check the response format
    
    # 위치와 장소 유형 추출
    try:
        # 응답을 지정된 형식으로 파싱
        location_part, place_type_part = extracted_info.split(', Type: ')
        location = location_part.split('Location: ')[1].strip()
        place_type = place_type_part.strip()
    
    except Exception as e:
        #print(f"Unexpected response format: {extracted_info}")  # Debugging line
        return None, None
    
    return location, place_type