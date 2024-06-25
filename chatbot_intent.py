import openai
import os
import deepl

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

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
