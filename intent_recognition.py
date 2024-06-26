import openai
import os

## 사용자의 발화 의도를 파악하는 챗봇.
## 장소 검색, 일정 추가, 일정 조회 등...

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def preprocess_input(user_input):
    # 특정 키워드를 기반으로 사전 처리하여 의도를 명확히 파악
    search_keywords = ["추천", "찾아줘", "알려줘", "어디", "검색", "카페", "맛집", "식당", "관광", "관광지"]
    schedule_keywords = ["일정", "예약", "계획", "추가", "저장", "할게", "갈게"]
    show_schedule_keywords = ["보여줘", "확인", "조회", "리스트", "요약"]
    time_keywords = ["아침", "점심", "오후", "저녁", "밤"]

    if any(keyword in user_input for keyword in search_keywords):
        return "search"
    if any(keyword in user_input for keyword in schedule_keywords):
        return "add_to_schedule"
    if any(keyword in user_input for keyword in show_schedule_keywords):
        return "show_schedule"
    if any(keyword in user_input for keyword in time_keywords):
        return "time_selection"

    return "else"

def recognize_intent(user_input):
    preprocessed_intent = preprocess_input(user_input)
    if preprocessed_intent:
        return preprocessed_intent

    messages = [
        {"role": "system", "content": "You are an assistant that classifies user intents into one of these categories: 'search', 'add_to_schedule', 'show_schedule', 'time_selection', 'else'. The input might contain typographical errors in Korean. Please correct them if necessary and output only one of these categories as the intent. If the user is asking an opinion or greeting, classify it as 'else'."},
        {"role": "user", "content": f"What is the intent of this input? '{user_input}'"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0
    )
    intent = response.choices[0].message['content'].strip().lower()
    return intent