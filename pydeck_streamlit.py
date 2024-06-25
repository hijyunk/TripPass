import os
import re
import pandas as pd
import streamlit as st
from serpapi import GoogleSearch
import openai
import deepl
from streamlit_chat import message
import pydeck as pdk

SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]

translator = deepl.Translator(DEEPL_AUTH_KEY)

## user_input에서 keywords 추출하기 
def extract_keywords(user_input):
    user_input = translator.translate_text(user_input, target_lang="EN-US").text
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts key information from user requests."},
        {"role": "user", "content": f"Extract the location and type of place from the following request:\n\nRequest: \"{user_input}\"\n\nResponse should be in the format 'Location: [location], Type: [type]'."}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0
    )
    
    keywords = response.choices[0].message['content'].strip()
    print("Extracted keywords:", keywords)
    return keywords

## 추출된 키워드로 장소 찾기 
def search_places(location, place_type):
    query = f"{place_type} near {location}"
    print("Generated Query:", query)
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

## 결과로부터 응답 생성하기 
def generate_response_from_results(results):
    # Extract relevant information from results
    local_results = results.get('local_results', [])
    if not local_results:
        return "No results found for your query.", pd.DataFrame()

    places_info = []
    data = []
    for result in local_results:
        name = result.get('title', 'N/A')
        address = result.get('address', 'N/A')
        rating = result.get('rating', 'N/A')
        latitude = result.get('gps_coordinates', {}).get('latitude', None)
        longitude = result.get('gps_coordinates', {}).get('longitude', None)
        places_info.append(f"Name: {name}\nAddress: {address}\nRating: {rating}\nLatitude: {latitude}\nLongitude: {longitude}\n")
        data.append({
            "Name": name,
            "Address": address,
            "Rating": rating,
            "Latitude": latitude,
            "Longitude": longitude
        })

    places_text = "\n".join(places_info)
    df = pd.DataFrame(data)
    
    # Generate a detailed response using GPT-3.5-turbo
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Based on the following search results, provide recommendations:\n\n{places_text}"}
        ],
        max_tokens=1000
    )

    return response.choices[0].message['content'], df

def generate_paginated_response(df, page):
    start_idx = page * 5
    end_idx = start_idx + 5
    paginated_data = df.iloc[start_idx:end_idx]

    if paginated_data.empty:
        return "더 이상 추천할 장소가 없습니다."

    response = ""
    for _, row in paginated_data.iterrows():
        response += f"Name: {row['Name']}\nAddress: {row['Address']}\nRating: {row['Rating']}\n\n"

    translated_response = translator.translate_text(response, target_lang="KO").text
    return translated_response

## 챗봇 대화하기 
def chatbot_interaction(user_query, page):
    # Perform the search
    keywords = extract_keywords(user_query)
    
    location = re.search(r'Location: ([^,]+)', keywords).group(1).strip()
    place_type = re.search(r'Type: (.+)', keywords).group(1).strip()
    
    results, error = search_places(location, place_type)
    if error:
        return f"Error occurred: {error}", pd.DataFrame()

    # Generate response from results
    _, df = generate_response_from_results(results)
    response = generate_paginated_response(df, page)
    return response, df


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
            message(st.session_state['generated'][i], key=f"bot_{i}")
            if i < len(st.session_state['past']):
                message(st.session_state['past'][i], is_user=True, key=f"user_{i}")

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
