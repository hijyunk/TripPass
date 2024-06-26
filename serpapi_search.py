from serpapi import GoogleSearch
import pandas as pd
import os

SERPAPI_API_KEY = os.environ['SERPAPI_API_KEY']

def search_places(location, place_type):
    query = f"{place_type} near {location}"
    params = {
        "engine": "google_local",
        "q": query,
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if 'error' in results:
        return None, results['error']

    local_results = results.get('local_results', [])
    
    data = []
    for result in local_results:
        data.append({
            "Name": result.get('title', 'N/A'),
            "Address": result.get('address', 'N/A'),
            "Rating": result.get('rating', 'N/A'),
            "latitude": result.get('gps_coordinates', {}).get('latitude', None),
            "longitude": result.get('gps_coordinates', {}).get('longitude', None),
            "Position": result.get('position', None)
        })

    df = pd.DataFrame(data)
    return df, None
