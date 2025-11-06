"""
Realistic merchant database organized by spending categories and personas.
This provides real merchant names that match actual spending patterns.
"""

# Streaming Services (Subscription-Heavy Persona)
STREAMING_SERVICES = [
    {"name": "Netflix", "category": "Entertainment/Streaming Services", "amount_range": [9.99, 22.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Hulu", "category": "Entertainment/Streaming Services", "amount_range": [7.99, 17.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Disney Plus", "category": "Entertainment/Streaming Services", "amount_range": [10.99, 13.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Spotify", "category": "Entertainment/Streaming Services", "amount_range": [9.99, 16.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Apple Music", "category": "Entertainment/Streaming Services", "amount_range": [9.99, 15.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "YouTube Premium", "category": "Entertainment/Streaming Services", "amount_range": [13.99, 13.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Amazon Prime Video", "category": "Entertainment/Streaming Services", "amount_range": [8.99, 14.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "HBO Max", "category": "Entertainment/Streaming Services", "amount_range": [9.99, 15.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Paramount Plus", "category": "Entertainment/Streaming Services", "amount_range": [5.99, 11.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Peacock", "category": "Entertainment/Streaming Services", "amount_range": [5.99, 11.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Crunchyroll", "category": "Entertainment/Streaming Services", "amount_range": [7.99, 9.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Max", "category": "Entertainment/Streaming Services", "amount_range": [9.99, 15.99], "payment_channels": ["online"], "type": "online_only"},
]

# Food Delivery Apps (Foodie/High Utilization Personas)
FOOD_DELIVERY = [
    {"name": "DoorDash", "category": "Food & Drink/Fast Food", "amount_range": [15, 45], "payment_channels": ["online", "mobile"], "type": "online_only"},
    {"name": "Uber Eats", "category": "Food & Drink/Fast Food", "amount_range": [15, 45], "payment_channels": ["online", "mobile"], "type": "online_only"},
    {"name": "Grubhub", "category": "Food & Drink/Fast Food", "amount_range": [15, 45], "payment_channels": ["online", "mobile"], "type": "online_only"},
    {"name": "Postmates", "category": "Food & Drink/Fast Food", "amount_range": [15, 45], "payment_channels": ["online", "mobile"], "type": "online_only"},
    {"name": "Instacart", "category": "Groceries/Food & Beverage Stores", "amount_range": [30, 120], "payment_channels": ["online", "mobile"], "type": "online_only"},
]

# Coffee Shops (Foodie/High Utilization)
COFFEE_SHOPS = [
    {"name": "Starbucks", "category": "Food & Drink/Coffee Shops", "amount_range": [4.50, 8.50], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Dunkin'", "category": "Food & Drink/Coffee Shops", "amount_range": [3.50, 7.50], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Peet's Coffee", "category": "Food & Drink/Coffee Shops", "amount_range": [4.00, 8.00], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Caribou Coffee", "category": "Food & Drink/Coffee Shops", "amount_range": [4.00, 8.00], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "The Coffee Bean", "category": "Food & Drink/Coffee Shops", "amount_range": [4.50, 8.50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Blue Bottle Coffee", "category": "Food & Drink/Coffee Shops", "amount_range": [5.00, 9.00], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
]

# Fast Food Chains (Foodie/High Utilization)
FAST_FOOD = [
    {"name": "McDonald's", "category": "Food & Drink/Fast Food", "amount_range": [8, 25], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Burger King", "category": "Food & Drink/Fast Food", "amount_range": [8, 25], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Taco Bell", "category": "Food & Drink/Fast Food", "amount_range": [7, 20], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Wendy's", "category": "Food & Drink/Fast Food", "amount_range": [8, 25], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Chick-fil-A", "category": "Food & Drink/Fast Food", "amount_range": [10, 30], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Subway", "category": "Food & Drink/Fast Food", "amount_range": [7, 20], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Chipotle", "category": "Food & Drink/Fast Food", "amount_range": [12, 18], "payment_channels": ["in_store", "contactless", "mobile"], "type": "national_chain"},
    {"name": "Five Guys", "category": "Food & Drink/Fast Food", "amount_range": [12, 30], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Shake Shack", "category": "Food & Drink/Fast Food", "amount_range": [10, 25], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "In-N-Out Burger", "category": "Food & Drink/Fast Food", "amount_range": [8, 20], "payment_channels": ["in_store", "contactless"], "type": "regional"},
]

# Casual Dining Restaurants (Foodie/High Utilization)
CASUAL_DINING = [
    {"name": "Olive Garden", "category": "Food & Drink/Restaurants", "amount_range": [25, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Applebee's", "category": "Food & Drink/Restaurants", "amount_range": [20, 50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Red Lobster", "category": "Food & Drink/Restaurants", "amount_range": [30, 70], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Cheesecake Factory", "category": "Food & Drink/Restaurants", "amount_range": [30, 80], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "TGI Friday's", "category": "Food & Drink/Restaurants", "amount_range": [25, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Buffalo Wild Wings", "category": "Food & Drink/Restaurants", "amount_range": [25, 55], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Outback Steakhouse", "category": "Food & Drink/Restaurants", "amount_range": [30, 70], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Texas Roadhouse", "category": "Food & Drink/Restaurants", "amount_range": [30, 70], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
]

# Bars & Pubs (High Utilization)
BARS_PUBS = [
    {"name": "Buffalo Wild Wings", "category": "Food & Drink/Bars & Pubs", "amount_range": [20, 50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "TGI Friday's", "category": "Food & Drink/Bars & Pubs", "amount_range": [20, 50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Applebees", "category": "Food & Drink/Bars & Pubs", "amount_range": [20, 50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Chili's", "category": "Food & Drink/Bars & Pubs", "amount_range": [20, 50], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
]

# Gym Memberships (Subscription-Heavy)
GYM_MEMBERSHIPS = [
    {"name": "Planet Fitness", "category": "Health & Fitness/Gym Memberships", "amount_range": [10, 24.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "24 Hour Fitness", "category": "Health & Fitness/Gym Memberships", "amount_range": [30, 60], "payment_channels": ["online"], "type": "online_only"},
    {"name": "LA Fitness", "category": "Health & Fitness/Gym Memberships", "amount_range": [29.99, 49.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Gold's Gym", "category": "Health & Fitness/Gym Memberships", "amount_range": [25, 50], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Equinox", "category": "Health & Fitness/Gym Memberships", "amount_range": [150, 200], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Crunch Fitness", "category": "Health & Fitness/Gym Memberships", "amount_range": [9.99, 24.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Anytime Fitness", "category": "Health & Fitness/Gym Memberships", "amount_range": [41, 50], "payment_channels": ["online"], "type": "online_only"},
]

# Software/Cloud Services (Subscription-Heavy)
SOFTWARE_SUBSCRIPTIONS = [
    {"name": "Adobe Creative Cloud", "category": "Software/Cloud Services", "amount_range": [20.99, 54.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Microsoft 365", "category": "Software/Cloud Services", "amount_range": [6.99, 22.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Dropbox", "category": "Software/Cloud Services", "amount_range": [9.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Google Drive", "category": "Software/Cloud Services", "amount_range": [1.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "iCloud", "category": "Software/Cloud Services", "amount_range": [0.99, 9.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "OneDrive", "category": "Software/Cloud Services", "amount_range": [1.99, 9.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Zoom", "category": "Software/Cloud Services", "amount_range": [14.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Slack", "category": "Software/Cloud Services", "amount_range": [7.25, 12.50], "payment_channels": ["online"], "type": "online_only"},
]

# Grocery Stores (Savings Builder - cooks at home)
GROCERY_STORES = [
    {"name": "Whole Foods Market", "category": "Groceries/Food & Beverage Stores", "amount_range": [50, 150], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Trader Joe's", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 100], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Kroger", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"], "type": "regional"},
    {"name": "Safeway", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Target", "category": "Groceries/Food & Beverage Stores", "amount_range": [30, 100], "payment_channels": ["in_store", "contactless", "online"], "type": "national_chain"},
    {"name": "Walmart", "category": "Groceries/Food & Beverage Stores", "amount_range": [30, 100], "payment_channels": ["in_store", "contactless", "online"], "type": "national_chain"},
    {"name": "Costco", "category": "Groceries/Food & Beverage Stores", "amount_range": [60, 200], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Publix", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"], "type": "regional"},
    {"name": "Albertsons", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"], "type": "regional"},
]

# Retail Stores (High Utilization - lots of shopping)
RETAIL_STORES = [
    {"name": "Amazon", "category": "Retail/Online Marketplace", "amount_range": [15, 200], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Target", "category": "Retail/Department Stores", "amount_range": [20, 150], "payment_channels": ["in_store", "contactless", "online"], "type": "national_chain"},
    {"name": "Walmart", "category": "Retail/Department Stores", "amount_range": [15, 150], "payment_channels": ["in_store", "contactless", "online"], "type": "national_chain"},
    {"name": "Best Buy", "category": "Retail/Electronics", "amount_range": [30, 500], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Home Depot", "category": "Retail/Home & Garden", "amount_range": [20, 300], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Lowe's", "category": "Retail/Home & Garden", "amount_range": [20, 300], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Macy's", "category": "Retail/Clothing", "amount_range": [30, 200], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Nordstrom", "category": "Retail/Clothing", "amount_range": [50, 300], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Old Navy", "category": "Retail/Clothing", "amount_range": [20, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
]

# Gas Stations (Variable Income - frequent small purchases)
GAS_STATIONS = [
    {"name": "Shell", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Exxon", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "BP", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Chevron", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "Mobil", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
    {"name": "7-Eleven", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store", "contactless"], "type": "national_chain"},
]

# Utilities (All personas)
UTILITIES = [
    {"name": "Pacific Gas & Electric", "category": "Bills & Utilities/Utilities", "amount_range": [80, 200], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Southern California Edison", "category": "Bills & Utilities/Utilities", "amount_range": [80, 200], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Con Edison", "category": "Bills & Utilities/Utilities", "amount_range": [80, 200], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Duke Energy", "category": "Bills & Utilities/Utilities", "amount_range": [80, 200], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "AT&T Internet", "category": "Bills & Utilities/Internet", "amount_range": [50, 100], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Comcast Xfinity", "category": "Bills & Utilities/Internet", "amount_range": [50, 100], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Verizon Fios", "category": "Bills & Utilities/Internet", "amount_range": [50, 100], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Spectrum", "category": "Bills & Utilities/Internet", "amount_range": [50, 100], "payment_channels": ["online", "other"], "type": "utility"},
]

# Mobile Carriers (All personas)
MOBILE_CARRIERS = [
    {"name": "Verizon Wireless", "category": "Bills & Utilities/Mobile Phone", "amount_range": [60, 120], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "AT&T Wireless", "category": "Bills & Utilities/Mobile Phone", "amount_range": [60, 120], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "T-Mobile", "category": "Bills & Utilities/Mobile Phone", "amount_range": [60, 120], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Sprint", "category": "Bills & Utilities/Mobile Phone", "amount_range": [60, 120], "payment_channels": ["online", "other"], "type": "utility"},
]

# Rideshare Services (All personas, frequent use)
RIDESHARE_SERVICES = [
    {"name": "Uber", "category": "Transport/Rideshare", "amount_range": [10, 50], "payment_channels": ["mobile", "online"], "type": "online_only"},
    {"name": "Lyft", "category": "Transport/Rideshare", "amount_range": [10, 50], "payment_channels": ["mobile", "online"], "type": "online_only"},
]

# Parking Services (All personas)
PARKING_SERVICES = [
    {"name": "ParkMobile", "category": "Transport/Parking", "amount_range": [3, 25], "payment_channels": ["mobile", "online"], "type": "online_only"},
    {"name": "SpotHero", "category": "Transport/Parking", "amount_range": [5, 30], "payment_channels": ["mobile", "online"], "type": "online_only"},
    {"name": "PayByPhone", "category": "Transport/Parking", "amount_range": [3, 20], "payment_channels": ["mobile", "online"], "type": "online_only"},
]

# Public Transit (All personas)
PUBLIC_TRANSIT = [
    {"name": "Metro", "category": "Transport/Public Transit", "amount_range": [2, 15], "payment_channels": ["contactless", "mobile"], "type": "regional"},
    {"name": "BART", "category": "Transport/Public Transit", "amount_range": [2, 15], "payment_channels": ["contactless", "mobile"], "type": "regional"},
    {"name": "MTA", "category": "Transport/Public Transit", "amount_range": [2, 15], "payment_channels": ["contactless", "mobile"], "type": "regional"},
    {"name": "Metro Transit", "category": "Transport/Public Transit", "amount_range": [2, 15], "payment_channels": ["contactless", "mobile"], "type": "regional"},
    {"name": "Transit Card", "category": "Transport/Public Transit", "amount_range": [2, 15], "payment_channels": ["contactless", "mobile"], "type": "regional"},
]

# Office Supply Stores (Retail)
OFFICE_SUPPLIES = [
    {"name": "Staples", "category": "Retail/Office Supplies", "amount_range": [10, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Office Depot", "category": "Retail/Office Supplies", "amount_range": [10, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "OfficeMax", "category": "Retail/Office Supplies", "amount_range": [10, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Amazon", "category": "Retail/Office Supplies", "amount_range": [5, 80], "payment_channels": ["online"], "type": "online_only"},
]

# Pet Stores (Retail)
PET_STORES = [
    {"name": "Petco", "category": "Retail/Pet Stores", "amount_range": [20, 150], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "PetSmart", "category": "Retail/Pet Stores", "amount_range": [20, 150], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Chewy", "category": "Retail/Pet Stores", "amount_range": [25, 120], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Amazon", "category": "Retail/Pet Stores", "amount_range": [15, 100], "payment_channels": ["online"], "type": "online_only"},
]

# Movie Rentals/Entertainment (Entertainment)
MOVIE_RENTALS = [
    {"name": "Apple iTunes", "category": "Entertainment/Movie Rentals", "amount_range": [4.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Amazon Prime Video", "category": "Entertainment/Movie Rentals", "amount_range": [3.99, 14.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Google Play Movies", "category": "Entertainment/Movie Rentals", "amount_range": [3.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "FandangoNOW", "category": "Entertainment/Movie Rentals", "amount_range": [5.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Vudu", "category": "Entertainment/Movie Rentals", "amount_range": [4.99, 19.99], "payment_channels": ["online"], "type": "online_only"},
]

# Subscription Boxes (Retail/Entertainment)
SUBSCRIPTION_BOXES = [
    {"name": "Birchbox", "category": "Retail/Subscription Boxes", "amount_range": [10, 15], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Ipsy", "category": "Retail/Subscription Boxes", "amount_range": [12, 25], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Blue Apron", "category": "Retail/Subscription Boxes", "amount_range": [50, 80], "payment_channels": ["online"], "type": "online_only"},
    {"name": "HelloFresh", "category": "Retail/Subscription Boxes", "amount_range": [50, 80], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Stitch Fix", "category": "Retail/Subscription Boxes", "amount_range": [20, 50], "payment_channels": ["online"], "type": "online_only"},
    {"name": "FabFitFun", "category": "Retail/Subscription Boxes", "amount_range": [49.99, 54.99], "payment_channels": ["online"], "type": "online_only"},
]

# Concert Venues (Entertainment)
CONCERT_VENUES = [
    {"name": "Ticketmaster", "category": "Entertainment/Concerts", "amount_range": [50, 300], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Live Nation", "category": "Entertainment/Concerts", "amount_range": [50, 300], "payment_channels": ["online"], "type": "online_only"},
    {"name": "StubHub", "category": "Entertainment/Concerts", "amount_range": [60, 400], "payment_channels": ["online"], "type": "online_only"},
    {"name": "AXS", "category": "Entertainment/Concerts", "amount_range": [50, 300], "payment_channels": ["online"], "type": "online_only"},
    {"name": "Vivid Seats", "category": "Entertainment/Concerts", "amount_range": [50, 350], "payment_channels": ["online"], "type": "online_only"},
]

# Discount Outlets (Retail)
DISCOUNT_OUTLETS = [
    {"name": "T.J. Maxx", "category": "Retail/Discount Outlets", "amount_range": [15, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Marshalls", "category": "Retail/Discount Outlets", "amount_range": [15, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Ross", "category": "Retail/Discount Outlets", "amount_range": [10, 80], "payment_channels": ["in_store"], "type": "national_chain"},
    {"name": "Burlington", "category": "Retail/Discount Outlets", "amount_range": [15, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "HomeGoods", "category": "Retail/Discount Outlets", "amount_range": [20, 150], "payment_channels": ["in_store"], "type": "national_chain"},
]

# Craft/Hobby Stores (Retail)
CRAFT_STORES = [
    {"name": "Michaels", "category": "Retail/Crafts & Hobbies", "amount_range": [10, 80], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Joann Fabrics", "category": "Retail/Crafts & Hobbies", "amount_range": [10, 100], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Hobby Lobby", "category": "Retail/Crafts & Hobbies", "amount_range": [10, 80], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Amazon", "category": "Retail/Crafts & Hobbies", "amount_range": [5, 60], "payment_channels": ["online"], "type": "online_only"},
]

# Luxury Boutiques (Retail)
LUXURY_BOUTIQUES = [
    {"name": "Saks Fifth Avenue", "category": "Retail/Luxury", "amount_range": [100, 500], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Neiman Marcus", "category": "Retail/Luxury", "amount_range": [100, 500], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Nordstrom", "category": "Retail/Luxury", "amount_range": [80, 400], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Bloomingdale's", "category": "Retail/Luxury", "amount_range": [80, 400], "payment_channels": ["in_store", "online"], "type": "national_chain"},
    {"name": "Bergdorf Goodman", "category": "Retail/Luxury", "amount_range": [150, 800], "payment_channels": ["in_store", "online"], "type": "national_chain"},
]

# Student Loan Servicers (Loan Payments)
STUDENT_LOAN_SERVICERS = [
    {"name": "Navient", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Great Lakes", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "FedLoan Servicing", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Nelnet", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "MOHELA", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
    {"name": "Aidvantage", "category": "GENERAL_MERCHANDISE/LOAN_PAYMENT", "amount_range": [100, 500], "payment_channels": ["online", "other"], "type": "utility"},
]

# Persona-specific merchant mappings
PERSONA_MERCHANTS = {
    1: {  # High Utilization
        "primary": FAST_FOOD + CASUAL_DINING + BARS_PUBS + RETAIL_STORES + FOOD_DELIVERY,
        "secondary": COFFEE_SHOPS + GAS_STATIONS + UTILITIES + MOBILE_CARRIERS + RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT,
        "frequency_multiplier": 1.5,  # More frequent transactions
    },
    2: {  # Variable Income Budgeter
        "primary": GROCERY_STORES + GAS_STATIONS + UTILITIES + MOBILE_CARRIERS,
        "secondary": FAST_FOOD + COFFEE_SHOPS + RETAIL_STORES + RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT,
        "frequency_multiplier": 0.8,  # Less frequent, more variable
    },
    3: {  # Subscription-Heavy
        "primary": STREAMING_SERVICES + SOFTWARE_SUBSCRIPTIONS + GYM_MEMBERSHIPS,
        "secondary": UTILITIES + MOBILE_CARRIERS + GROCERY_STORES + RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT,
        "frequency_multiplier": 1.2,  # Regular recurring charges
    },
    4: {  # Savings Builder
        "primary": GROCERY_STORES + UTILITIES + MOBILE_CARRIERS,
        "secondary": RETAIL_STORES + COFFEE_SHOPS + GAS_STATIONS + RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT,
        "frequency_multiplier": 0.7,  # Less frequent spending
    },
    5: {  # Custom/Balanced
        "primary": GROCERY_STORES + FAST_FOOD + RETAIL_STORES + STREAMING_SERVICES[:3],
        "secondary": COFFEE_SHOPS + GAS_STATIONS + UTILITIES + MOBILE_CARRIERS + RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT,
        "frequency_multiplier": 1.0,  # Normal frequency
    },
}

# Get merchants for a specific persona
def get_merchants_for_persona(persona_id: int):
    """Get merchant list for a specific persona."""
    if persona_id not in PERSONA_MERCHANTS:
        persona_id = 5  # Default to balanced
    return PERSONA_MERCHANTS[persona_id]

# Get merchants by category
def get_merchants_by_category(category: str):
    """Get all merchants matching a category.
    
    Args:
        category: Category string like "Entertainment/Streaming Services" or "Food & Drink/Fast Food"
    
    Returns:
        List of merchants matching the category
    """
    all_merchants = (
        STREAMING_SERVICES + FOOD_DELIVERY + COFFEE_SHOPS + FAST_FOOD +
        CASUAL_DINING + BARS_PUBS + GYM_MEMBERSHIPS + SOFTWARE_SUBSCRIPTIONS +
        GROCERY_STORES + RETAIL_STORES + GAS_STATIONS + UTILITIES + MOBILE_CARRIERS +
        RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT +
        OFFICE_SUPPLIES + PET_STORES + MOVIE_RENTALS + SUBSCRIPTION_BOXES +
        CONCERT_VENUES + DISCOUNT_OUTLETS + CRAFT_STORES + LUXURY_BOUTIQUES +
        STUDENT_LOAN_SERVICERS
    )
    # Match if category is contained in merchant category (e.g., "Streaming Services" matches "Entertainment/Streaming Services")
    # Also handle partial matches (e.g., "Transport" matches "Transport/Fuel", "Transport/Rideshare", etc.)
    category_lower = category.lower()
    matched = []
    category_parts = category_lower.split('/')
    primary_category = category_parts[0].strip()
    secondary_category = category_parts[1].strip() if len(category_parts) > 1 else None
    
    for m in all_merchants:
        merchant_cat = m["category"].lower()
        merchant_parts = merchant_cat.split('/')
        merchant_primary = merchant_parts[0].strip()
        merchant_secondary = merchant_parts[1].strip() if len(merchant_parts) > 1 else None
        
        # If both have secondary categories, they must match (exact or substring match)
        if secondary_category and merchant_secondary:
            if primary_category == merchant_primary:
                # Check if secondary categories match (exact or substring)
                if secondary_category in merchant_secondary or merchant_secondary in secondary_category:
                    matched.append(m)
        # If only one has secondary category, check if primary matches and secondary is compatible
        elif secondary_category and not merchant_secondary:
            # Looking for specific subcategory but merchant only has primary - skip unless it's a general category
            if primary_category == merchant_primary:
                # For general retail/entertainment/transport, allow fallback
                if primary_category in ["retail", "entertainment", "transport"]:
                    matched.append(m)
        elif not secondary_category and merchant_secondary:
            # Looking for primary category only - match if primary matches
            if primary_category == merchant_primary:
                matched.append(m)
        else:
            # Both are primary categories only - exact match
            if primary_category == merchant_primary:
                matched.append(m)
    
    return matched

# Get all merchants
def get_all_merchants():
    """Get all available merchants."""
    return (
        STREAMING_SERVICES + FOOD_DELIVERY + COFFEE_SHOPS + FAST_FOOD +
        CASUAL_DINING + BARS_PUBS + GYM_MEMBERSHIPS + SOFTWARE_SUBSCRIPTIONS +
        GROCERY_STORES + RETAIL_STORES + GAS_STATIONS + UTILITIES + MOBILE_CARRIERS +
        RIDESHARE_SERVICES + PARKING_SERVICES + PUBLIC_TRANSIT +
        OFFICE_SUPPLIES + PET_STORES + MOVIE_RENTALS + SUBSCRIPTION_BOXES +
        CONCERT_VENUES + DISCOUNT_OUTLETS + CRAFT_STORES + LUXURY_BOUTIQUES +
        STUDENT_LOAN_SERVICERS
    )

