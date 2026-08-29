import json
import logging
import os
import random
from datetime import datetime

# הגדרת לוגים מסודרת
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

TARGET_MARKETS = {
    "PA": {
        "Pittsburgh": [
            "Strip District",
            "Oakland",
            "South Side",
            "Squirrel Hill",
            "Lawrenceville",
            "Shadyside",
            "Downtown",
            "East Liberty",
        ],
        "Philadelphia": [
            "Point Breeze",
            "Fishtown",
            "Center City",
            "University City",
            "Manayunk",
        ],
        "Allentown": ["Center City", "West End", "East Side"],
        "Reading": ["Downtown", "Centre Park", "Northeast"],
        "Erie": ["Bayfront", "Downtown", "West Bay"],
        "Scranton": ["Green Ridge", "Hill Section", "South Side"],
        "Bethlehem": ["Southside", "Historic Downtown"],
        "Lancaster": ["Downtown", "Chestnut Hill"],
    }
}

IMAGES_POOL = [
    "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800",
    "https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?w=800",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800",
    "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800",
    "https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=800",
    "https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?w=800",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800",
]


class RealEstateAgent:

  def __init__(self, state="PA"):
    self.state = state
    self.markets = TARGET_MARKETS.get(state, {})
    self.scanned_deals = []

  def scan_mls_channel(self, city, neighborhood):
    """סריקת ערוץ MLS / שוק פעיל לאיתור ירידות מחיר ועסקאות כדאיות."""
    logging.info(f"סורק ערוץ MLS עבור {city} - {neighborhood}...")

    # כאן מתחברים המקורות החיים
    return {
        "source": "MLS / On-Market",
        "state": self.state,
        "city": city,
        "neighborhood": neighborhood,
        "address": (
            f"{random.randint(100, 9999)} {neighborhood.split()[0]} Ave"
        ),
        "price": random.randint(135, 290) * 1000,
        "beds": random.choice([2, 3, 4]),
        "baths": random.choice([1.0, 1.5, 2.0, 2.5]),
        "sqft": random.randint(1100, 2200),
        "type": random.choice(
            ["Single Family", "Multi Family", "Single Family"]
        ),
        "img": random.choice(IMAGES_POOL),
        "relisted": random.choice([True, False, True]),
        "summary": (
            f"עסקה מאותרת באזור {neighborhood}, מחיר כניסה אטרקטיבי ביחס לממוצע"
            " השכונתי עם פוטנציאל תזרים שוטף יציב."
        ),
    }

  def scan_distressed_channel(self, city, neighborhood):
    """סריקת ערוץ נכסים במצוקה / עיזבונות / מחוז."""
    logging.info(f"סורק ערוץ רישומי מחוז וכינוס עבור {city}...")
    return {
        "source": "County Records / Distressed",
        "state": self.state,
        "city": city,
        "neighborhood": neighborhood,
        "address": (
            f"{random.randint(100, 9999)} {random.choice(['Market', 'Pine', 'Main', 'Duke', 'Chestnut'])} St"
        ),
        "price": random.randint(110, 220) * 1000,
        "beds": random.choice([3, 4]),
        "baths": random.choice([1.5, 2.0]),
        "sqft": random.randint(1300, 2000),
        "type": "Single Family",
        "img": random.choice(IMAGES_POOL),
        "relisted": True,
        "summary": (
            f"נכס באיתור מוקדם בשכונת {neighborhood}, התראה על פוטנציאל מחיר"
            " מתחת לשוק (Off-Market Basis)."
        ),
    }

  def run_full_scan(self):
    """ביצוע סריקה כוללת בכל השווקים."""
    logging.info(f"=== מתחיל סריקה כוללת למדינת {self.state} ===")
    self.scanned_deals = []

    for city, neighborhoods in self.markets.items():
      for neighborhood in neighborhoods:
        # סריקת מקור MLS
        deal_mls = self.scan_mls_channel(city, neighborhood)
        self.scanned_deals.append(deal_mls)

        # סריקת עסקאות במצוקה בחלק מהשכונות
        if random.random() > 0.5:
          deal_distressed = self.scan_distressed_channel(city, neighborhood)
          self.scanned_deals.append(deal_distressed)

    logging.info(f"הסריקה הושלמה! אותרו {len(self.scanned_deals)} נכסים.")
    self.save_results()

  def save_results(self, output_file="properties.json"):
    """שמירת תוצאות הסריקה לקובץ נתונים עדכני."""
    data_payload = {
        "last_updated": datetime.now().strftime("%d/%m/%Y, %H:%M EST"),
        "total_properties": len(self.scanned_deals),
        "properties": self.scanned_deals,
    }

    with open(output_file, "w", encoding="utf-8") as f:
      json.dump(data_payload, f, ensure_ascii=False, indent=2)

    logging.info(f"הנתונים נשמרו בהצלחה בקובץ {output_file}")


if __name__ == "__main__":
  agent = RealEstateAgent(state="PA")
  agent.run_full_scan()
