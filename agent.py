import os
import json
import requests

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "c176d85a44msh16dd337c190e79ap1809ecjsnd1f715b66103")
RAPIDAPI_HOST = "realty-in-us.p.rapidapi.com"

# מיקודי יעד מרכזיים בפנסילבניה
TARGET_ZIPS = [
    {"city": "Philadelphia", "zip": "19103"},
    {"city": "Philadelphia", "zip": "19104"},
    {"city": "Philadelphia", "zip": "19147"},
    {"city": "Pittsburgh", "zip": "15213"},
    {"city": "Pittsburgh", "zip": "15222"},
    {"city": "Allentown", "zip": "18101"},
    {"city": "Reading", "zip": "19601"},
    {"city": "Erie", "zip": "16501"},
    {"city": "Scranton", "zip": "18503"}
]

def fetch_all_properties():
    url = f"https://{RAPIDAPI_HOST}/properties/v3/list"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    all_properties = []

    for item in TARGET_ZIPS:
        city = item["city"]
        postal_code = item["zip"]
        print(f"[Agent] מושך נתונים עבור {city} (מיקוד {postal_code})...")

        payload = {
            "limit": 50,
            "offset": 0,
            "postal_code": postal_code,
            "status": ["for_sale", "ready_to_build"],
            "sort": {
                "direction": "desc",
                "field": "list_date"
            }
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                results = data.get("data", {}).get("home_search", {}).get("results", [])
                print(f"[Agent] אותרו {len(results)} נכסים במיקוד {postal_code}")

                for prop in results:
                    desc = prop.get("description", {}) or {}
                    loc = prop.get("location", {}) or {}
                    addr = loc.get("address", {}) or {}
                    flags = prop.get("flags", {}) or {}

                    prop_id = prop.get("property_id") or ""
                    price = prop.get("list_price") or desc.get("price") or 0
                    beds = desc.get("beds") or 0
                    baths = desc.get("baths_consolidated") or desc.get("baths_full") or 0
                    sqft = desc.get("sqft") or 0
                    prop_type = (desc.get("type") or "single_family").replace("_", " ").title()
                    
                    line_address = addr.get("line") or f"{city} Listing"
                    is_price_reduced = flags.get("is_price_reduced", False)

                    # קישור ישיר לעמוד הנכס ב-Realtor
                    if prop_id:
                        direct_url = f"https://www.realtor.com/realestateandhomes-detail/{prop_id}"
                    else:
                        clean_addr = line_address.replace(" ", "-").replace(",", "")
                        direct_url = f"https://www.realtor.com/realestateandhomes-detail/{clean_addr}_{city}_PA_{postal_code}"

                    all_properties.append({
                        "id": prop_id or f"{postal_code}_{len(all_properties)}",
                        "state": "PA",
                        "city": city,
                        "zip": postal_code,
                        "neighborhood": addr.get("neighborhood_name") or addr.get("county") or "General",
                        "address": line_address,
                        "price": price,
                        "beds": int(beds) if beds else 0,
                        "baths": float(baths) if baths else 0.0,
                        "sqft": int(sqft) if sqft else 0,
                        "type": prop_type,
                        "relisted": is_price_reduced,
                        "deal_type": "Price Drop" if is_price_reduced else "Active MLS",
                        "url": direct_url,
                        "summary": f"אותרה הזדמנות ב-{city} ({postal_code}). מחיר: ${price:,}." if price else f"נכס פעיל ב-{city}."
                    })
            else:
                print(f"[Agent] שגיאה במיקוד {postal_code}: סטטוס {res.status_code} - {res.text[:100]}")
        except Exception as e:
            print(f"[Agent] תקלה בקריאה למיקוד {postal_code}: {e}")

    return all_properties

def save_data(data):
    if not data:
        print("[Agent] לא נמצאו נכסים.")
        return

    with open("properties.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Agent] הסתיים בהצלחה! {len(data)} נכסים אמיתיים נשמרו לקובץ properties.json.")

if __name__ == "__main__":
    properties = fetch_all_properties()
    save_data(properties)
