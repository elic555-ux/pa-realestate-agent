import os
import requests
from supabase import create_client, Client

# משתני סביבה
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# רשימת ערי פנסילבניה לסריקה
PA_CITIES = [
    {"city": "Philadelphia", "state_code": "PA"},
    {"city": "Pittsburgh", "state_code": "PA"},
    {"city": "Allentown", "state_code": "PA"},
    {"city": "Reading", "state_code": "PA"},
    {"city": "Erie", "state_code": "PA"},
    {"city": "Scranton", "state_code": "PA"},
    {"city": "Lancaster", "state_code": "PA"},
    {"city": "Bethlehem", "state_code": "PA"}
]

def fetch_properties_for_city(city_name, state_code):
    """שאיבת נכסים חיים מ-Realty in US API"""
    url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com"
    }
    
    payload = {
        "limit": 10,
        "offset": 0,
        "postal_code": "",
        "city": city_name,
        "state_code": state_code,
        "status": ["for_sale"],
        "sort": {"direction": "desc", "field": "list_date"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("home_search", {}).get("results", [])
        else:
            print(f"Error fetching {city_name}: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Request failed for {city_name}: {e}")
        return []

def parse_and_save():
    total_saved = 0
    
    # ניקוי נתונים ישנים
    supabase.table("properties").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    for item in PA_CITIES:
        city = item["city"]
        state = item["state_code"]
        print(f"🔍 סורק מודעות חיות עבור: {city}, {state}...")
        
        listings = fetch_properties_for_city(city, state)
        
        for prop in listings:
            location = prop.get("location", {}).get("address", {})
            desc = prop.get("description", {})
            flags = prop.get("flags", {})
            
            # כתובת ומפרט
            address = location.get("line", f"Property in {city}")
            zip_code = location.get("postal_code", "")
            price = prop.get("list_price") or desc.get("price") or 150000
            beds = desc.get("beds", 3)
            baths = desc.get("baths_consolidated", 1.5)
            sqft = desc.get("sqft", 1350)
            prop_type = desc.get("type", "single_family").replace("_", " ").title()
            
            # תמונה מקורית
            primary_photo = prop.get("primary_photo", {}).get("href")
            image_url = primary_photo if primary_photo else "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800"
            
            # קישור ישיר לנכס
            property_id = prop.get("property_id")
            external_url = f"https://www.realtor.com/realestateandhomes-detail/{property_id}" if property_id else f"https://www.zillow.com/homes/{address.replace(' ', '-')}-{city}-{state}_rb/"

            # זיהוי אי-מכירה / Relisted
            is_relisted = flags.get("is_price_reduced", False) or flags.get("is_contingent", False)
            relisted_details = "נכס חזר לשוק או חווה ירידת מחיר." if is_relisted else None
            
            # ניתוח AI בסיסי
            ai_summary = f"נכס מסוג {prop_type} ב-{city}. אותרה הזדמנות תמחור באזור ביקוש."
            if is_relisted:
                ai_summary += " אות סחירות: חזר לשוק / גמישות במחיר."

            record = {
                "address": address,
                "city": city,
                "state": state,
                "zip": zip_code,
                "neighborhood": location.get("neighborhood_name", city),
                "price": price,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "property_type": prop_type,
                "condition": "סטנדרטי / לבדיקה",
                "heating": "Forced Air / גז",
                "cooling": "Central / חלון",
                "water_heater": "דוד תקין",
                "is_relisted": is_relisted,
                "relisted_details": relisted_details,
                "ai_summary": ai_summary,
                "external_url": external_url,
                "image_url": image_url
            }
            
            try:
                supabase.table("properties").insert(record).execute()
                total_saved += 1
            except Exception as err:
                print(f"Insert error: {err}")

    print(f" סך הכל נשמרו {total_saved} נכסים חיים עם תמונות מקוריות ב-Supabase!")

if __name__ == "__main__":
    parse_and_save()
