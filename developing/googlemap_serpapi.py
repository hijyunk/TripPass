import os
import re
from serpapi import GoogleSearch
import openai
import deepl

SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]
translator = deepl.Translator(DEEPL_AUTH_KEY)

def extract_keywords(user_input):
    user_input = translator.translate_text(user_input, target_lang="EN-US")
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts key information from user requests."},
        {"role": "user", "content": f"Extract the location and type of place from the following request:\n\nRequest: \"{user_input}\"\n\nResponse should be in the format 'Location: [location], Type: [type]'."}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        temperature=0
    )
    
    keywords = response.choices[0].message['content'].strip()
    print("Extracted keywords:", keywords)
    return keywords


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
        places_info.append(f"Name: {name}\nAddress: {address}\nRating: {rating}\n")

    places_text = "\n".join(places_info)
    
    # Generate a detailed response using GPT-3.5-turbo
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Based on the following search results, provide recommendations:\n\n{places_text}"}
        ]
    )

    return response.choices[0].message['content']

def chatbot_interaction(user_query):
    # Perform the search
    keywords = extract_keywords(user_query)
    
    location = re.search(r'Location: ([^,]+)', keywords).group(1).strip()
    place_type = re.search(r'Type: (.+)', keywords).group(1).strip()
    
    results, error = search_places(location, place_type)
    if error:
        return f"Error occurred: {error}"

    # Generate response from results
    response = generate_response_from_results(results)
    return response

# Example usage
if __name__ == "__main__":
    user_query = "뉴욕에 있는 카페 추천해줘."
    response = chatbot_interaction(user_query)
    print(response)