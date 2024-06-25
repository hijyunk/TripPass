import os
import re
import streamlit as st
from streamlit_chat import message
from serpapi import GoogleSearch
import openai
import deepl
import folium
from streamlit_folium import folium_static

# 환경 변수에서 API 키를 가져옵니다.
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")

translator = deepl.Translator(DEEPL_AUTH_KEY)

def extract_keywords(user_input):
    translated_input = translator.translate_text(user_input, target_lang="EN-US").text
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts key information from user requests."},
        {"role": "user", "content": f"Extract the location and type of place from the following request:\n\nRequest: \"{translated_input}\"\n\nResponse should be in the format 'Location: [location], Type: [type]'."}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        temperature=0
    )
    
    keywords = response.choices[0].message['content'].strip()
    return keywords

def search_places(location, place_type):
    query = f"{place_type} near {location}"
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Check for errors in the results
    if 'error' in results:
        return None, results['error']

    return results, None

def generate_response_from_results(results):
    # Extract relevant information from results
    local_results = results.get('local_results', [])
    if not local_results:
        return "No results found for your query."

    places_info = []
    for result in local_results:
        name = result.get('title', 'N/A')
        address = result.get('address', 'N/A')
        rating = result.get('rating', 'N/A')
        latitude = result.get('gps_coordinates', {}).get('latitude', 'N/A')
        longitude = result.get('gps_coordinates', {}).get('longitude', 'N/A')
        places_info.append({
            "name": name,
            "address": address,
            "rating": rating,
            "latitude": latitude,
            "longitude": longitude
        })

    return places_info

def chatbot_interaction(user_query):
    # Perform the search
    keywords = extract_keywords(user_query)
    
    location = re.search(r'Location: ([^,]+)', keywords).group(1).strip()
    place_type = re.search(r'Type: (.+)', keywords).group(1).strip()
    
    results, error = search_places(location, place_type)
    if error:
        return f"Error occurred: {error}", []

    # Generate response from results
    places_info = generate_response_from_results(results)

    if not places_info:
        return "검색 결과가 없습니다.", []

    response = ""
    for place in places_info:
        response += f"Name: {place['name']}\nAddress: {place['address']}\nRating: {place['rating']}\n\n"

    # Translate response back to Korean
    translated_response = translator.translate_text(response, target_lang="KO").text
    return translated_response, places_info

# Streamlit 애플리케이션 설정
st.header("🤖 챗봇 세영이랑 대화를 해보세요")

# 세션 상태 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["안녕하세요. 저는 여행 계획 챗봇이에요. 어느 지역에서 무엇을 하고 싶으신가요? 원하는 장소와 활동을 말씀해 주세요!"]

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
    ai_response, places_info = chatbot_interaction(user_input)
    st.session_state.generated.append(ai_response or "응답을 생성하는 데 실패했습니다.")

    if places_info:
        # 첫 번째 장소의 위도와 경도로 맵 초기 위치 설정
        first_place = places_info[0]
        map_center = [first_place['latitude'], first_place['longitude']]
        map = folium.Map(location=map_center, zoom_start=12)
        for place in places_info:
            folium.Marker(
                [place['latitude'], place['longitude']],
                popup=f"{place['name']}<br>Rating: {place['rating']}<br>Address: {place['address']}"
            ).add_to(map)

        folium_static(map)

# 대화 히스토리 출력
for i in range(len(st.session_state['past'])):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    if len(st.session_state['generated']) > i:
        message(st.session_state['generated'][i], key=str(i) + '_ai')

