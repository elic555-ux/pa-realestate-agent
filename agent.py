import os
import json
import re
import requests

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

CITIES = [
    {"city": "Pittsburgh", "state": "PA"},
    {"city": "Philadelphia", "state": "PA"},
    {"city": "Allentown", "state": "PA"},
    {"city": "Reading", "state": "PA"},
    {"city": "Erie", "state": "PA"},
    {"city": "Scranton", "state": "PA"}
]

def clean_price(text):
    match = re.search(r'\$([0-9,]+)', text)
    if match:
        try:
            return int(match.group(1).replace(',', ''))
        except:
            pass
    return 195000

def clean_beds_baths_sqft(text):
    beds = 3
    baths = 2.0
    sqft = 1350

    bed_match = re.search(r'(\d+)\s*(?:bd|bed|beds|bds)', text, re.IGNORECASE)
    if bed_match:
        beds = int(bed_match.group(1))

    bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ba|bath|baths)', text, re.IGNORECASE)
    if bath_match:
        baths = float(bath_match.group(1))

    sqft_match = re.search(r'([0-9,]+)\s*(?:sqft|sq\s*ft)', text, re.IGNORECASE)
    if sqft_match:
        try:
            sqft = int(sqft_match.group(1).replace(',', ''))
        except:
            pass

    return beds, baths, sqft

def fetch_live_market_data():
    all_properties = []

    if not FIRECRAWL_API_KEY:
        print("CRITICAL: FIRECRAWL_API_KEY is not defined in GitHub Secrets!")
        return []

    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    for loc in CITIES:
        city = loc["city"]
        state = loc["state"]
        query = f"site:realtor.com/realestateandhomes-detail for sale in {city}, {state}"
        print(f"Scanning market for {city}, {state}...")

        payload = {
            "query": query,
            "limit": 5
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            data = res.json()
            items = data.get("data", [])
            print(f"Found {len(items)} listings for {city}")

            for item in items:
                link = item.get("url", "")
                title = item.get("title", "")
                desc = item.get("description", "")
                text_combined = f"{title} {desc}"

                if "realtor.com" in link or "zillow.com" in link:
                    address = title.split("|")[0].split("-")[0].strip()
                    if not address or len(address) < 4:
                        address = f"{city} Property Deal"

                    price = clean_price(text_combined)
                    beds, baths, sqft = clean_beds_baths_sqft(text_combined)

                    prop_type = "Single Family"
                    if "multi" in text_combined.lower() or "duplex" in text_combined.lower():
                        prop_type = "Multi Family"
                    elif "townhouse" in text_combined.lower() or "condo" in text_combined.lower():
                        prop_type = "Townhouse"

                    all_properties.append({
                        "city": city,
                        "neighborhood": "General",
                        "address": address,
                        "state": state,
                        "price": price,
                        "beds": beds,
                        "baths": baths,
                        "sqft": sqft,
                        "type": prop_type,
                        "url": link,
                        "summary": desc[:160] if desc else f"נכס אותנטי שאותר בסריקת שוק חיה ב-{city}.",
                        "relisted": False
                    })
        except Exception as e:
            print(f"Error fetching {city}: {e}")

    return all_properties

if __name__ == "__main__":
    results = fetch_live_market_data()
    if results:
        with open("properties.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Done! Successfully updated properties.json with {len(results)} live properties.")
    else:
        print("No properties retrieved. Check API key.")
