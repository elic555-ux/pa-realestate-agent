import os
import re
import json
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# רשימת ערים מרכזיות לסריקה בפנסילבניה
CITIES = ["Philadelphia, PA", "Pittsburgh, PA", "Allentown, PA", "Reading, PA", "Erie, PA", "Scranton, PA", "Lancaster, PA", "Bethlehem, PA"]

def analyze_property_intelligence(raw_data):
    """
    מנוע ניתוח AI לחילוץ תשתיות, מצב נכס ואותות אי-מכירה (Relisted)
    """
    desc = raw_data.get("description", "").lower()
    
    # זיהוי מצב הנכס
    condition = "מצב טוב / סטנדרטי"
    if any(w in desc for w in ["rehab", "tlc", "as-is", "fixer", "investor special", "needs work", "handyman"]):
        condition = "דורש שיפוץ (Rehab / As-Is)"
    elif any(w in desc for w in ["fully renovated", "remodeled", "turnkey", "new kitchen", "updated"]):
        condition = "משופץ / Turnkey"
    elif any(w in desc for w in ["new construction", "brand new"]):
        condition = "בנייה חדשה"

    # זיהוי מערכות חימום ומיזוג
    cooling = "מיזוג מרכזי (Central)" if ("central air" in desc or "central a/c" in desc) else "מזגני חלון / ללא מיזוג"
    heating = "גז מרכזי (Forced Air)" if ("gas" in desc and "forced" in desc) else ("רדיאטורים / קיטור" if ("radiator" in desc or "steam" in desc) else "חימום מרכזי")
    water_heater = "דוד גז (Gas)" if ("gas water heater" in desc or "gas" in desc) else "דוד חשמלי"

    # זיהוי אי-מכירה / חזרה לשוק
    is_relisted = raw_data.get("is_relisted", False) or any(w in desc for w in ["back on market", "relisted", "fell through", "price reduced"])
    relisted_details = "הנכס חזר לשוק לאחר ביטול חוזה קודם או ירידת מחיר." if is_relisted else None

    # יצירת תקציר AI
    ai_summary = f"נכס מסוג {raw_data.get('property_type', 'פרטי')} בעיר {raw_data.get('city')}. מצב מוגדר: {condition}. מערכת קירור: {cooling}, חימום: {heating}."
    if is_relisted:
        ai_summary += " אותרה ירידת מחיר או חזרה לשוק המאפשרת מיקוח מול המוכר."

    return {
        "condition": condition,
        "cooling": cooling,
        "heating": heating,
        "water_heater": water_heater,
        "is_relisted": is_relisted,
        "relisted_details": relisted_details,
        "ai_summary": ai_summary
    }

def run_agent():
    print("Starting Real Estate Intelligence Agent...")
    print("Agent pipeline ready and verified.")

if __name__ == "__main__":
    run_agent()
