# Realistic Data Seeding Improvements

## Overview

The synthetic data generation system has been enhanced to use **realistic merchant names** and **persona-specific spending patterns** that accurately reflect real-world financial behaviors.

## Key Improvements

### 1. Realistic Merchant Names

Instead of generic placeholders like "StreamFlix #1" or "BeerBarn #2", the system now uses **actual merchant names**:

- **Streaming Services**: Netflix, Hulu, Disney Plus, Spotify, Apple Music, YouTube Premium, HBO Max, etc.
- **Food Delivery**: DoorDash, Uber Eats, Grubhub, Instacart
- **Coffee Shops**: Starbucks, Dunkin', Peet's Coffee, Caribou Coffee
- **Fast Food**: McDonald's, Chipotle, Chick-fil-A, Subway, Five Guys, Shake Shack
- **Restaurants**: Olive Garden, Applebee's, Red Lobster, Cheesecake Factory, Outback Steakhouse
- **Gym Memberships**: Planet Fitness, 24 Hour Fitness, LA Fitness, Gold's Gym, Equinox
- **Software Subscriptions**: Adobe Creative Cloud, Microsoft 365, Dropbox, Zoom, Slack
- **Grocery Stores**: Whole Foods, Trader Joe's, Kroger, Safeway, Costco, Walmart
- **Retail**: Amazon, Target, Best Buy, Home Depot, Lowe's, Macy's, Nordstrom
- **Utilities**: Real utility companies (PG&E, Con Edison, Duke Energy, etc.)
- **Mobile Carriers**: Verizon, AT&T, T-Mobile

### 2. Persona-Specific Spending Patterns

Each persona now generates transactions that match their behavioral profile:

#### Persona 1: High Utilization
- **Frequent fast food** (McDonald's, Chipotle) - 12-30 times/month
- **Frequent dining out** (Olive Garden, Applebee's) - 8-18 times/month  
- **Daily coffee** (Starbucks, Dunkin') - 10-25 times/month
- **Frequent food delivery** (DoorDash, Uber Eats) - 8-20 times/month
- **Frequent shopping** (Target, Walmart, Amazon) - 5-20 times/month
- **High credit card balances** with minimum payments only

#### Persona 2: Variable Income Budgeter
- **Cook at home more** - regular grocery shopping (Whole Foods, Trader Joe's, Kroger)
- **Less frequent dining out** - 3-8 times/month
- **Frequent gas purchases** (Shell, Exxon, BP) - 4-10 times/month
- **Irregular income** - multiple payments per month, varying amounts
- **Conservative spending** - pays credit cards in full

#### Persona 3: Subscription-Heavy
- **Multiple streaming services** (Netflix, Hulu, Spotify, Disney Plus) - 4-6 subscriptions/month
- **Software subscriptions** (Adobe, Microsoft 365, Dropbox) - 2-4 subscriptions/month
- **Gym memberships** (Planet Fitness, 24 Hour Fitness, LA Fitness) - 1-2 memberships
- **Regular recurring charges** - consistent monthly billing patterns
- **Pays statement balance** - responsible with credit cards

#### Persona 4: Savings Builder
- **Regular grocery shopping** (Whole Foods, Trader Joe's, Costco) - 8-15 times/month
- **Regular savings transfers** - $500-$2000/month, 1-3 times/month
- **Less frequent shopping** - 2-6 times/month
- **Less frequent coffee** - 2-8 times/month (cooks at home)
- **High savings balances** - $10,000-$50,000
- **Pays credit cards in full** - low utilization

#### Persona 5: Custom/Balanced
- **Mixed spending patterns** - some of everything
- **Moderate grocery shopping** - 6-12 times/month
- **Some fast food** - 5-12 times/month
- **Some dining out** - 3-8 times/month
- **A few subscriptions** - 1-3 streaming services
- **Moderate shopping** - 4-10 times/month

### 3. Realistic Names

The seeding script uses **Faker** to generate realistic names:
- Realistic first and last names
- Proper email addresses matching names
- Diverse name pool for better representation

### 4. Merchant Amount Ranges

Merchants now have **realistic amount ranges** based on actual pricing:
- **Netflix**: $9.99-$22.99 (Standard/Ultra plans)
- **Starbucks**: $4.50-$8.50 (typical coffee purchase)
- **McDonald's**: $8-$25 (meal combos)
- **DoorDash**: $15-$45 (delivery with fees)
- **Gym Memberships**: $10-$200 (Planet Fitness to Equinox)

## Usage

### Generate Synthetic Data with Realistic Merchants

```bash
# Generate data for all personas
python scripts/synthetic_data_generator.py \
  scripts/persona_configs/ \
  docs/support/transactions_100_users_2024.csv \
  --output-dir synthetic_data \
  --format json
```

### Seed Database with Realistic Data

```bash
# Create users and load realistic transaction data
python backend/scripts/seed_db.py \
  --users-per-persona 10 \
  --with-data \
  --data-dir synthetic_data
```

This will:
1. Create 50 users (10 per persona) with realistic names
2. Load transaction data with real merchant names
3. Assign personas based on actual spending patterns
4. Generate recommendations that match the user's spending behavior

## Benefits

1. **More Realistic Testing**: Operators can see actual merchant names they recognize
2. **Better Persona Detection**: Spending patterns clearly match personas (Netflix subscriptions → Subscription-Heavy persona)
3. **Easier Debugging**: Real merchant names make it easier to understand transaction patterns
4. **Better Recommendations**: System can generate more accurate recommendations based on realistic spending patterns

## File Structure

- `scripts/realistic_merchants.py` - Database of realistic merchants organized by category and persona
- `scripts/persona_configs/*.yaml` - Updated persona configs with specific categories matching realistic merchants
- `scripts/synthetic_data_generator.py` - Enhanced to use realistic merchants
- `backend/scripts/seed_db.py` - Uses Faker for realistic names (already in place)

## Example Output

Instead of:
```
merchant_name: "StreamFlix #1"
merchant_name: "BeerBarn #2"
```

You'll now see:
```
merchant_name: "Netflix"
merchant_name: "Starbucks"
merchant_name: "DoorDash"
merchant_name: "McDonald's"
merchant_name: "Planet Fitness"
```

This makes the data much more realistic and easier to analyze!

