from serpapi import GoogleSearch

def search_places(location, place_type, api_key):
    query = f"{place_type} near {location}"
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if 'error' in results:
        return None, results['error']

    return results, None
