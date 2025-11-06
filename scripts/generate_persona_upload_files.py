#!/usr/bin/env python3
"""
Generate data upload JSON files for each persona with a full year of transactions.
Includes mortgage and car payments.
"""

import json
import uuid
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Persona configurations
PERSONAS = {
    "1": {
        "name": "High Utilization",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "checking_balance": 850.00,
        "savings_balance": 1800.00,
        "credit_balance": 4800.00,
        "credit_limit": 5000.00,
        "monthly_income": 4200.00,
        "income_frequency": 2,  # bi-weekly
        "mortgage_payment": 1850.00,
        "auto_payment": 425.00,
        "transactions": {
            "coffee_shops_freq": 20,  # per month
            "fast_food_freq": 25,
            "restaurants_freq": 12,
            "delivery_freq": 18,
            "bars_freq": 6,
            "groceries_freq": 4,
            "retail_freq": 8,
            "online_shopping_freq": 10,
            "gas_freq": 8,
            "payment_behavior": "minimum_only"
        }
    },
    "2": {
        "name": "Variable Income Budgeter",
        "user_id": "22222222-2222-2222-2222-222222222222",
        "checking_balance": 1200.00,
        "savings_balance": 3500.00,
        "credit_balance": 1250.00,
        "credit_limit": 5000.00,
        "monthly_income": None,  # Variable
        "income_range": [500, 4000],
        "income_frequency": [1, 5],  # Variable
        "mortgage_payment": 1850.00,
        "auto_payment": 425.00,
        "transactions": {
            "coffee_shops_freq": 4,
            "fast_food_freq": 5,
            "restaurants_freq": 3,
            "delivery_freq": 3,
            "bars_freq": 2,
            "groceries_freq": 8,
            "retail_freq": 5,
            "online_shopping_freq": 4,
            "gas_freq": 6,
            "payment_behavior": "pays_in_full"
        }
    },
    "3": {
        "name": "Subscription-Heavy",
        "user_id": "33333333-3333-3333-3333-333333333333",
        "checking_balance": 2500.00,
        "savings_balance": 5000.00,
        "credit_balance": 1800.00,
        "credit_limit": 7500.00,
        "monthly_income": 5000.00,
        "income_frequency": 2,
        "mortgage_payment": 1850.00,
        "auto_payment": 425.00,
        "transactions": {
            "coffee_shops_freq": 6,
            "fast_food_freq": 4,
            "restaurants_freq": 3,
            "delivery_freq": 3,
            "bars_freq": 1,
            "groceries_freq": 6,
            "retail_freq": 4,
            "online_shopping_freq": 5,
            "gas_freq": 4,
            "streaming_freq": 8,
            "software_freq": 4,
            "gym_freq": 2,
            "payment_behavior": "pays_statement_balance"
        }
    },
    "4": {
        "name": "Savings Builder",
        "user_id": "44444444-4444-4444-4444-444444444444",
        "checking_balance": 3500.00,
        "savings_balance": 25000.00,
        "credit_balance": 600.00,
        "credit_limit": 12000.00,
        "monthly_income": 6500.00,
        "income_frequency": 2,
        "mortgage_payment": 1850.00,
        "auto_payment": 425.00,
        "transactions": {
            "coffee_shops_freq": 4,
            "fast_food_freq": 3,
            "restaurants_freq": 2,
            "delivery_freq": 2,
            "bars_freq": 1,
            "groceries_freq": 10,
            "retail_freq": 4,
            "online_shopping_freq": 3,
            "gas_freq": 5,
            "streaming_freq": 2,
            "savings_transfer_freq": 2,
            "savings_transfer_amount": [800, 1500],
            "payment_behavior": "pays_in_full"
        }
    },
    "5": {
        "name": "Custom/Balanced",
        "user_id": "55555555-5555-5555-5555-555555555555",
        "checking_balance": 2200.00,
        "savings_balance": 8000.00,
        "credit_balance": 2000.00,
        "credit_limit": 8000.00,
        "monthly_income": 5250.00,
        "income_frequency": 2,
        "mortgage_payment": 1850.00,
        "auto_payment": 425.00,
        "transactions": {
            "coffee_shops_freq": 8,
            "fast_food_freq": 8,
            "restaurants_freq": 5,
            "delivery_freq": 4,
            "bars_freq": 3,
            "groceries_freq": 8,
            "retail_freq": 6,
            "online_shopping_freq": 7,
            "gas_freq": 7,
            "streaming_freq": 2,
            "savings_transfer_freq": [0, 2],  # Variable
            "savings_transfer_amount": [100, 1000],
            "payment_behavior": "pays_statement_balance"
        }
    }
}

