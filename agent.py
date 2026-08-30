import os
import json
import requests

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "realty-in-us.p.rapidapi.com"

TARGET_CITIES = [
    {"city": "Pittsburgh", "state_code": "PA"},
    {"city": "Philadelphia", "state_code": "PA"},
    {"city": "Allentown", "state_code": "PA"},
    {"city": "Reading", "state_code": "PA"},
    {"city": "Erie", "state_code": "PA"},
    {"city": "Scranton", "state_code": "PA"}
]

def fetch_on_market_deals():
    if not RAPIDAPI_KEY:
        print("[Agent] שגיאה: RAPIDAPI_KEY אינו מוגדר.")
        return []

    url = f"https://{RAPIDAPI_HOST}/properties/v3/list"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }

    scraped_properties = []

    for target in TARGET_CITIES:
        city = target["city"]
        state = target["state_code"]
        print(f"[Agent] סורק נכסים ב-{city}, {state}...")

        payload = {
            "limit": 25,
            "offset": 0,
            "status": ["for_sale"],
            "sort": {"direction": "desc", "field": "list_date"},
            "city": city,
            "state_code": state
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=25)
            if res.status_code == 200:
                data = res.json()
                listings = data.get("data", {}).get("home_search", {}).get("results", [])
                print(f"[Agent] נמצאו {len(listings)} נכסים עבור {city}")

                for item in listings:
                    desc = item.get("description", {})
                    loc = item.get("location", {}).get("address", {})
                    flags = item.get("flags", {})

                    price = item.get("list_price") or desc.get("price") or 0
                    beds = desc.get("beds") or 0
                    baths = desc.get("baths_consolidated") or desc.get("baths_full") or 0
                    sqft = desc.get("sqft") or 0
                    prop_type = desc.get("type", "single_family").replace("_", " ").title()
                    prop_id = item.get("property_id") or item.get("mpr_id") or ""
                    
                    # חילוץ כתובת מדויקת
                    line_addr = loc.get("line") or ""
                    street_view = loc.get("street_view_url") or ""
                    
                    # חילוץ קישור ישיר אמיתי ל-Realtor
                    href = item.get("href")
                    if href:
                        if href.startswith("http"):
                            real_url = href
                        else:
                            real_url = f"https://www.realtor.com/realestateandhomes-detail/{href.lstrip('/')}"
                    elif prop_id:
                        real_url = f"https://www.realtor.com/realestateandhomes-detail/{prop_id}"
                    elif line_addr:
                        clean_addr = line_addr.replace(" ", "-").replace(",", "")
                        real_url = f"https://www.realtor.com/realestateandhomes-detail/{clean_addr}_{city}_{state}"
                    else:
                        real_url = f"https://www.realtor.com/realestateandhomes-search/{city}_{state}"

                    is_price_cut = flags.get("is_price_reduced", False)

                    scraped_properties.append({
                        "id": prop_id or f"{city}_{len(scraped_properties)}",
                        "state": state,
                        "city": city,
                        "neighborhood": loc.get("neighborhood_name") or loc.get("county") or "General",
                        "address": line_addr if line_addr else f"{city} Listing",
                        "price": price,
                        "beds": int(beds) if beds else 0,
                        "baths": float(baths) if baths else 0.0,
                        "sqft": int(sqft) if sqft else 0,
                        "type": prop_type,
                        "relisted": is_price_cut,
                        "deal_type": "Price Drop" if is_price_cut else "Active MLS",
                        "url": real_url,
                        "summary": f"נכס מאומת ב-{city}. מחיר מבוקש: ${price:,}." if price else f"נכס פעיל ב-{city}."
                    })
            else:
                print(f"[Agent] שגיאת API עבור {city}: קוד {res.status_code}")
        except Exception as err:
            print(f"[Agent] שגיאה בקריאה ל-{city}: {err}")

    return scraped_properties

def save_listings(data):
    if not data:
        print("[Agent] לא נמצאו נתונים לשמירה.")
        return

    with open("properties.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Agent] סיום מוצלח: {len(data)} נכסים נשמרו ב-properties.json.")

if __name__ == "__main__":
    deals = fetch_on_market_deals()
    save_listings(deals)
