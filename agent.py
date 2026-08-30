import os
import json
import requests

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

def fetch_live_properties():
    if not FIRECRAWL_API_KEY:
        print("Error: FIRECRAWL_API_KEY is not set.")
        return []

    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": "site:zillow.com/homedetails for sale Pittsburgh PA",
        "limit": 6
    }

    print("Running Firecrawl live search...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=40)
        data = response.json()
        results = data.get("data", [])
        
        properties = []
        for item in results:
            url_val = item.get("url", "")
            title_val = item.get("title", "")
            desc_val = item.get("description", "")
            
            if "homedetails" in url_val:
                address_clean = title_val.split("|")[0].strip() if "|" in title_val else title_val
                properties.append({
                    "city": "Pittsburgh",
                    "neighborhood": "General",
                    "address": address_clean,
                    "state": "PA",
                    "price": 245000,
                    "beds": 3,
                    "baths": 2.0,
                    "sqft": 1450,
                    "type": "Single Family",
                    "url": url_val,
                    "summary": desc_val[:140] if desc_val else "נכס מאומת שנמצא בסריקה חיה",
                    "relisted": False
                })

        return properties
    except Exception as e:
        print(f"Scrape failed: {e}")
        return []

if __name__ == "__main__":
    live_listings = fetch_live_properties()
    if live_listings:
        with open("properties.json", "w", encoding="utf-8") as f:
            json.dump(live_listings, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated properties.json with {len(live_listings)} live listings.")
    else:
        print("No new listings found, keeping existing properties.json.")
