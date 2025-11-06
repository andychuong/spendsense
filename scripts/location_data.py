"""
Location data for generating realistic, geographically-aware synthetic data.
Includes states, major cities, and some regional merchant chains.
"""

US_STATES_CITIES = {
    "Alabama": ["Birmingham", "Montgomery", "Huntsville", "Mobile"],
    "Alaska": ["Anchorage", "Fairbanks", "Juneau"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville"],
    "California": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins"],
    "Connecticut": ["Bridgeport", "New Haven", "Hartford"],
    "Delaware": ["Wilmington", "Dover"],
    "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon"],
    "Hawaii": ["Honolulu"],
    "Idaho": ["Boise"],
    "Illinois": ["Chicago", "Aurora", "Joliet", "Naperville"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville"],
    "Iowa": ["Des Moines", "Cedar Rapids"],
    "Kansas": ["Wichita", "Overland Park"],
    "Kentucky": ["Louisville", "Lexington"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport"],
    "Maine": ["Portland"],
    "Maryland": ["Baltimore", "Columbia"],
    "Massachusetts": ["Boston", "Worcester", "Springfield"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren"],
    "Minnesota": ["Minneapolis", "Saint Paul"],
    "Mississippi": ["Jackson"],
    "Missouri": ["Kansas City", "Saint Louis", "Springfield"],
    "Montana": ["Billings"],
    "Nebraska": ["Omaha", "Lincoln"],
    "Nevada": ["Las Vegas", "Henderson", "Reno"],
    "New Hampshire": ["Manchester"],
    "New Jersey": ["Newark", "Jersey City", "Paterson"],
    "New Mexico": ["Albuquerque"],
    "New York": ["New York City", "Buffalo", "Rochester", "Yonkers"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
    "North Dakota": ["Fargo"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "Oklahoma": ["Oklahoma City", "Tulsa"],
    "Oregon": ["Portland", "Salem"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown"],
    "Rhode Island": ["Providence"],
    "South Carolina": ["Columbia", "Charleston"],
    "South Dakota": ["Sioux Falls"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth"],
    "Utah": ["Salt Lake City", "West Valley City"],
    "Vermont": ["Burlington"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver"],
    "West Virginia": ["Charleston"],
    "Wisconsin": ["Milwaukee", "Madison"],
    "Wyoming": ["Cheyenne"],
}

REGIONAL_MERCHANTS = {
    "Southeast": [
        {"name": "Publix", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
        {"name": "Winn-Dixie", "category": "Groceries/Food & Beverage Stores", "amount_range": [30, 100], "payment_channels": ["in_store", "contactless"]},
        {"name": "Bojangles'", "category": "Food & Drink/Fast Food", "amount_range": [8, 20], "payment_channels": ["in_store", "contactless"]},
        {"name": "Wawa", "category": "Transport/Fuel", "amount_range": [10, 50], "payment_channels": ["in_store", "contactless"]},
    ],
    "West": [
        {"name": "In-N-Out Burger", "category": "Food & Drink/Fast Food", "amount_range": [8, 20], "payment_channels": ["in_store", "contactless"]},
        {"name": "Albertsons", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
        {"name": "Fred Meyer", "category": "Retail/Department Stores", "amount_range": [20, 150], "payment_channels": ["in_store", "contactless"]},
        {"name": "ARCO", "category": "Transport/Fuel", "amount_range": [30, 60], "payment_channels": ["in_store"]},
    ],
    "Northeast": [
        {"name": "Wegmans", "category": "Groceries/Food & Beverage Stores", "amount_range": [50, 150], "payment_channels": ["in_store", "contactless"]},
        {"name": "Sheetz", "category": "Transport/Fuel", "amount_range": [10, 50], "payment_channels": ["in_store", "contactless"]},
        {"name": "Stop & Shop", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
    ],
    "Midwest": [
        {"name": "Kroger", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
        {"name": "Meijer", "category": "Retail/Department Stores", "amount_range": [20, 150], "payment_channels": ["in_store", "contactless"]},
        {"name": "Hy-Vee", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
    ],
    "Southwest": [
        {"name": "H-E-B", "category": "Groceries/Food & Beverage Stores", "amount_range": [40, 120], "payment_channels": ["in_store", "contactless"]},
        {"name": "Whataburger", "category": "Food & Drink/Fast Food", "amount_range": [8, 20], "payment_channels": ["in_store", "contactless"]},
    ]
}

def get_random_location():
    """Returns a random (state, city) tuple."""
    import random
    state = random.choice(list(US_STATES_CITIES.keys()))
    city = random.choice(US_STATES_CITIES[state])
    return state, city
