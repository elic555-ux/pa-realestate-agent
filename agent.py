import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 2 נכסים אמיתיים לבדיקה מדויקת
TEST_PROPERTIES = [
    {
        "state": "PA",
        "city": "Pittsburgh",
        "neighborhood": "Oakland",
        "address": "312 S Bouquet St",
        "price": 195000,
        "beds": 3,
        "baths": 2.0,
        "sqft": 1420,
        "type": "Single Family",
        "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1200&q=80",
        "url": "https://www.zillow.com/homes/312-S-Bouquet-St-Pittsburgh,-PA-15213_rb/",
        "relisted": True,
        "summary": "נכס אותנטי ב-Oakland פיטסבורג. סמוך לאוניברסיטאות CMU ו-Pitt, פוטנציאל שכירות מעולה."
    },
    {
        "state": "PA",
        "city": "Philadelphia",
        "neighborhood": "Point Breeze",
        "address": "2108 Point Breeze Ave",
        "price": 195000,
        "beds": 3,
        "baths": 2.0,
        "sqft": 1400,
        "type": "Townhouse",
        "img": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
        "url": "https://www.zillow.com/homes/2108-Point-Breeze-Ave-Philadelphia,-PA-19145_rb/",
        "relisted": False,
        "summary": "נכס בדרום פילדלפיה, אזור בצמיחה עם ביקוש גבוה למגורים ושכירות."
    }
]

def run_agent():
    logging.info("מעדכן 2 נכסי בדיקה...")
    
    payload = {
        "last_updated": datetime.now().strftime("%d/%m/%Y, %H:%M EST"),
        "total_properties": len(TEST_PROPERTIES),
        "properties": TEST_PROPERTIES
    }

    with open("properties.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logging.info("קובץ properties.json עודכן בהצלחה עם 2 הנכסים.")

if __name__ == "__main__":
    run_agent()