# Merchant pools
COFFEE_SHOPS = ["Starbucks", "Dunkin'", "Peet's Coffee", "Local Coffee Shop"]
FAST_FOOD = ["McDonald's", "Burger King", "Taco Bell", "Chipotle", "Subway", "Wendy's"]
RESTAURANTS = ["Olive Garden", "Applebee's", "Red Lobster", "Outback Steakhouse", "Local Restaurant"]
DELIVERY = ["DoorDash", "Uber Eats", "Grubhub", "Postmates"]
BARS = ["Local Bar & Grill", "Sports Bar", "Pub", "Cocktail Lounge"]
GROCERIES = ["Kroger", "Walmart", "Target", "Whole Foods", "Safeway", "Trader Joe's"]
RETAIL = ["Target", "Walmart", "Best Buy", "Home Depot", "Costco"]
ONLINE = ["Amazon", "eBay", "Etsy", "Wayfair"]
GAS = ["Shell", "Exxon", "BP", "Chevron", "7-Eleven"]
STREAMING = ["Netflix", "Hulu", "Disney+", "HBO Max", "Paramount+", "Peacock", "Spotify", "Apple Music"]
SOFTWARE = ["Adobe Creative Cloud", "Microsoft 365", "Dropbox", "Google Workspace", "Zoom"]
GYMS = ["Planet Fitness", "24 Hour Fitness", "Equinox", "YMCA", "ClassPass"]

UTILITIES = ["Electric Company", "Gas Company", "Water Department"]
INTERNET = ["Comcast", "Verizon Fios", "AT&T Internet", "Spectrum"]
PHONE = ["Verizon Wireless", "AT&T", "T-Mobile", "Sprint"]

MORTGAGE_SERVICERS = ["Wells Fargo Mortgage", "Chase Mortgage", "Bank of America Mortgage", "Quicken Loans"]
AUTO_LOAN_SERVICERS = ["Toyota Financial", "Honda Financial", "Ford Credit", "Chase Auto Loan", "Capital One Auto"]

