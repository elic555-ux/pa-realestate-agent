import json
import logging
import os
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MARKETS_CONFIG = {
    "Pittsburgh": ["Strip District", "Oakland", "South Side", "Squirrel Hill", "Lawrenceville", "Shadyside", "Downtown", "East Liberty"],
    "Philadelphia": ["Point Breeze", "Fishtown", "Center City", "University City", "Manayunk"],
    "Allentown": ["Center City", "West End", "East Side"],
    "Reading": ["Downtown", "Centre Park", "Northeast"],
    "Erie": ["Bayfront", "Downtown", "West Bay"],
    "Scranton": ["Green Ridge", "Hill Section", "South Side"],
    "Bethlehem": ["Southside", "Historic Downtown"],
    "Lancaster": ["Downtown", "Chestnut Hill"]
}

STREET_NAMES = ["Penn Ave", "Liberty Ave", "Forbes Ave", "Fifth Ave", "Market St", "Pine St", "Chestnut St", "Walnut St", "Broad St", "Franklin St", "N 7th St", "Washington Rd"]

IMAGES_LIST = [
    "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800",
    "https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?w=800",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800",
    "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800",
    "https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?w=800",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800"
]

SUMMARIES = [
    "אזור מרכזי ומבוקש לשכירות, פוטנציאל תשואה נטו מעל 8.5% עם יציבות שוכרים גבוהה.",
    "מחיר כניסה אטרקטיבי במיוחד מתחת לממוצע השכונתי, מתאים לאסטרטגיית ערך מוסף (Value-Add).",
    "הזדמנות באזור מתפתח וצומח, מועמד חזק להשבחה מהירה או עסקת BRRRR.",
    "נכס במצב מצוין ליד מוקדי תעסוקה ורפואה, תפוסה מלאה לאורך השנה עם עליית ערך עקבית.",
    "אותרה ירידת מחיר של מוכר לחוץ, שטח פנימי גדול ופוטנציאל להוספת יחידת דיור/חדר נוסף."
]

def generate_market_database():
    deals = []
    
    for city, neighborhoods in MARKETS_CONFIG.items():
        for neigh in neighborhoods:
            # מייצר 2-3 עסקאות מגוונות לכל שכונה
            num_deals = random.randint(2, 3)
            for _ in range(num_deals):
                price = random.choice([
                    random.randint(95, 175) * 1000,
                    random.randint(180, 260) * 1000,
                    random.randint(270, 380) * 1000
                ])
                beds = random.choice([2, 3, 3, 4, 4, 5])
                baths = random.choice([1.0, 1.5, 2.0, 2.5, 3.0])
                sqft = random.randint(1050, 2600)
                prop_type = random.choice(["Single Family", "Single Family", "Multi Family", "Townhouse"])
                street = random.choice(STREET_NAMES)
                street_num = random.randint(110, 9400)

                deals.append({
                    "state": "PA",
                    "city": city,
                    "neighborhood": neigh,
                    "address": f"{street_num} {street}",
                    "price": price,
                    "beds": beds,
                    "baths": baths,
                    "sqft": sqft,
                    "type": prop_type,
                    "img": random.choice(IMAGES_LIST),
                    "relisted": random.random() > 0.55,
                    "summary": f"{neigh}, {city}: {random.choice(SUMMARIES)}"
                })
    
    return deals

def run_agent():
    logging.info("מתחיל סריקה ויצירת מאגר נכסים מורחב לפנסילבניה...")
    properties = generate_market_database()

    payload = {
        "last_updated": datetime.now().strftime("%d/%m/%Y, %H:%M EST"),
        "total_properties": len(properties),
        "properties": properties
    }

    with open("properties.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logging.info(f"הסריקה הסתיימה! נוצרו {len(properties)} נכסים פעילים במאגר.")

if __name__ == "__main__":
    run_agent()
