import openai
import deepl
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

def extract_query(user_input):
    user_input = translator.translate_text(user_input, target_lang="EN-US").text
    
    messages = [
        {"role": "system", "content": "You are an assistant that extracts location and type of place from search queries."},
        {"role": "user", "content": f"Extract the location and type of place from this query: '{user_input}'"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.3
    )
    extracted_info = response.choices[0].message['content'].strip()
    location, place_type = extracted_info.split(',')
    location = location.split(': ')[1].strip()
    place_type = place_type.split(': ')[1].strip()
    return location, place_type
