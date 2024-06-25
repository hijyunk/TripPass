import os
import re
import pandas as pd
import streamlit as st
import openai
from streamlit_chat import message
import pydeck as pdk
from serpapi_search import search_places
from chatbot_intent import extract_keywords
from response_generation import generate_response_from_results, generate_paginated_response

# API 키 설정
SERPAPI_API_KEY = os.environ['SERPAPI_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]

# Streamlit UI 설정
st.set_page_config(layout="wide")
st.header("🤖 여행 계획 챗봇")

# 세션 상태 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["안녕하세요. 저는 여행 계획 챗봇이에요. 어느 지역에서 무엇을 하고 싶으신가요? 원하는 장소와 활동을 말씀해 주세요!"]

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'map_data' not in st.session_state:
    st.session_state['map_data'] = pd.DataFrame()

if 'page' not in st.session_state:
    st.session_state['page'] = 0

# 채팅 및 지도 인터페이스 설정
col1, col2 = st.columns([1.5, 1.5])

# 왼쪽 컬럼: 채팅 인터페이스
with col1:
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

    if submitted and user_input:
        keywords = extract_keywords(user_input)
        location = re.search(r'Location: ([^,]+)', keywords).group(1).strip()
        place_type = re.search(r'Type: (.+)', keywords).group(1).strip()

        results, error = search_places(location, place_type, SERPAPI_API_KEY)
        if error:
            st.session_state.generated.append(f"Error occurred: {error}")
        else:
            _, df = generate_response_from_results(results)
            response = generate_paginated_response(df, st.session_state.page)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
            st.session_state.map_data = df
            st.session_state.page = 0

    if not st.session_state['map_data'].empty:
        start_idx = st.session_state['page'] * 5
        end_idx = start_idx + 5
        if end_idx < len(st.session_state['map_data']):
            if st.button("다른 추천 보기"):
                st.session_state.page += 1
                new_response = generate_paginated_response(st.session_state['map_data'], st.session_state['page'])
                st.session_state.generated.append(new_response)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state['generated'][i], key=f"bot_{i}")
            if i < len(st.session_state['past']):
                message(st.session_state['past'][i], is_user=True, key=f"user_{i}")

# 오른쪽 컬럼: 지도 인터페이스
with col2:
    if not st.session_state['map_data'].empty:
        map_data = st.session_state['map_data'].dropna(subset=['Latitude', 'Longitude'])
        if not map_data.empty:
            start_idx = st.session_state['page'] * 5
            end_idx = start_idx + 5
            paginated_data = map_data.iloc[start_idx:end_idx]

            avg_lat = paginated_data['Latitude'].mean()
            avg_lng = paginated_data['Longitude'].mean()

            layer = pdk.Layer(
                'ScatterplotLayer',
                data=paginated_data,
                get_position='[Longitude, Latitude]',
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
