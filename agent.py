import os
import json
import requests

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "c176d85a44msh16dd337c190e79ap1809ecjsnd1f715b66103")
RAPIDAPI_HOST = "realty-in-us.p.rapidapi.com"

# מוקדי יעד מרכזיים בפנסילבניה (לפי מחוזות וערים)
TARGET_REGIONS = [
    # Philadelphia County
    {"city": "Philadelphia", "zip": "19103", "county": "Philadelphia"},
    {"city": "Philadelphia", "zip": "19104", "county": "Philadelphia"},
    {"city": "Philadelphia", "zip": "19147", "county": "Philadelphia"},
    {"city": "Philadelphia", "zip": "19124", "county": "Philadelphia"},
    # Allegheny County (Pittsburgh)
    {"city": "Pittsburgh", "zip": "15213", "county": "Allegheny"},
    {"city": "Pittsburgh", "zip": "15222", "county": "Allegheny"},
    {"city": "Pittsburgh", "zip": "15210", "county": "Allegheny"},
    # Lehigh County
    {"city": "Allentown", "zip": "18101", "county": "Lehigh"},
    # Berks County
    {"city": "Reading", "zip": "19601", "county": "Berks"},
    # Erie County
    {"city": "Erie", "zip": "16501", "county": "Erie"},
    # Lackawanna County
    {"city": "Scranton", "zip": "18503", "county": "Lackawanna"}
]

KEYWORDS_DISTRESSED = [
    "foreclosure", "sheriff", "bank owned", "reo", "cash only",
    "as-is", "as is", "investor", "handyman", "probate", "estate sale", "motivated"
]

def analyze_deal_type(flags, description_text):
    text = (description_text or "").lower()
    
    if flags.get("is_foreclosure") or "foreclosure" in text or "sheriff" in text:
        return "Foreclosure / Sheriff Sale"
    if flags.get("is_bank_owned") or "reo" in text or "bank owned" in text:
        return "Bank Owned / REO"
    if flags.get("is_short_sale") or "short sale" in text:
        return "Short Sale"
    if any(kw in text for kw in ["probate", "estate sale", "executor"]):
        return "Probate / Estate"
    if flags.get("is_price_reduced"):
        return "Price Drop / Motivated"
    if any(kw in text for kw in ["as-is", "as is", "cash only", "handyman", "investor special"]):
        return "Distressed Opportunity"
    
    return "Active MLS"

def fetch_county_intelligence():
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    url = f"https://{RAPIDAPI_HOST}/properties/v3/list"

    collected_leads = []

    for region in TARGET_REGIONS:
        city = region["city"]
        postal_code = region["zip"]
        county = region["county"]
        print(f"[PA-Agent] סורק נתוני עסקאות ומצוקה ב-{city} ({county} County, {postal_code})...")

        payload = {
            "limit": 50,
            "offset": 0,
            "postal_code": postal_code,
            "status": ["for_sale", "ready_to_build"],
            "sort": {"direction": "desc", "field": "list_date"}
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                results = data.get("data", {}).get("home_search", {}).get("results", [])

                for item in results:
                    desc = item.get("description", {}) or {}
                    loc = item.get("location", {}) or {}
                    addr = loc.get("address", {}) or {}
                    flags = item.get("flags", {}) or {}

                    prop_id = item.get("property_id") or ""
                    price = item.get("list_price") or desc.get("price") or 0
                    beds = desc.get("beds") or 0
                    baths = desc.get("baths_consolidated") or desc.get("baths_full") or 0
                    sqft = desc.get("sqft") or 0
                    prop_type = (desc.get("type") or "single_family").replace("_", " ").title()
                    raw_text = desc.get("text") or ""

                    line_addr = addr.get("line") or f"{city} Property"
                    is_price_reduced = flags.get("is_price_reduced", False)
                    deal_classification = analyze_deal_type(flags, raw_text)

                    if prop_id:
                        direct_url = f"https://www.realtor.com/realestateandhomes-detail/{prop_id}"
                    else:
                        clean_addr = line_addr.replace(" ", "-").replace(",", "")
                        direct_url = f"https://www.realtor.com/realestateandhomes-detail/{clean_addr}_{city}_PA_{postal_code}"

                    lead_summary = (
                        f"אותרה עסקת {deal_classification} במחוז {county} ({city}). "
                        f"מחיר מבוקש: ${price:,}." if price else f"נכס רשום במחוז {county}."
                    )

                    collected_leads.append({
                        "id": prop_id or f"{postal_code}_{len(collected_leads)}",
                        "state": "PA",
                        "county": county,
                        "city": city,
                        "zip": postal_code,
                        "neighborhood": addr.get("neighborhood_name") or county,
                        "address": line_addr,
                        "price": price,
                        "beds": int(beds) if beds else 0,
                        "baths": float(baths) if baths else 0.0,
                        "sqft": int(sqft) if sqft else 0,
                        "type": prop_type,
                        "relisted": is_price_reduced,
                        "deal_type": deal_classification,
                        "url": direct_url,
                        "summary": lead_summary
                    })
            else:
                print(f"[PA-Agent] שגיאה בסריקת {postal_code}: סטטוס {res.status_code}")
        except Exception as e:
            print(f"[PA-Agent] שגיאה בקריאה ל-{postal_code}: {e}")

    return collected_leads

def save_output(leads):
    if not leads:
        print("[PA-Agent] לא נמצאו נתונים לשמירה.")
        return

    with open("properties.json", "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    print(f"[PA-Agent] נשמרו בהצלחה {len(leads)} נכסים ומודעות מצוקה ב-properties.json.")

if __name__ == "__main__":
    leads = fetch_county_intelligence()
    save_output(leads)
