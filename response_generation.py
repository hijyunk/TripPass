import openai
import os
import pandas as pd
import deepl

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

def generate_response_from_results(results):
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
