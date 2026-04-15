"""
seed_food_data.py
Run once to insert the expanded food POI dataset into the existing database.
Safe to re-run — skips rows where (name, country) already exist.
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     "itinerary_db"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
}

NEW_POIS = [
    # ── THAILAND — food (was critically under-represented) ───────────
    ("Or Tor Kor Market",               "food", "Premium fresh market with top-quality Thai produce and ready-to-eat dishes.",                                 "Bangkok",              "Thailand",    "medium", "relaxing"),
    ("Yaowarat Road (Chinatown)",        "food", "Bangkok's lively Chinatown strip famous for dim sum, seafood, and street snacks.",                           "Bangkok",              "Thailand",    "low",    "relaxing"),
    ("Asiatique The Riverfront",         "food", "Riverside night bazaar with diverse restaurants, craft beer, and Thai cuisine.",                             "Bangkok",              "Thailand",    "medium", "relaxing"),
    ("Nimman Road Restaurants",          "food", "Trendy Chiang Mai street lined with cafes, Thai fusion, and specialty coffee.",                              "Chiang Mai",           "Thailand",    "medium", "relaxing"),
    ("Hua Hin Night Market",             "food", "Relaxed seaside night market with fresh seafood and local Thai street food.",                                "Hua Hin",              "Thailand",    "low",    "relaxing"),
    ("Phuket Weekend Market (Naka)",     "food", "Local favourite for grilled seafood, mango sticky rice, and Thai desserts.",                                 "Phuket",               "Thailand",    "low",    "relaxing"),
    ("Chatuchak Weekend Market Food",    "food", "Massive food section inside Thailand's largest market — try boat noodles and pad thai.",                     "Bangkok",              "Thailand",    "low",    "adventure"),
    ("Ratchada Train Night Market",      "food", "Colourful photogenic night market with street food, clothes, and cocktails.",                               "Bangkok",              "Thailand",    "low",    "adventure"),
    ("Khao San Road Food Stalls",        "food", "Backpacker hub with pad thai, mango sticky rice, and international bites.",                                 "Bangkok",              "Thailand",    "low",    "adventure"),
    ("Chiang Mai Sunday Walking Street", "food", "Weekly street fair with northern Thai specialties like khao soi and sai oua sausage.",                      "Chiang Mai",           "Thailand",    "low",    "cultural"),
    ("Blue Elephant Restaurant",         "food", "Upscale Thai royal cuisine in a beautifully restored colonial mansion.",                                    "Bangkok",              "Thailand",    "high",   "relaxing"),
    ("Gaggan Anand",                     "food", "World-renowned progressive Indian-Thai restaurant, one of Asia's best.",                                    "Bangkok",              "Thailand",    "high",   "relaxing"),

    # ── MALAYSIA — food expansion ────────────────────────────────────
    ("Jalan Alor Food Street",           "food", "Kuala Lumpur's most famous outdoor food street — bustling with hawker stalls at night.",                    "Kuala Lumpur",         "Malaysia",    "low",    "relaxing"),
    ("Gurney Drive Hawker Centre",       "food", "Penang's premier seafront hawker centre for char kway teow and assam laksa.",                               "George Town",          "Malaysia",    "low",    "relaxing"),
    ("Batu Ferringhi Night Market",      "food", "Beachside night market with satay, grilled seafood, and fresh fruit.",                                      "Penang",               "Malaysia",    "low",    "relaxing"),
    ("Madam Kwan's",                     "food", "Popular Malaysian restaurant known for nasi lemak and signature beef rendang.",                             "Kuala Lumpur",         "Malaysia",    "medium", "relaxing"),
    ("Hutong Food Court KLCC",           "food", "Air-conditioned hawker hall beneath the Petronas Towers with all Malaysian classics.",                      "Kuala Lumpur",         "Malaysia",    "medium", "relaxing"),
    ("Yut Kee Kopitiam",                 "food", "Heritage coffeehouse serving Hainanese chicken chop and kaya toast since 1928.",                           "Kuala Lumpur",         "Malaysia",    "low",    "cultural"),
    ("Melaka Jonker Walk",               "food", "Historic night market in UNESCO Melaka with Nyonya snacks and durian cendol.",                              "Melaka",               "Malaysia",    "low",    "cultural"),
    ("Penang Famous Teochew Chendul",    "food", "Iconic dessert stall serving Malaysia's best chendul since 1936.",                                         "George Town",          "Malaysia",    "low",    "relaxing"),

    # ── INDONESIA — food expansion ───────────────────────────────────
    ("Seminyak Food Trail",              "food", "Bali's hippest dining strip with beach clubs, warungs, and international cafes.",                           "Bali",                 "Indonesia",   "medium", "relaxing"),
    ("Pasar Badung",                     "food", "Bali's largest traditional market — taste fresh jamu, sate lilit, and Balinese rice dishes.",               "Denpasar, Bali",       "Indonesia",   "low",    "relaxing"),
    ("Ubud Food Festival Area",          "food", "Ubud's artisan food scene with organic cafes, cooking classes, and farm-to-table dining.",                  "Ubud, Bali",           "Indonesia",   "medium", "relaxing"),
    ("Jalan Sabang Food Street",         "food", "Central Jakarta street packed with warung stalls serving nasi goreng and soto.",                            "Jakarta",              "Indonesia",   "low",    "relaxing"),
    ("Kota Tua Food Alley",              "food", "Jakarta's Old Town neighbourhood with colonial-era bakeries and kerak telor vendors.",                      "Jakarta",              "Indonesia",   "low",    "cultural"),
    ("Locavore Restaurant",              "food", "Award-winning Ubud fine dining showcasing hyper-local Balinese ingredients.",                               "Ubud, Bali",           "Indonesia",   "high",   "relaxing"),

    # ── SINGAPORE — food expansion ───────────────────────────────────
    ("Maxwell Food Centre",              "food", "Beloved hawker centre home to Tian Tian Hainanese chicken rice and popiah.",                               "Chinatown",            "Singapore",   "low",    "relaxing"),
    ("Lau Pa Sat Festival Market",       "food", "Victorian cast-iron market turned hawker centre — famous for satay after 7 pm.",                           "Singapore",            "Singapore",   "low",    "relaxing"),
    ("Tiong Bahru Bakery",               "food", "Iconic Singapore bakery with kouign-amann and specialty coffee in a heritage shophouse.",                   "Tiong Bahru",          "Singapore",   "medium", "relaxing"),
    ("Candlenut Restaurant",             "food", "World's first Michelin-starred Peranakan restaurant with heritage Nyonya recipes.",                        "Singapore",            "Singapore",   "high",   "relaxing"),
    ("Old Airport Road Food Centre",     "food", "One of Singapore's oldest hawker centres with legendary char kway teow and rojak.",                        "Singapore",            "Singapore",   "low",    "relaxing"),
    ("Hawker Chan",                      "food", "World's cheapest Michelin-star meal — soya sauce chicken rice from $3.",                                   "Singapore",            "Singapore",   "low",    "relaxing"),
    ("Dempsey Hill Restaurant Row",      "food", "Lush colonial estate converted into upscale restaurants and wine bars.",                                    "Singapore",            "Singapore",   "high",   "relaxing"),
    ("Tekka Centre",                     "food", "Little India's bustling wet market and hawker centre with roti prata and biryani.",                         "Little India",         "Singapore",   "low",    "cultural"),

    # ── PHILIPPINES — food expansion ─────────────────────────────────
    ("Mercato Centrale BGC",             "food", "Weekend night market in Bonifacio Global City with artisanal Filipino street food.",                        "Taguig",               "Philippines", "medium", "relaxing"),
    ("Rico's Lechon Cebu",               "food", "Cebu's legendary slow-roasted pig — crispy skin and juicy meat, a must-eat.",                              "Cebu City",            "Philippines", "low",    "relaxing"),
    ("Salcedo Saturday Market",          "food", "Makati's premium weekend market with artisanal Filipino produce and street food.",                          "Makati",               "Philippines", "medium", "relaxing"),
    ("Larsian Barbecue",                 "food", "Cebu open-air grill market open late into the night — isaw, pork belly, and seafood.",                     "Cebu City",            "Philippines", "low",    "relaxing"),
    ("Toyo Eatery",                      "food", "Manila's acclaimed modern Filipino restaurant championing local ingredients.",                              "Makati",               "Philippines", "high",   "relaxing"),
    ("Dampa Seafood Market",             "food", "Choose your fresh seafood and have it cooked to order at stalls around the market.",                        "Pasay",                "Philippines", "medium", "relaxing"),

    # ── BRUNEI — food expansion ──────────────────────────────────────
    ("Kianggeh Tamu Market",             "food", "Morning market along the river selling fresh local produce and traditional Bruneian snacks.",               "Bandar Seri Begawan",  "Brunei",      "low",    "relaxing"),
    ("Pasar Gadong Night Market",        "food", "Popular evening market with ambuyat, soto, and Malay grilled meats.",                                      "Gadong",               "Brunei",      "low",    "relaxing"),
    ("Seri Damai Restaurant",            "food", "Waterfront restaurant serving traditional Bruneian seafood and rice dishes.",                               "Bandar Seri Begawan",  "Brunei",      "medium", "relaxing"),
    ("Pondok Sari Wangi",                "food", "Local favourite for nasi katok — Brunei's simple iconic rice-and-chicken dish.",                           "Bandar Seri Begawan",  "Brunei",      "low",    "relaxing"),
]

def run():
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()
    inserted = 0
    skipped  = 0
    for row in NEW_POIS:
        name, category, description, location, country, budget_level, travel_style = row
        cur.execute("SELECT 1 FROM poi WHERE name = %s AND country = %s", (name, country))
        if cur.fetchone():
            skipped += 1
            continue
        cur.execute(
            "INSERT INTO poi (name, category, description, location, country, budget_level, travel_style) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            row,
        )
        inserted += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"Done — inserted {inserted} new POIs, skipped {skipped} already-existing.")

if __name__ == "__main__":
    run()
