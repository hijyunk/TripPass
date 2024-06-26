import streamlit as st
from streamlit_chat import message
from intent_recognition import recognize_intent
from query_extraction import extract_query
from serpapi_search import search_places
from schedule_management import add_to_schedule, show_schedule
from default_chatbot import default_chatbot_response
import openai
import deepl
import pandas as pd
import pydeck as pdk
import deepl
import os
import re

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)


# 사용자의 데이터를 저장하는 DataFrame 초기화
if 'user_df' not in st.session_state:
    st.session_state['user_df'] = {"region": "", "plan": {}}

# 여행지(region) 추출 함수
def extract_region(user_input):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts the travel destination from user input."},
        {"role": "user", "content": f"Extract the travel destination from the following input:\n\nInput: \"{user_input}\".\n\nResponse must be the region name exactly as this query: '{user_input}'. If you cannot determine a region, respond with 'None'."}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0
    )
    region = response.choices[0].message['content'].strip()
    if region == "None":
        return None
    return region


# 챗봇 상호작용 처리
def chatbot_interaction(user_input, page):
    # region 추출
    if st.session_state['user_df']['region'] == "":
        region = extract_region(user_input)
        if region:
            # 번역하여 region을 영어로 저장
            translated_region = translator.translate_text(region, target_lang="EN-US").text
            st.session_state['user_df']['region'] = translated_region
            return f"여행지로 {region}을(를) 선택하셨습니다! 무엇을 하고 싶으신가요?", pd.DataFrame()
        else:
            return "여행지를 입력하지 않았습니다. 다시 입력해 주세요: 어느 지역으로 여행을 가시나요?", pd.DataFrame()
    else:
        intent = recognize_intent(user_input)
        
        # 장소 검색
        if intent == "search":
            location = st.session_state['user_df']['region']
            place_type = extract_query(user_input)
            if not place_type:
                return "무엇을 하고 싶으신지 모르겠어요. 다시 입력해주시겠어요?", pd.DataFrame()
            df, error = search_places(location, place_type)
            if error:
                return f"Error occurred: {error}", pd.DataFrame()
            st.session_state['map_data'] = df
            return generate_paginated_response(df, page), df
        
        # 장소 선택
        elif intent == "add_to_schedule":
            try:
                place_index = int(re.search(r'\d+', user_input).group()) - 1
                selected_place = st.session_state['map_data'].iloc[place_index]
                st.session_state['current_place'] = selected_place.to_dict()
                return "알겠습니다. 언제 가시고 싶으신가요? 아침, 점심, 오후, 저녁, 밤 중에 골라주세요.", pd.DataFrame()
            except (ValueError, IndexError, AttributeError):
                return "유효한 번호를 입력해주세요.", pd.DataFrame()
        
        # 시간 선택에 대한 응답 처리
        elif st.session_state.get('current_place') and intent == "time_selection":
            time_of_day = user_input
            place_name = st.session_state['current_place']['Name']
            add_to_schedule(time_of_day, st.session_state['current_place'])
            st.session_state['current_place'] = {}
            return f"알겠습니다. {time_of_day}에 {place_name}에 가는 것으로 저장하겠습니다! 또 다른 일정을 계획할까요? 계획을 마치셨다면 '완료'라고 입력해주세요.", pd.DataFrame()
        
        # 일정 완료
        elif user_input.strip().lower() == "완료":
            schedule_summary, map_data = show_schedule()
            st.session_state['map_data'] = map_data
            return f"알겠습니다. 최종 계획을 요약해드리겠습니다:\n\n{schedule_summary}", map_data
        
        # 일정 조회 
        elif intent == "show_schedule":
            schedule, map_data = show_schedule()
            st.session_state['map_data'] = map_data
            return schedule, pd.DataFrame()
        
        # 기본 채팅 
        else:
            return default_chatbot_response(user_input), pd.DataFrame()


# 추천할 장소를 5개씩 보여주기 
def generate_paginated_response(df, page):
    start_idx = page * 5
    end_idx = start_idx + 5
    paginated_data = df.iloc[start_idx:end_idx]

    if paginated_data.empty:
        return "더 이상 추천할 장소가 없습니다."

    response = ""
    for i, row in paginated_data.iterrows():
        response += f"{row['Position']}. 이름: {row['Name']}\n   주소: {row['Address']}\n   별점: {row['Rating']}\n\n"

    return response



#---------- Streamlit UI ----------#
st.set_page_config(layout="wide")
st.header("🤖 여행 계획 챗봇")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = [
        {"role": "bot", "text": "안녕하세요! 저는 당신의 여행 도우미예요. 어느 지역으로 여행을 가시나요?"}
    ]

if 'map_data' not in st.session_state:
    st.session_state['map_data'] = pd.DataFrame()

if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Create two columns with a ratio to take up more space
col1, col2 = st.columns([1.5, 1.5])

# 왼쪽 : 채팅 인터페이스 
with col1:
    # User input form
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

    if submitted and user_input:
        # 사용자 입력 추가
        st.session_state['conversation'].append({"role": "user", "text": user_input})
        response, df = chatbot_interaction(user_input, st.session_state.page)
        # 챗봇 응답 추가
        st.session_state['conversation'].append({"role": "bot", "text": response})
        st.session_state.map_data = df
        st.session_state.page = 0  # Reset page number for new query

    # Display 'Show more' button if there are more places to show
    if not st.session_state['map_data'].empty:
        start_idx = st.session_state['page'] * 5
        end_idx = start_idx + 5
        if end_idx < len(st.session_state['map_data']):
            if st.button("다른 추천 보기"):
                st.session_state.page += 1
                new_response = generate_paginated_response(st.session_state['map_data'], st.session_state['page'])
                st.session_state['conversation'].append({"role": "bot", "text": new_response})

    # Display conversation in reverse order
    for i in range(len(st.session_state['conversation']) - 1, -1, -1):
        if st.session_state['conversation'][i]['role'] == 'bot':
            message(st.session_state['conversation'][i]['text'], key=f"bot_{i}")
        else:
            message(st.session_state['conversation'][i]['text'], is_user=True, key=f"user_{i}")

# 오른쪽 : 지도 인터페이스 
with col2:
    # Display map
    if not st.session_state['map_data'].empty:
        # Filter out rows with None latitude or longitude
        map_data = st.session_state['map_data'].dropna(subset=['latitude', 'longitude'])

        if not map_data.empty:
            # Paginate map data
            start_idx = st.session_state['page'] * 5
            end_idx = start_idx + 5
            paginated_data = map_data.iloc[start_idx:end_idx]

            avg_lat = paginated_data['latitude'].mean()
            avg_lng = paginated_data['longitude'].mean()

            layer = pdk.Layer(
                'ScatterplotLayer',
                data=paginated_data,
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=avg_lat,
                longitude=avg_lng,
                zoom=12
            )

            r = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v10',
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "Name: {Name}\nAddress: {Address}\nRating: {Rating}"}
            )

            st.pydeck_chart(r)
        else:
            st.write("No valid data to display on the map.")
