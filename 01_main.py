import streamlit as st
from intent_recognition import recognize_intent
from query_extraction import extract_query
from serp_api import search_places  # 해당 API 호출을 처리하는 함수
from schedule_management import add_to_schedule, show_schedule
import pandas as pd
import pydeck as pdk
import openai
import deepl
import os

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def default_chatbot_response(user_input):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{user_input}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.5  # Adjust temperature for a balanced response
    )
    reply = response.choices[0].message['content'].strip()
    translated_reply = translator.translate_text(reply, target_lang="KO").text
    return translated_reply

def chatbot_interaction(user_input, page):
    intent = recognize_intent(user_input)
    if intent == "search":
        location, place_type = extract_query(user_input)
        results, error = search_places(location, place_type)
        if error:
            return f"Error occurred: {error}", pd.DataFrame()
        return generate_paginated_response(results, page), results
    elif intent == "add_to_schedule":
        # 예를 들어 날짜와 활동을 추출하는 추가 작업 필요
        # 단순히 예시로, "1일차 저녁에 a관광지 갈게"라는 입력이 들어왔을 때 처리하는 로직을 가정
        day, time, activity = "day1", "evening", "a관광지"  # 실제로는 NLP를 통해 추출해야 함
        add_to_schedule(day, time, activity)
        return "일정이 추가되었습니다.", pd.DataFrame()
    elif intent == "show_schedule":
        schedule = show_schedule()
        return schedule, pd.DataFrame()
    else:
        return default_chatbot_response(user_input), pd.DataFrame()

def generate_paginated_response(results, page):
    start_idx = page * 5
    end_idx = start_idx + 5
    paginated_data = results.iloc[start_idx:end_idx]

    if paginated_data.empty:
        return "더 이상 추천할 장소가 없습니다."

    response = ""
    for _, row in paginated_data.iterrows():
        response += f"Name: {row['Name']}\nAddress: {row['Address']}\nRating: {row['Rating']}\n\n"

    translated_response = translator.translate_text(response, target_lang="KO").text
    return translated_response

# Streamlit UI
st.set_page_config(layout="wide")
st.header("🤖 여행 계획 챗봇")

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["안녕하세요. 저는 여행 계획 챗봇이에요. 어느 지역에서 무엇을 하고 싶으신가요? 원하는 장소와 활동을 말씀해 주세요!"]

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'map_data' not in st.session_state:
    st.session_state['map_data'] = pd.DataFrame()

if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Create two columns with a ratio to take up more space
col1, col2 = st.columns([1.5, 1.5])

# Left column for chat
with col1:
    # User input form
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

    if submitted and user_input:
        response, df = chatbot_interaction(user_input, st.session_state.page)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
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
                st.session_state.generated.append(new_response)

    # Display conversation in reverse order
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            st.write(st.session_state['generated'][i])
            if i < len(st.session_state['past']):
                st.write(st.session_state['past'][i])

# Right column for map
with col2:
    # Display map
    if not st.session_state['map_data'].empty:
        # Filter out rows with None latitude or longitude
        map_data = st.session_state['map_data'].dropna(subset=['Latitude', 'Longitude'])

        if not map_data.empty:
            # Paginate map data
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
