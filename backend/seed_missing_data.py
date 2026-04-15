"""
seed_missing_data.py
Fills every zero-result gap found in the coverage audit:
  - Removes France and United States (leftover sample data, not offered countries)
  - Adds shopping POIs for: Brunei, Indonesia, Malaysia, Philippines, Singapore
  - Adds history POIs for:  Singapore (was 0)
  - Adds adventure POIs for: Malaysia (was 0)
  - Adds family POIs for:   all 7 core countries (was 0 everywhere)
  - Adds high-budget POIs for: Brunei, Malaysia (was 0)

Safe to re-run — skips rows where (name, country) already exist.
"""
import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = dict(
    dbname   = os.getenv("DB_NAME",     "itinerary_db"),
    user     = os.getenv("DB_USER",     "postgres"),
    password = os.getenv("DB_PASSWORD", ""),
    host     = os.getenv("DB_HOST",     "localhost"),
    port     = int(os.getenv("DB_PORT", 5432)),
)

NEW_POIS = [
    # ══════════════════════════════════════════════════════════
    #  SHOPPING — missing for Brunei, Indonesia, Malaysia,
    #             Philippines, Singapore
    # ══════════════════════════════════════════════════════════

    # Brunei
    ("Gadong Commercial Complex",    "shopping", "Brunei's main shopping hub with local boutiques, food court, and a night market.",         "Gadong",              "Brunei",      "medium", "relaxing"),
    ("Yayasan Sultan Complex",       "shopping", "Elegant riverfront mall near the mosque with local and international brands.",             "Bandar Seri Begawan", "Brunei",      "medium", "relaxing"),
    ("Tamu Kianggeh Craft Stalls",   "shopping", "Riverside stalls selling traditional Brunei handicrafts, baskets, and batik.",             "Bandar Seri Begawan", "Brunei",      "low",    "cultural"),
    ("Hua Ho Manggis Mall",          "shopping", "Popular local department store chain with affordable fashion and household goods.",         "Bandar Seri Begawan", "Brunei",      "low",    "relaxing"),

    # Indonesia
    ("Grand Indonesia Mall",         "shopping", "Jakarta's premier luxury mall with international brands, dining, and entertainment.",      "Jakarta",             "Indonesia",   "high",   "relaxing"),
    ("Beachwalk Shopping Centre",    "shopping", "Stylish open-air mall in Kuta with sea views, fashion, and beachside dining.",             "Bali",                "Indonesia",   "medium", "relaxing"),
    ("Malioboro Street",             "shopping", "Yogyakarta's iconic shopping street for batik, silver jewellery, and local street food.",  "Yogyakarta",          "Indonesia",   "low",    "cultural"),
    ("Pasar Seni Ancol",             "shopping", "Jakarta's arts market with live crafts demos, batik painting, and local souvenirs.",       "Jakarta",             "Indonesia",   "low",    "adventure"),
    ("Seminyak Square",              "shopping", "Bali's boutique shopping street with surf brands, swimwear, and designer homewares.",      "Bali",                "Indonesia",   "medium", "relaxing"),

    # Malaysia
    ("Pavilion Kuala Lumpur",        "shopping", "Flagship luxury mall in the heart of Bukit Bintang with designer labels and fine dining.", "Kuala Lumpur",        "Malaysia",    "high",   "relaxing"),
    ("Suria KLCC",                   "shopping", "Premium mall at the base of the Petronas Towers with 400+ stores.",                       "Kuala Lumpur",        "Malaysia",    "high",   "relaxing"),
    ("Central Market KL",            "shopping", "Heritage art-deco market showcasing Malaysian crafts, batik, and antiques.",              "Kuala Lumpur",        "Malaysia",    "low",    "cultural"),
    ("Sunway Pyramid",               "shopping", "Egyptian-themed mega-mall with an ice rink, cinemas, and 700+ outlets.",                  "Selangor",            "Malaysia",    "medium", "family"),
    ("Penang Times Square",          "shopping", "Penang's modern mall with local fashion brands, food court, and entertainment.",          "George Town",         "Malaysia",    "medium", "relaxing"),
    ("Pasar Seni (Central Market)",  "shopping", "KL's oldest market converted into a cultural arts bazaar for local crafts.",              "Kuala Lumpur",        "Malaysia",    "low",    "relaxing"),

    # Philippines
    ("SM Mall of Asia",              "shopping", "One of the largest malls in Asia with bay views, shops, skating rink, and dining.",       "Pasay",               "Philippines", "medium", "relaxing"),
    ("Divisoria Market",             "shopping", "Manila's famous wholesale district for ultra-cheap fashion, textiles, and novelties.",    "Manila",              "Philippines", "low",    "adventure"),
    ("Greenhills Shopping Centre",   "shopping", "Upscale mall known for pearl jewellery, pirated DVDs, and local fashion.",               "Mandaluyong",         "Philippines", "medium", "relaxing"),
    ("Ayala Center Cebu",            "shopping", "Cebu's premier lifestyle mall with fashion, restaurants, and weekend events.",            "Cebu City",           "Philippines", "medium", "relaxing"),
    ("Ukay-Ukay Tiangge",            "shopping", "Thrift markets across the Metro selling second-hand fashion and hidden gems.",            "Manila",              "Philippines", "low",    "adventure"),

    # Singapore
    ("ION Orchard",                  "shopping", "Iconic glass tower mall on Orchard Road — Louis Vuitton to H&M across 8 floors.",        "Orchard",             "Singapore",   "high",   "relaxing"),
    ("VivoCity",                     "shopping", "Singapore's largest mall with rooftop park, cinema, and Sentosa access.",                "HarbourFront",        "Singapore",   "medium", "relaxing"),
    ("Bugis Junction",               "shopping", "Covered streetscape mall blending heritage shophouses with modern retail.",              "Bugis",               "Singapore",   "medium", "relaxing"),
    ("Jewel Changi Airport",         "shopping", "World's tallest indoor waterfall surrounded by gardens, shops, and restaurants.",         "Changi",              "Singapore",   "medium", "family"),
    ("Mustafa Centre",               "shopping", "24-hour megastore in Little India — electronics, groceries, gold, and more.",            "Little India",        "Singapore",   "low",    "adventure"),
    ("Orchard Road Stretch",         "shopping", "Singapore's premier retail boulevard lined with malls, boutiques, and flagship stores.", "Orchard",             "Singapore",   "medium", "relaxing"),

    # ══════════════════════════════════════════════════════════
    #  HISTORY — Singapore was at 0
    # ══════════════════════════════════════════════════════════
    ("National Museum of Singapore", "history",  "Singapore's oldest museum covering the nation's history from early settlements to today.", "Bras Basah",         "Singapore",   "medium", "cultural"),
    ("Fort Canning Park",            "history",  "14th-century royal Malay fort turned heritage park with WWII command bunker tours.",       "Singapore",          "Singapore",   "low",    "relaxing"),
    ("Asian Civilisations Museum",   "history",  "World-class museum tracing the cultural heritage of Asia's diverse civilisations.",       "Empress Place",       "Singapore",   "medium", "cultural"),
    ("Battlebox at Fort Canning",    "history",  "Wartime underground bunker where Allied commanders surrendered to Japan in 1942.",        "Singapore",           "Singapore",   "medium", "cultural"),
    ("Chinatown Heritage Centre",    "history",  "Immersive museum inside restored shophouses showing early Chinese immigrant life.",       "Chinatown",           "Singapore",   "medium", "cultural"),
    ("Malay Heritage Centre",        "history",  "Museum in the Sultan's royal compound showcasing Malay culture and history.",            "Kampong Glam",        "Singapore",   "low",    "cultural"),

    # ══════════════════════════════════════════════════════════
    #  ADVENTURE — Malaysia was at 0
    # ══════════════════════════════════════════════════════════
    ("Taman Negara National Park",   "nature",   "Malaysia's oldest rainforest — canopy walkway, river rapids, and jungle trekking.",      "Pahang",              "Malaysia",    "medium", "adventure"),
    ("Gopeng White Water Rafting",   "nature",   "Grade II–IV rapids on the Kampar River — one of Malaysia's best rafting spots.",        "Perak",               "Malaysia",    "medium", "adventure"),
    ("Penang Hill Hiking Trail",     "nature",   "Steep hike up Bukit Bendera with panoramic views over Penang island.",                  "George Town",         "Malaysia",    "low",    "adventure"),
    ("Pulau Perhentian",             "nature",   "Pristine islands off Terengganu coast with snorkelling, diving, and clear waters.",     "Terengganu",          "Malaysia",    "medium", "adventure"),
    ("Via Ferrata Mount Kinabalu",   "nature",   "World's highest via ferrata climb on the flanks of Borneo's tallest peak.",            "Sabah",               "Malaysia",    "high",   "adventure"),
    ("Batu Caves Climbing",          "nature",   "Sport climbing routes on Batu Caves limestone alongside the famous Hindu temples.",     "Selangor",            "Malaysia",    "low",    "adventure"),

    # ══════════════════════════════════════════════════════════
    #  FAMILY — missing across ALL 7 countries
    # ══════════════════════════════════════════════════════════

    # Brunei
    ("Jerudong Park Playground",     "nature",   "Brunei's free theme park with rides, bumper cars, and picnic lawns for families.",      "Jerudong",            "Brunei",      "low",    "family"),
    ("Taman Jubli Perak",            "nature",   "Riverside recreational park popular with families for picnics and cycling.",            "Bandar Seri Begawan", "Brunei",      "low",    "family"),
    ("Brunei Museum",                "history",  "Family-friendly national museum with natural history and Islamic art galleries.",       "Bandar Seri Begawan", "Brunei",      "low",    "family"),

    # Indonesia
    ("Taman Safari Bogor",           "nature",   "Drive-through safari park near Jakarta with over 2,500 animals across open enclosures.", "Bogor",              "Indonesia",   "medium", "family"),
    ("Bali Bird Park",               "nature",   "Award-winning aviary with 1,000 exotic birds including hornbills and birds of paradise.", "Batubulan, Bali",   "Indonesia",   "medium", "family"),
    ("Waterbom Bali",                "nature",   "Asia's best water park with slides, lazy river, and kids' splash zones.",               "Kuta, Bali",          "Indonesia",   "medium", "family"),
    ("Kidzania Jakarta",             "shopping", "Interactive city for kids where children role-play adult professions in mini buildings.","Jakarta",             "Indonesia",   "medium", "family"),

    # Japan
    ("teamLab Planets",              "nature",   "Immersive digital art museum — barefoot walk through water and mirror rooms.",          "Tokyo",               "Japan",       "medium", "family"),
    ("Tokyo Disneyland",             "nature",   "Japan's original Disney theme park with classic rides and Disney character parades.",   "Tokyo",               "Japan",       "high",   "family"),
    ("Osaka Aquarium Kaiyukan",      "nature",   "One of the world's largest aquariums featuring a whale shark as the centrepiece.",     "Osaka",               "Japan",       "medium", "family"),
    ("Nara Deer Park",               "nature",   "Free-roaming deer across a UNESCO park — feed 'bowing' deer next to ancient temples.", "Nara",                "Japan",       "low",    "family"),
    ("Ghibli Museum Mitaka",         "history",  "Enchanting museum dedicated to Studio Ghibli films — magical for kids and adults.",    "Tokyo",               "Japan",       "medium", "family"),

    # Malaysia
    ("Aquaria KLCC",                 "nature",   "Underwater tunnel aquarium beneath the Petronas Towers with sharks and giant rays.",   "Kuala Lumpur",        "Malaysia",    "medium", "family"),
    ("KL Bird Park",                 "nature",   "World's largest walk-in aviary with 3,000 free-flying birds in a rainforest setting.", "Kuala Lumpur",        "Malaysia",    "medium", "family"),
    ("Genting Skyworlds",            "nature",   "Malaysia's largest theme park in the highlands with rides for all ages.",             "Pahang",              "Malaysia",    "high",   "family"),
    ("Legoland Malaysia",            "nature",   "The first Legoland in Asia — rides, water park, and a Miniland of SE Asian landmarks.", "Johor Bahru",        "Malaysia",    "medium", "family"),

    # Philippines
    ("Star City Theme Park",         "nature",   "Manila amusement park with roller coasters, bumper cars, and carnival games.",        "Pasay",               "Philippines", "medium", "family"),
    ("Manila Ocean Park",            "nature",   "Oceanarium behind the Quirino Grandstand with shark and jellyfish tunnels.",          "Manila",              "Philippines", "medium", "family"),
    ("Mind Museum BGC",              "history",  "Interactive science museum with dinosaur exhibits, space gallery, and tech labs.",    "Taguig",              "Philippines", "medium", "family"),
    ("Enchanted Kingdom",            "nature",   "Philippines' biggest theme park with rollercoasters, shows, and themed zones.",      "Santa Rosa, Laguna",  "Philippines", "medium", "family"),

    # Singapore
    ("Universal Studios Singapore",  "nature",   "Southeast Asia's first Universal Studios — rides, shows, and themed zones.",          "Sentosa",             "Singapore",   "high",   "family"),
    ("Singapore Zoo",                "nature",   "Open-concept zoo famous for its Night Safari and Rainforest Wild exhibits.",          "Mandai",              "Singapore",   "medium", "family"),
    ("S.E.A. Aquarium",              "nature",   "One of the world's largest aquariums with 100,000 marine animals.",                  "Sentosa",             "Singapore",   "medium", "family"),
    ("Adventure Cove Waterpark",     "nature",   "Sentosa water park with a snorkelling lagoon and high-speed waterslides.",           "Sentosa",             "Singapore",   "medium", "family"),
    ("Science Centre Singapore",     "history",  "Hands-on science museum with 1,000 exhibits across 14 galleries.",                  "Jurong East",         "Singapore",   "low",    "family"),

    # Thailand
    ("Dream World Bangkok",          "nature",   "Bangkok's classic theme park with rollercoasters, snow town, and a fairy-tale castle.", "Pathum Thani",       "Thailand",    "medium", "family"),
    ("SEA LIFE Bangkok Ocean World", "nature",   "Massive aquarium under Siam Paragon with sharks, penguins, and an ocean tunnel.",    "Bangkok",             "Thailand",    "medium", "family"),
    ("Nong Nooch Tropical Garden",   "nature",   "Botanical garden and zoo with elephant shows and Thai cultural performances.",       "Pattaya",             "Thailand",    "medium", "family"),
    ("Elephant Nature Park",         "nature",   "Ethical elephant sanctuary in Chiang Mai — feed and bathe rescued elephants.",      "Chiang Mai",          "Thailand",    "medium", "family"),

    # ══════════════════════════════════════════════════════════
    #  HIGH BUDGET — Brunei and Malaysia were at 0
    # ══════════════════════════════════════════════════════════

    # Brunei
    ("The Empire Hotel Brunei",      "nature",   "Ultra-luxury beachfront resort with private pools, golf course, and fine dining.",   "Jerudong",            "Brunei",      "high",   "relaxing"),
    ("Rizqun International Hotel Dining", "food","Brunei's top hotel restaurant serving international and local cuisine.",             "Bandar Seri Begawan", "Brunei",      "high",   "relaxing"),
    ("Pantai Jerudong Beach Club",   "nature",   "Exclusive beach club with private cabanas, water sports, and ocean-view dining.",   "Jerudong",            "Brunei",      "high",   "relaxing"),

    # Malaysia
    ("Mandarin Oriental KL",         "food",     "Award-winning hotel restaurants with views over Petronas Towers and KLCC Park.",    "Kuala Lumpur",        "Malaysia",    "high",   "relaxing"),
    ("Resorts World Genting",        "nature",   "High-altitude highland resort complex with casino, theme park, and luxury hotels.", "Pahang",              "Malaysia",    "high",   "relaxing"),
    ("Four Seasons KL Dining",       "food",     "Rooftop bar and multiple fine-dining concepts in Kuala Lumpur's newest luxury tower.", "Kuala Lumpur",      "Malaysia",    "high",   "relaxing"),
]

def run():
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    # Remove leftover sample-only countries not offered in the chatbot
    cur.execute("DELETE FROM poi WHERE country IN ('France', 'United States')")
    removed = cur.rowcount
    print(f"Removed {removed} POIs for France / United States.")

    inserted = skipped = 0
    for row in NEW_POIS:
        name, *_, country, __, ___ = row  # unpack name and country cheaply
        name    = row[0]
        country = row[4]
        cur.execute("SELECT 1 FROM poi WHERE name=%s AND country=%s", (name, country))
        if cur.fetchone():
            skipped += 1
            continue
        cur.execute(
            "INSERT INTO poi (name, category, description, location, country, budget_level, travel_style) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)", row,
        )
        inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done — inserted {inserted} new POIs, skipped {skipped} duplicates.")

if __name__ == "__main__":
    run()
