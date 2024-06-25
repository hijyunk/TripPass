from serpapi import GoogleSearch
import os

SERPAPI_API_KEY = os.environ['SERPAPI_API_KEY']

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

    if 'error' in results:
        return None, results['error']

    return results, None