def generate_transactions_for_persona(persona_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Generate a full year of transactions for a persona."""
    persona = PERSONAS[persona_id]
    transactions = []
    current_date = start_date
    txn_counter = 1
    
    # Generate income payments
    if persona["monthly_income"]:
        # Fixed income
        income_amount = persona["monthly_income"] / persona["income_frequency"]
        next_income = current_date.replace(day=15)
        while next_income <= end_date:
            transactions.append({
                "transaction_id": f"txn-payroll-{next_income.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": next_income.strftime("%Y-%m-%d"),
                "amount": income_amount,
                "merchant_name": "Direct Deposit",
                "merchant_entity_id": None,
                "payment_channel": "ACH",
                "personal_finance_category": {
                    "primary": "PAYROLL",
                    "detailed": "PAYROLL"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            # Bi-weekly
            if persona["income_frequency"] == 2:
                next_income += timedelta(days=14)
            else:
                next_income += timedelta(days=30)
    else:
        # Variable income
        income_counter = 0
        while current_date <= end_date:
            if random.random() < 0.15:  # Random income payments
                income_amount = random.uniform(*persona["income_range"])
                transactions.append({
                    "transaction_id": f"txn-payroll-{current_date.strftime('%Y-%m-%d')}-{income_counter}",
                    "account_id": "acct-checking-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": income_amount,
                    "merchant_name": "Direct Deposit",
                    "merchant_entity_id": None,
                    "payment_channel": "ACH",
                    "personal_finance_category": {
                        "primary": "PAYROLL",
                        "detailed": "PAYROLL"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
                income_counter += 1
            current_date += timedelta(days=1)
    
    # Generate monthly mortgage and auto payments for all months in range
    payment_date = start_date.replace(day=1)
    while payment_date <= end_date:
        # Mortgage payment on 1st
        transactions.append({
            "transaction_id": f"txn-mortgage-{payment_date.strftime('%Y-%m-%d')}",
            "account_id": "acct-checking-001",
            "date": payment_date.strftime("%Y-%m-%d"),
            "amount": persona["mortgage_payment"],
            "merchant_name": random.choice(MORTGAGE_SERVICERS) + " Payment",
            "merchant_entity_id": None,
            "payment_channel": "online",
            "personal_finance_category": {
                "primary": "Bills & Utilities",
                "detailed": "Bills & Utilities/Mortgage"
            },
            "pending": False,
            "iso_currency_code": "USD"
        })
        
        # Auto loan payment on 5th (or first day if 5th is before start_date)
        auto_payment_date = payment_date.replace(day=5)
        if auto_payment_date < start_date:
            auto_payment_date = (payment_date + timedelta(days=32)).replace(day=5)
        if auto_payment_date <= end_date:
            transactions.append({
                "transaction_id": f"txn-auto-{auto_payment_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": auto_payment_date.strftime("%Y-%m-%d"),
                "amount": persona["auto_payment"],
                "merchant_name": random.choice(AUTO_LOAN_SERVICERS) + " Payment",
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Bills & Utilities",
                    "detailed": "Bills & Utilities/Auto Loan"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        
        # Move to next month
        if payment_date.month == 12:
            payment_date = payment_date.replace(year=payment_date.year + 1, month=1)
        else:
            payment_date = payment_date.replace(month=payment_date.month + 1)
    
    # Reset current_date for spending transactions
    current_date = start_date
    
    # Generate spending transactions
    while current_date <= end_date:
        month = current_date.month
        day_of_month = current_date.day
        
        # Utilities (early in month)
        if day_of_month == 6:
            transactions.append({
                "transaction_id": f"txn-utilities-{current_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(80, 200), 2),
                "merchant_name": random.choice(UTILITIES),
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Bills & Utilities",
                    "detailed": "Bills & Utilities/Utilities"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        
        # Internet (early in month)
        if day_of_month == 7:
            transactions.append({
                "transaction_id": f"txn-internet-{current_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(50, 100), 2),
                "merchant_name": random.choice(INTERNET),
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Bills & Utilities",
                    "detailed": "Bills & Utilities/Internet"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        
        # Phone (early in month)
        if day_of_month == 8:
            transactions.append({
                "transaction_id": f"txn-phone-{current_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(60, 120), 2),
                "merchant_name": random.choice(PHONE),
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Bills & Utilities",
                    "detailed": "Bills & Utilities/Mobile Phone"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        
        # Credit card payment (mid-month)
        if day_of_month == 15 and persona["transactions"]["payment_behavior"] != "minimum_only":
            # Pays statement balance or in full
            payment_amount = persona["credit_balance"] * 0.8 if persona["transactions"]["payment_behavior"] == "pays_statement_balance" else persona["credit_balance"]
            transactions.append({
                "transaction_id": f"txn-cc-payment-{current_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(payment_amount, 2),
                "merchant_name": "Credit Card Payment",
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Financial",
                    "detailed": "Financial/Payments"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        elif day_of_month == 10 and persona["transactions"]["payment_behavior"] == "minimum_only":
            # Minimum payment only
            transactions.append({
                "transaction_id": f"txn-cc-minimum-{current_date.strftime('%Y-%m-%d')}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": 150.00,
                "merchant_name": "Credit Card Payment",
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Financial",
                    "detailed": "Financial/Payments"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
        
        # Coffee shops (daily for high utilization, less for others)
        freq = persona["transactions"]["coffee_shops_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-coffee-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(4, 9), 2),
                "merchant_name": random.choice(COFFEE_SHOPS),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Food & Drink",
                    "detailed": "Food & Drink/Coffee Shops"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Fast food
        freq = persona["transactions"]["fast_food_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-fastfood-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(8, 30), 2),
                "merchant_name": random.choice(FAST_FOOD),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Food & Drink",
                    "detailed": "Food & Drink/Fast Food"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Restaurants
        freq = persona["transactions"]["restaurants_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-restaurant-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(20, 80), 2),
                "merchant_name": random.choice(RESTAURANTS),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Food & Drink",
                    "detailed": "Food & Drink/Restaurants"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Delivery
        if "delivery_freq" in persona["transactions"]:
            freq = persona["transactions"]["delivery_freq"]
            if random.random() < (freq / 30):
                transactions.append({
                    "transaction_id": f"txn-delivery-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                    "account_id": "acct-credit-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": round(random.uniform(15, 45), 2),
                    "merchant_name": random.choice(DELIVERY),
                    "merchant_entity_id": None,
                    "payment_channel": "online",
                    "personal_finance_category": {
                        "primary": "Food & Drink",
                        "detailed": "Food & Drink/Fast Food"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
                txn_counter += 1
        
        # Bars
        freq = persona["transactions"]["bars_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-bar-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(20, 60), 2),
                "merchant_name": random.choice(BARS),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Food & Drink",
                    "detailed": "Food & Drink/Bars & Pubs"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Groceries
        freq = persona["transactions"]["groceries_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-groceries-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(40, 150), 2),
                "merchant_name": random.choice(GROCERIES),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Food & Drink",
                    "detailed": "Food & Drink/Groceries"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Retail
        freq = persona["transactions"]["retail_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-retail-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(20, 200), 2),
                "merchant_name": random.choice(RETAIL),
                "merchant_entity_id": None,
                "payment_channel": random.choice(["in_store", "online"]),
                "personal_finance_category": {
                    "primary": "Retail",
                    "detailed": "Retail/Department Stores"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Online shopping
        freq = persona["transactions"]["online_shopping_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-online-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-credit-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(15, 200), 2),
                "merchant_name": random.choice(ONLINE),
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {
                    "primary": "Retail",
                    "detailed": "Retail/Online Marketplace"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Gas
        freq = persona["transactions"]["gas_freq"]
        if random.random() < (freq / 30):
            transactions.append({
                "transaction_id": f"txn-gas-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                "account_id": "acct-checking-001",
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(30, 70), 2),
                "merchant_name": random.choice(GAS),
                "merchant_entity_id": None,
                "payment_channel": "in_store",
                "personal_finance_category": {
                    "primary": "Transport",
                    "detailed": "Transport/Fuel"
                },
                "pending": False,
                "iso_currency_code": "USD"
            })
            txn_counter += 1
        
        # Streaming services (for subscription-heavy persona)
        if "streaming_freq" in persona["transactions"]:
            freq = persona["transactions"]["streaming_freq"]
            if random.random() < (freq / 30):
                transactions.append({
                    "transaction_id": f"txn-streaming-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                    "account_id": "acct-credit-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": round(random.uniform(10, 30), 2),
                    "merchant_name": random.choice(STREAMING),
                    "merchant_entity_id": None,
                    "payment_channel": "online",
                    "personal_finance_category": {
                        "primary": "Entertainment",
                        "detailed": "Entertainment/Streaming Services"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
                txn_counter += 1
        
        # Software subscriptions (for subscription-heavy persona)
        if "software_freq" in persona["transactions"]:
            freq = persona["transactions"]["software_freq"]
            if random.random() < (freq / 30):
                transactions.append({
                    "transaction_id": f"txn-software-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                    "account_id": "acct-credit-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": round(random.uniform(5, 50), 2),
                    "merchant_name": random.choice(SOFTWARE),
                    "merchant_entity_id": None,
                    "payment_channel": "online",
                    "personal_finance_category": {
                        "primary": "Software",
                        "detailed": "Software/Cloud Services"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
                txn_counter += 1
        
        # Gym memberships (for subscription-heavy persona)
        if "gym_freq" in persona["transactions"]:
            freq = persona["transactions"]["gym_freq"]
            if day_of_month == 1 and random.random() < (freq / 1):  # Monthly charges
                transactions.append({
                    "transaction_id": f"txn-gym-{current_date.strftime('%Y-%m-%d')}",
                    "account_id": "acct-credit-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": round(random.uniform(10, 200), 2),
                    "merchant_name": random.choice(GYMS),
                    "merchant_entity_id": None,
                    "payment_channel": "online",
                    "personal_finance_category": {
                        "primary": "Health & Fitness",
                        "detailed": "Health & Fitness/Gym Memberships"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
        
        # Savings transfers (for savings builder persona)
        if "savings_transfer_freq" in persona["transactions"]:
            freq = persona["transactions"]["savings_transfer_freq"]
            amount_range = persona["transactions"].get("savings_transfer_amount", [100, 1000])
            if isinstance(freq, list):
                # Variable frequency
                if random.random() < (sum(freq) / 60):
                    transactions.append({
                        "transaction_id": f"txn-savings-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                        "account_id": "acct-checking-001",
                        "date": current_date.strftime("%Y-%m-%d"),
                        "amount": round(random.uniform(*amount_range), 2),
                        "merchant_name": "Transfer to Savings",
                        "merchant_entity_id": None,
                        "payment_channel": "online",
                        "personal_finance_category": {
                            "primary": "Financial",
                            "detailed": "Financial/Transfers"
                        },
                        "pending": False,
                        "iso_currency_code": "USD"
                    })
                    txn_counter += 1
            elif day_of_month in [1, 15] and random.random() < (freq / 30):
                transactions.append({
                    "transaction_id": f"txn-savings-{current_date.strftime('%Y-%m-%d')}-{txn_counter}",
                    "account_id": "acct-checking-001",
                    "date": current_date.strftime("%Y-%m-%d"),
                    "amount": round(random.uniform(*amount_range), 2),
                    "merchant_name": "Transfer to Savings",
                    "merchant_entity_id": None,
                    "payment_channel": "online",
                    "personal_finance_category": {
                        "primary": "Financial",
                        "detailed": "Financial/Transfers"
                    },
                    "pending": False,
                    "iso_currency_code": "USD"
                })
                txn_counter += 1
        
        current_date += timedelta(days=1)
    
    # Sort transactions by date
    transactions.sort(key=lambda x: x["date"])
    
    return transactions

def generate_persona_file(persona_id: str, output_path: str):
    """Generate a complete upload JSON file for a persona."""
    persona = PERSONAS[persona_id]
    
    # Calculate date range (last 365 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Generate accounts
    accounts = [
        {
            "account_id": "acct-checking-001",
            "name": "Chase Checking",
            "type": "depository",
            "subtype": "checking",
            "holder_category": "individual",
            "balances": {
                "available": persona["checking_balance"],
                "current": persona["checking_balance"] * 1.1,
                "limit": None
            },
            "iso_currency_code": "USD",
            "mask": "1234"
        },
        {
            "account_id": "acct-savings-001",
            "name": "Chase Savings",
            "type": "depository",
            "subtype": "savings",
            "holder_category": "individual",
            "balances": {
                "available": persona["savings_balance"],
                "current": persona["savings_balance"],
                "limit": None
            },
            "iso_currency_code": "USD",
            "mask": "5678"
        },
        {
            "account_id": "acct-credit-001",
            "name": "Chase Freedom Credit Card",
            "type": "credit",
            "subtype": "credit card",
            "holder_category": "individual",
            "balances": {
                "available": persona["credit_limit"] - persona["credit_balance"],
                "current": persona["credit_balance"],
                "limit": persona["credit_limit"]
            },
            "iso_currency_code": "USD",
            "mask": "9012"
        },
        {
            "account_id": "acct-mortgage-001",
            "name": "Wells Fargo Mortgage",
            "type": "loan",
            "subtype": "mortgage",
            "holder_category": "individual",
            "balances": {
                "available": None,
                "current": 285000.00,
                "limit": 300000.00
            },
            "iso_currency_code": "USD",
            "mask": "3456"
        },
        {
            "account_id": "acct-auto-loan-001",
            "name": "Toyota Financial Auto Loan",
            "type": "loan",
            "subtype": "auto",
            "holder_category": "individual",
            "balances": {
                "available": None,
                "current": 18500.00,
                "limit": 25000.00
            },
            "iso_currency_code": "USD",
            "mask": "7890"
        }
    ]
    
    # Generate transactions
    transactions = generate_transactions_for_persona(persona_id, start_date, end_date)
    
    # Generate liabilities
    last_mortgage_date = end_date.replace(day=1) - timedelta(days=1)
    last_auto_date = end_date.replace(day=5)
    if last_auto_date > end_date:
        last_auto_date = (end_date - timedelta(days=32)).replace(day=5)
    
    liabilities = [
        {
            "account_id": "acct-mortgage-001",
            "apr_percentage": None,
            "apr_type": None,
            "minimum_payment_amount": persona["mortgage_payment"],
            "last_payment_amount": persona["mortgage_payment"],
            "last_payment_date": last_mortgage_date.strftime("%Y-%m-%d"),
            "last_statement_balance": 285000.00,
            "is_overdue": False,
            "next_payment_due_date": (end_date + timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d"),
            "interest_rate": 6.5
        },
        {
            "account_id": "acct-auto-loan-001",
            "apr_percentage": None,
            "apr_type": None,
            "minimum_payment_amount": persona["auto_payment"],
            "last_payment_amount": persona["auto_payment"],
            "last_payment_date": last_auto_date.strftime("%Y-%m-%d"),
            "last_statement_balance": 18500.00,
            "is_overdue": False,
            "next_payment_due_date": (end_date + timedelta(days=1)).replace(day=5).strftime("%Y-%m-%d"),
            "interest_rate": 4.75
        }
    ]
    
    # Create the complete JSON structure
    data = {
        "user_id": persona["user_id"],
        "accounts": accounts,
        "transactions": transactions,
        "liabilities": liabilities
    }
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated {output_path} with {len(transactions)} transactions")

def main():
    """Generate upload files for all personas."""
    output_dir = "../data_examples"
    
    for persona_id in PERSONAS.keys():
        persona_name = PERSONAS[persona_id]["name"].lower().replace(" ", "_").replace("/", "_")
        output_path = f"{output_dir}/persona_{persona_id}_{persona_name}_upload.json"
        generate_persona_file(persona_id, output_path)
    
    print("\nAll persona upload files generated successfully!")

if __name__ == "__main__":
    main()

