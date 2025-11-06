import argparse
import csv
import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List
import uuid

import yaml
from faker import Faker

# Import location data
try:
    from location_data import get_random_location, REGIONAL_MERCHANTS
    LOCATION_DATA_AVAILABLE = True
except ImportError:
    LOCATION_DATA_AVAILABLE = False
    print("⚠ location_data module not found. Geographic realism will be disabled.")


# Add paths for imports
import sys
import os
_current_file = os.path.abspath(__file__)
_project_root = os.path.dirname(os.path.dirname(_current_file))
_backend_dir = os.path.join(_project_root, "backend")
_service_dir = os.path.join(_project_root, "service")
_scripts_dir = os.path.dirname(_current_file)

# Add backend first (service depends on it), then service, then scripts
for path in [_backend_dir, _service_dir, _scripts_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import validator directly from the file to avoid circular imports
import importlib.util
spec = importlib.util.spec_from_file_location("validator", os.path.join(_project_root, "service", "app", "ingestion", "validator.py"))
validator_module = importlib.util.module_from_spec(spec)
sys.modules['validator'] = validator_module
spec.loader.exec_module(validator_module)
PlaidValidator = validator_module.PlaidValidator

# --- Configuration ---
LOGGING_LEVEL = logging.INFO
# Set the locale for the Faker instance, which determines the localization for the generated data
FAKER_LOCALE = "en_US"

# --- Setup Logging ---
logging.basicConfig(level=LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Main Generator Class ---

class SyntheticDataGenerator:
    """Generates synthetic Plaid-style financial data based on persona configurations."""

    def __init__(self, config_path: str, transactions_csv_path: str):
        """
        Initializes the generator.

        Args:
            config_path: Path to the persona YAML configuration file.
            transactions_csv_path: Path to the CSV file with sample transactions.
        """
        self.config = self._load_config(config_path)
        self.faker = Faker(FAKER_LOCALE)
        self.validator = PlaidValidator()
        self.merchant_pool = self._load_merchant_pool(transactions_csv_path)
        
        # Load realistic merchants based on persona
        try:
            from realistic_merchants import get_merchants_for_persona, get_merchants_by_category
            self.realistic_merchants = get_merchants_for_persona
            self.get_merchants_by_category = get_merchants_by_category
            
            # Determine persona ID from config path or config
            persona_id = self._extract_persona_id(config_path)
            if persona_id:
                persona_merchants = get_merchants_for_persona(persona_id)
                # Merge realistic merchants into merchant pool
                all_realistic = persona_merchants["primary"] + persona_merchants["secondary"]
                # Create a set of existing merchant names for quick lookup
                existing_names = {m.get("name", "") for m in self.merchant_pool if isinstance(m, dict)}
                for merchant in all_realistic:
                    if merchant["name"] not in existing_names:
                        # Add realistic merchant with full metadata
                        self.merchant_pool.append({
                            "name": merchant["name"],
                            "category": merchant["category"],
                            "amount_range": merchant.get("amount_range", [10, 100]),
                            "payment_channels": merchant.get("payment_channels", ["online"]),
                            "type": merchant.get("type", "national_chain"),
                            "_is_realistic": True  # Flag to identify realistic merchants
                        })
                        existing_names.add(merchant["name"])
        except ImportError:
            logger.warning("realistic_merchants module not found. Using fallback merchant pool.")
            self.realistic_merchants = None
            self.get_merchants_by_category = None

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads a YAML configuration file."""
        logger.info(f"Loading persona configuration from: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _extract_persona_id(self, config_path: str) -> int:
        """Extract persona ID from config file path or name."""
        # Try to extract from filename (e.g., "1_high_utilization.yaml" -> 1)
        import re
        filename = os.path.basename(config_path)
        match = re.match(r'^(\d+)_', filename)
        if match:
            return int(match.group(1))
        
        # Try to get from config content
        persona_name = self.config.get("persona_name", "").lower()
        if "high utilization" in persona_name or "high_utilization" in persona_name:
            return 1
        elif "variable income" in persona_name or "variable_income" in persona_name:
            return 2
        elif "subscription" in persona_name:
            return 3
        elif "savings" in persona_name:
            return 4
        return 5  # Default to balanced
    
    def _load_merchant_pool(self, path: str) -> List[Dict[str, str]]:
        """Loads a pool of merchants and categories from a CSV file."""
        logger.info(f"Loading merchant pool from: {path}")
        pool = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pool.append({
                        "name": row["merchant_name"],
                        "category": row["personal_finance_category"],
                    })
            logger.info(f"Loaded {len(pool)} merchants from CSV into the pool.")
            return pool
        except FileNotFoundError:
            logger.warning(f"Transactions CSV not found at {path}. Will use realistic merchants only.")
            return []
        except Exception as e:
            logger.error(f"Error loading merchant pool: {e}")
            return []

    def generate_profiles(self) -> List[Dict[str, Any]]:
        """Generates a list of user profiles based on the configuration."""
        num_profiles = self.config.get("num_profiles", 1)
        logger.info(f"Generating {num_profiles} profiles for persona: {self.config.get('persona_name', 'Unknown')}")

        profiles = []
        for i in range(num_profiles):
            user_id = str(uuid.uuid4())
            logger.info(f"Generating profile {i+1}/{num_profiles} for user {user_id}...")
            profile = self._generate_single_profile(user_id)
            profiles.append(profile)
        return profiles

    def _generate_single_profile(self, user_id: str) -> Dict[str, Any]:
        """Generates a single, complete user profile with accounts, transactions, and liabilities.
        
        Note: user_id is used only for internal tracking during generation.
        The output JSON does NOT include user_id - it will be assigned by the authenticated user during upload.
        """
        
        # Assign a home location to this user
        if LOCATION_DATA_AVAILABLE:
            self.home_state, self.home_city = get_random_location()
        else:
            self.home_state, self.home_city = "CA", "San Francisco" # Fallback

        accounts = self._generate_accounts()
        transactions = self._generate_transactions(accounts)
        liabilities = self._generate_liabilities(accounts)

        # Do NOT include user_id in the output - it will be assigned by the authenticated user
        profile_data = {
            "accounts": accounts,
            "transactions": transactions,
            "liabilities": liabilities
        }
        return profile_data

    def _get_random_value(self, config_range: List[float]) -> float:
        """Returns a random value from a [min, max] range."""
        return random.uniform(config_range[0], config_range[1])

    def _generate_accounts(self) -> List[Dict[str, Any]]:
        """Generates a list of accounts based on the persona configuration."""
        accounts = []
        account_configs = self.config.get("accounts", [])
        
        # Realistic bank names
        bank_names = [
            "Chase", "Bank of America", "Wells Fargo", "Citibank", "US Bank",
            "Capital One", "PNC Bank", "TD Bank", "SunTrust", "BB&T",
            "Ally Bank", "Discover Bank", "Goldman Sachs", "Morgan Stanley",
            "Charles Schwab", "Fidelity", "Vanguard"
        ]

        for acc_config in account_configs:
            account_id = f"acct-{uuid.uuid4()}"
            balance = self._get_random_value(acc_config["balance_range"])
            limit = self._get_random_value(acc_config["limit_range"]) if "limit_range" in acc_config else None
            
            # Use realistic bank name
            bank_name = random.choice(bank_names)
            account_name = f"{bank_name} {acc_config['subtype'].replace('_', ' ').title()}"

            account = {
                "account_id": account_id,
                "name": account_name,
                "type": acc_config["type"],
                "subtype": acc_config["subtype"],
                "holder_category": "individual",
                "balances": {
                    "available": balance * random.uniform(0.8, 1.0), # Assume available is slightly less than current
                    "current": balance,
                    "limit": limit,
                },
                "iso_currency_code": "USD",
                "mask": str(random.randint(1000, 9999)),
            }
            accounts.append(account)
        return accounts

    def _generate_transactions(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generates a list of transactions based on the persona configuration.
        """
        transactions = []
        tx_config = self.config.get("transactions", {})
        history_days = tx_config.get("history_days", 180)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=history_days)
        
        # --- Generate recurring monthly transactions first for consistency ---
        recurring_transactions = self._generate_recurring_transactions(accounts, start_date, end_date)
        transactions.extend(recurring_transactions)

        # --- Generate special transaction types (income, credit card payments, transfers) ---
        special_transactions = self._generate_special_transactions(accounts, start_date, end_date)
        transactions.extend(special_transactions)

        # --- Generate general spending transactions ---
        general_transactions = self._generate_general_spending(accounts, start_date, end_date)
        transactions.extend(general_transactions)

        # --- Generate event-based "stories" ---
        story_transactions = self._generate_transaction_stories(accounts, start_date, end_date)
        transactions.extend(story_transactions)

        # --- Post-processing ---
        # 1. Sort all transactions by date
        transactions.sort(key=lambda x: x["datetime"])
        
        # 2. Add refunds for a small percentage of retail transactions
        transactions_with_refunds = self._add_refunds(transactions)
        
        # 3. Mark most recent transactions as pending
        final_transactions = self._mark_pending_transactions(transactions_with_refunds)

        # 4. Final sort and format datetime to string
        final_transactions.sort(key=lambda x: x["datetime"])
        for tx in final_transactions:
            tx["date"] = tx["datetime"].strftime("%Y-%m-%d")
            # The datetime object is not JSON serializable, so remove it or convert to string
            tx["datetime"] = tx["datetime"].isoformat()
        
        return final_transactions

    def _get_datetime_for_category(self, date, category: str) -> datetime:
        """Generates a realistic timestamp for a transaction based on its category."""
        # Convert date to datetime if needed
        if isinstance(date, datetime):
            base_datetime = date
        else:
            # It's a date object, convert to datetime at midnight
            from datetime import date as date_type
            if isinstance(date, date_type):
                base_datetime = datetime.combine(date, datetime.min.time())
            else:
                # Fallback: assume it's already a datetime
                base_datetime = date
        
        hour = 12  # Default noon
        if "Coffee" in category:
            hour = random.randint(7, 10) # Morning
        elif "Restaurant" in category or "Bar" in category:
            hour = random.randint(18, 22) # Evening
        elif "Fast Food" in category:
            hour = random.choice([random.randint(11, 13), random.randint(17, 20)]) # Lunch/Dinner
        else:
            hour = random.randint(9, 21) # General daytime
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return base_datetime.replace(hour=hour, minute=minute, second=second)

    def _generate_recurring_transactions(self, accounts, start_date, end_date):
        """Generates consistent monthly recurring transactions like subscriptions and loan payments."""
        transactions = []
        tx_config = self.config.get("transactions", {})
        
        recurring_patterns = [p for p in tx_config.get("patterns", []) if self._is_recurring(p)]
        
        for pattern in recurring_patterns:
            # Assign a consistent day of the month for this recurring charge
            billing_day = random.randint(1, 28)
            
            num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

            for i in range(num_months + 1):
                current_month = start_date.month + i
                current_year = start_date.year + (current_month - 1) // 12
                current_month = (current_month - 1) % 12 + 1
                
                # Skip if the calculated date is in the future
                if datetime(current_year, current_month, billing_day) > end_date:
                    continue

                date = datetime(current_year, current_month, billing_day)
                
                # Find a merchant for this recurring transaction
                merchant = self._get_merchant_for_pattern(pattern)
                if not merchant:
                    continue
                
                amount = -abs(self._get_random_value(merchant.get("amount_range") or pattern.get("amount_range", [10, 50])))
                # Map payment channels to valid Plaid values (online, in_store, other, ACH)
                payment_channel_raw = random.choice(merchant.get("payment_channels", ["online"]))
                payment_channel_map = {
                    "mobile": "online",  # Mobile payments are online
                    "contactless": "in_store",  # Contactless is in-store
                    "online": "online",
                    "in_store": "in_store",
                    "other": "other",
                    "ACH": "ACH"
                }
                payment_channel = payment_channel_map.get(payment_channel_raw, "other")
                
                tx = {
                    "transaction_id": f"txn-{uuid.uuid4()}",
                    "account_id": self._get_random_account(accounts, ["checking", "credit card"]),
                    "datetime": self._get_datetime_for_category(date, merchant["category"]),
                    "amount": amount,
                    "merchant_name": merchant["name"],
                    "merchant_entity_id": None,
                    "payment_channel": payment_channel,
                    "personal_finance_category": {
                        "primary": merchant["category"].split('/')[0],
                        "detailed": merchant["category"],
                    },
                    "pending": False,
                    "iso_currency_code": "USD",
                }
                transactions.append(tx)
                
        return transactions

    def _is_recurring(self, pattern: Dict[str, Any]) -> bool:
        """Determines if a transaction pattern is for a recurring subscription or payment."""
        category = pattern.get("category", "").lower()
        payment_type = pattern.get("payment_type", "").lower()

        recurring_categories = [
            "subscription", "memberships", "streaming", "cloud services", 
            "internet", "mobile phone", "utilities"
        ]
        recurring_payments = ["loan_payment", "credit_card_payment"]

        if any(sub in category for sub in recurring_categories):
            return True
        if payment_type in recurring_payments:
            # Only consider it recurring if frequency is monthly
            freq = pattern.get("frequency_per_month", [0,0])
            if freq == [1,1]:
                return True
        return False

    def _get_merchant_for_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Finds a suitable merchant from the merchant pool for a given pattern.
        Prioritizes realistic merchants over CSV merchants."""
        merchants_in_category = []
        category = pattern.get("category")
        if not category:
            return None
            
        # First try realistic merchants - ALWAYS prioritize these
        if self.get_merchants_by_category:
            merchants_in_category = self.get_merchants_by_category(category)
        
        # If we have realistic merchants, use them and NEVER fall back to CSV
        if merchants_in_category:
            return random.choice(merchants_in_category)
        
        # Only use CSV merchants if NO realistic merchants exist for this category
        # AND filter out generic merchant names
        if self.merchant_pool:
            csv_merchants = []
            category_lower = category.lower()
            category_parts = category_lower.split('/')
            primary_category = category_parts[0].strip()
            secondary_category = category_parts[1].strip() if len(category_parts) > 1 else None
            
            for m in self.merchant_pool:
                if not isinstance(m, dict) or m.get("_is_realistic", False):
                    continue
                    
                merchant_cat = m.get("category", "").lower()
                if not merchant_cat:
                    continue
                
                # Match categories more precisely
                merchant_parts = merchant_cat.split('/')
                merchant_primary = merchant_parts[0].strip()
                merchant_secondary = merchant_parts[1].strip() if len(merchant_parts) > 1 else None
                
                # Match if primary category matches
                if merchant_primary == primary_category:
                    # If both have secondary categories, they should match
                    if secondary_category and merchant_secondary:
                        if secondary_category in merchant_secondary or merchant_secondary in secondary_category:
                            csv_merchants.append(m)
                    # If only one has secondary, only match if we're looking for primary only
                    elif not secondary_category:
                        csv_merchants.append(m)
                    # If we're looking for specific secondary but merchant doesn't have it, skip
                    elif secondary_category and not merchant_secondary:
                        continue
            # Filter out generic merchant names from CSV
            # These patterns catch generic placeholder merchants that should be replaced with realistic ones
            generic_patterns = [
                "rideshareco", "mobilecarrier", "quickfuel", "parkinglot", 
                "streamflix", "beerbarn", "citytransit", "payutilities",
                "craftsonline", "electrohub", "hardwarepro", "officesupply",
                "toyhouse", "petworld", "movierentals", "subscriptionbox",
                "concerthall", "discountoutlets", "luxuryboutique",
                "student loan payment", "student loan",
                # Catch patterns like "OfficeSupply Co #3", "PetWorld #1", etc.
                "officesupply co", "petworld", "movierentals", "subscriptionbox",
                "concerthall", "discountoutlets", "craftsonline", "luxuryboutique",
                "citytransit", "parkinglot inc", "parkinglot",
                # Generic patterns with numbers
                "co #", "inc #", "pro #", "lot #", "transit #", "world #",
                "online #", "outlet #", "hall #", "rental #"
            ]
            merchants_in_category = [
                m for m in csv_merchants
                if not any(generic in m.get("name", "").lower() for generic in generic_patterns)
            ]
        
        return random.choice(merchants_in_category) if merchants_in_category else None
    
    def _generate_special_transactions(self, accounts, start_date, end_date):
        """Generates special transaction types like income, credit card payments, and transfers."""
        transactions = []
        tx_config = self.config.get("transactions", {})
        history_days = (end_date - start_date).days
        
        for pattern in tx_config.get("patterns", []):
            if "payment_type" not in pattern:
                continue
                
            num_months = history_days / 30
            freq_min, freq_max = pattern.get("frequency_per_month", [1, 1])
            num_transactions = int(random.uniform(freq_min, freq_max) * num_months)

            for _ in range(num_transactions):
                amount = self._get_random_value(pattern.get("amount_range", [50, 200]))

                if pattern["payment_type"] == "income":
                    # Income deposits: positive amounts, PAYROLL category, ACH channel
                    merchant_name = random.choice([
                        "Direct Deposit",
                        "Payroll Deposit",
                        "Salary Deposit",
                        "Employer Payroll",
                        "ACH Deposit"
                    ])
                    category_primary = "PAYROLL"
                    category_detailed = "PAYROLL"
                    account_id = self._get_random_account(accounts, ["checking"])
                    # Amount should be positive for deposits (Plaid convention)
                    payment_channel = "ACH"
                elif pattern["payment_type"] == "transfer_to_savings":
                    # Create transfer out from checking (negative)
                    checking_account_id = self._get_random_account(accounts, ["checking"])
                    savings_account_id = self._get_random_account(accounts, ["savings"])

                    if not savings_account_id:
                        continue

                    # First transaction: transfer out from checking (negative)
                    date = self.faker.date_between(start_date=start_date, end_date=end_date)
                    transaction_out = {
                        "transaction_id": f"txn-{uuid.uuid4()}",
                        "account_id": checking_account_id,
                        "datetime": self._get_datetime_for_category(date, "Transfer"),
                        "amount": -abs(amount),
                        "merchant_name": "Transfer to Savings",
                        "merchant_entity_id": None,
                        "payment_channel": "other",
                        "personal_finance_category": {
                            "primary": "GENERAL_MERCHANDISE",
                            "detailed": "TRANSFER_OUT",
                        },
                        "pending": False,
                        "iso_currency_code": "USD",
                    }
                    transactions.append(transaction_out)

                    # Second transaction: transfer in to savings (positive)
                    transaction_in = {
                        "transaction_id": f"txn-{uuid.uuid4()}",
                        "account_id": savings_account_id,
                        "datetime": transaction_out["datetime"],
                        "amount": abs(amount),
                        "merchant_name": "Transfer from Checking",
                        "merchant_entity_id": None,
                        "payment_channel": "other",
                        "personal_finance_category": {
                            "primary": "GENERAL_MERCHANDISE",
                            "detailed": "TRANSFER_IN",
                        },
                        "pending": False,
                        "iso_currency_code": "USD",
                    }
                    transactions.append(transaction_in)
                    continue  # Skip creating the single transaction below
                elif pattern["payment_type"] == "credit_card_payment":
                    merchant_name = "Credit Card Payment"
                    category_primary = "GENERAL_MERCHANDISE"
                    category_detailed = "CREDIT_CARD_PAYMENT"
                    account_id = self._get_random_account(accounts, ["checking"])
                    amount = -abs(amount)
                    payment_channel = "other"
                elif pattern["payment_type"] == "loan_payment":
                    # Use realistic loan servicer names
                    if pattern.get("loan_type") == "student":
                        loan_servicers = ["Navient", "Great Lakes", "FedLoan Servicing", "Nelnet", "MOHELA", "Aidvantage"]
                        merchant_name = random.choice(loan_servicers)
                    else:
                        merchant_name = f"{pattern['loan_type'].title()} Loan Payment"
                    category_primary = "GENERAL_MERCHANDISE"
                    category_detailed = "LOAN_PAYMENT"
                    account_id = self._get_random_account(accounts, ["checking"])
                    amount = -abs(amount)
                    payment_channel = "other"
                else:
                    continue  # Skip unknown payment types

                date = self.faker.date_between(start_date=start_date, end_date=end_date)
                transaction = {
                    "transaction_id": f"txn-{uuid.uuid4()}",
                    "account_id": account_id,
                    "datetime": self._get_datetime_for_category(date, category_primary),
                    "amount": amount,
                    "merchant_name": merchant_name,
                    "merchant_entity_id": None,
                    "payment_channel": payment_channel,
                    "personal_finance_category": {
                        "primary": category_primary,
                        "detailed": category_detailed,
                    },
                    "pending": False,
                    "iso_currency_code": "USD",
                }
                transactions.append(transaction)
        
        return transactions

    def _generate_transaction_stories(self, accounts, start_date, end_date):
        """Generates logical sequences of transactions, like a travel story."""
        transactions = []
        # Decide if this user will have a travel story (e.g., 25% chance)
        if random.random() < 0.25:
            # Pick a random travel date (convert to datetime)
            travel_start_date_raw = self.faker.date_between(start_date=start_date + timedelta(days=30), end_date=end_date - timedelta(days=10))
            travel_start_date = datetime.combine(travel_start_date_raw, datetime.min.time())
            
            # 1. Book a flight
            flight_merchants = [
                {"name": "Delta Airlines", "category": "Travel/Airfare", "amount_range": [250, 800], "payment_channels": ["online"]},
                {"name": "United Airlines", "category": "Travel/Airfare", "amount_range": [250, 800], "payment_channels": ["online"]},
                {"name": "American Airlines", "category": "Travel/Airfare", "amount_range": [250, 800], "payment_channels": ["online"]},
            ]
            flight_merchant = random.choice(flight_merchants)
            flight_tx = {
                "transaction_id": f"txn-{uuid.uuid4()}",
                "account_id": self._get_random_account(accounts, ["credit card"]),
                "datetime": self._get_datetime_for_category(travel_start_date - timedelta(days=random.randint(14, 45)), "Travel"),
                "amount": -abs(self._get_random_value(flight_merchant["amount_range"])),
                "merchant_name": flight_merchant["name"],
                "merchant_entity_id": None,
                "payment_channel": "online",
                "personal_finance_category": {"primary": "TRAVEL", "detailed": "TRAVEL/AIRFARE"},
                "pending": False,
                "iso_currency_code": "USD",
            }
            transactions.append(flight_tx)
            
            # 2. During the trip (3-7 days), add lodging, food, and transport
            trip_duration = random.randint(3, 7)
            destination_city = "New York" # Could be randomized further
            
            # Lodging
            lodging_merchants = [
                {"name": "Marriott", "category": "Travel/Lodging", "amount_range": [150, 400], "payment_channels": ["in_store"]},
                {"name": "Hilton", "category": "Travel/Lodging", "amount_range": [150, 400], "payment_channels": ["in_store"]},
                {"name": "Airbnb", "category": "Travel/Lodging", "amount_range": [100, 300], "payment_channels": ["online"]},
            ]
            lodging_merchant = random.choice(lodging_merchants)
            lodging_tx = {
                "transaction_id": f"txn-{uuid.uuid4()}",
                "account_id": self._get_random_account(accounts, ["credit card"]),
                "datetime": self._get_datetime_for_category(travel_start_date, "Travel"),
                "amount": -abs(self._get_random_value(lodging_merchant["amount_range"])) * trip_duration,
                "merchant_name": f"{lodging_merchant['name']} - {destination_city.upper()}",
                "merchant_entity_id": None,
                "payment_channel": random.choice(lodging_merchant["payment_channels"]),
                "personal_finance_category": {"primary": "TRAVEL", "detailed": "TRAVEL/LODGING"},
                "pending": False,
                "iso_currency_code": "USD",
            }
            transactions.append(lodging_tx)
            
            # Food and Transport during trip
            for day in range(trip_duration):
                trip_date = travel_start_date + timedelta(days=day)
                # 1-3 food/transport transactions per day
                for _ in range(random.randint(1, 3)):
                    category = random.choice(["Food & Drink/Restaurants", "Transport/Rideshare"])
                    merchant_options = {
                        "Food & Drink/Restaurants": [{"name": "Local Restaurant", "amount_range": [20, 80], "payment_channels": ["in_store"]}],
                        "Transport/Rideshare": [{"name": "Uber", "amount_range": [15, 40], "payment_channels": ["mobile"]}, {"name": "Lyft", "amount_range": [15, 40], "payment_channels": ["mobile"]}],
                    }
                    merchant = random.choice(merchant_options[category])
                    # Map payment channels
                    payment_channel_raw = random.choice(merchant["payment_channels"])
                    payment_channel_map = {"mobile": "online", "contactless": "in_store", "online": "online", "in_store": "in_store", "other": "other"}
                    payment_channel = payment_channel_map.get(payment_channel_raw, "other")
                    tx = {
                        "transaction_id": f"txn-{uuid.uuid4()}",
                        "account_id": self._get_random_account(accounts, ["credit card"]),
                        "datetime": self._get_datetime_for_category(trip_date, category),
                        "amount": -abs(self._get_random_value(merchant["amount_range"])),
                        "merchant_name": f"{merchant['name']} - {destination_city.upper()}",
                        "merchant_entity_id": None,
                        "payment_channel": payment_channel,
                        "personal_finance_category": {"primary": category.split('/')[0].upper(), "detailed": category.upper().replace(' ', '_')},
                        "pending": False,
                        "iso_currency_code": "USD",
                    }
                    transactions.append(tx)

        return transactions

    def _generate_general_spending(self, accounts, start_date, end_date):
        """Generates general, randomized spending transactions based on persona patterns."""
        transactions = []
        tx_config = self.config.get("transactions", {})
        history_days = (end_date - start_date).days

        non_recurring_patterns = [p for p in tx_config.get("patterns", []) if not self._is_recurring(p)]

        for pattern in non_recurring_patterns:
            if "category" not in pattern:
                continue

            num_months = history_days / 30
            freq_min, freq_max = pattern.get("frequency_per_month", [1, 1])
            num_transactions = int(random.uniform(freq_min, freq_max) * num_months)

            for _ in range(num_transactions):
                date = self.faker.date_between(start_date=start_date, end_date=end_date)
                
                # Boost weekend spending for certain categories
                is_weekend = date.weekday() >= 5 # Saturday or Sunday
                if "Restaurant" in pattern["category"] or "Bar" in pattern["category"] or "Entertainment" in pattern["category"]:
                    if is_weekend and random.random() < 0.4: # 40% chance of extra weekend transaction
                        num_transactions += 1

                merchant = self._get_merchant_for_pattern(pattern)
                if not merchant:
                    continue

                amount = -abs(self._get_random_value(merchant.get("amount_range") or pattern.get("amount_range", [10, 100])))
                # Map payment channels to valid Plaid values
                payment_channel_raw = random.choice(merchant.get("payment_channels", ["in_store", "online"]))
                payment_channel_map = {
                    "mobile": "online",
                    "contactless": "in_store",
                    "online": "online",
                    "in_store": "in_store",
                    "other": "other",
                    "ACH": "ACH"
                }
                payment_channel = payment_channel_map.get(payment_channel_raw, "other")
                
                merchant_name = merchant["name"]
                if merchant.get("type") in ["national_chain", "regional"]:
                    merchant_name = f"{merchant['name']} #{self.faker.numerify('####')} - {self.home_city.upper()}"

                tx = {
                    "transaction_id": f"txn-{uuid.uuid4()}",
                    "account_id": self._get_random_account(accounts, ["checking", "credit card"]),
                    "datetime": self._get_datetime_for_category(date, merchant["category"]),
                    "amount": amount,
                    "merchant_name": merchant_name,
                    "merchant_entity_id": None,
                    "payment_channel": payment_channel,
                    "personal_finance_category": {
                        "primary": merchant["category"].split('/')[0],
                        "detailed": merchant["category"],
                    },
                    "pending": False,
                    "iso_currency_code": "USD",
                }
                transactions.append(tx)

        return transactions

    def _add_refunds(self, transactions):
        """Adds refunds for a small percentage of retail transactions."""
        refunds = []
        # Find original transactions that are eligible for a refund
        refundable_txs = [
            tx for tx in transactions 
            if "Retail" in tx["personal_finance_category"]["primary"] and tx["amount"] < 0
        ]

        # Create refunds for about 2% of eligible transactions
        for original_tx in refundable_txs:
            if random.random() < 0.02:
                refund_date = original_tx["datetime"] + timedelta(days=random.randint(2, 7))
                if refund_date > datetime.now():
                    continue # Don't create refunds in the future

                refund_tx = {
                    "transaction_id": f"txn-{uuid.uuid4()}",
                    "account_id": original_tx["account_id"],
                    "datetime": self._get_datetime_for_category(refund_date, "Retail"),
                    "amount": abs(original_tx["amount"]), # Positive amount for refund
                    "merchant_name": f"Refund: {original_tx['merchant_name']}",
                    "merchant_entity_id": None,
                    "payment_channel": original_tx["payment_channel"],
                    "personal_finance_category": {
                        "primary": "GENERAL_SERVICES",
                        "detailed": "GENERAL_SERVICES/REFUNDS",
                    },
                    "pending": False,
                    "iso_currency_code": "USD",
                }
                refunds.append(refund_tx)
        
        return transactions + refunds

    def _mark_pending_transactions(self, transactions):
        """Marks the most recent 1-3 transactions as pending."""
        # Sort by date descending to easily find the most recent
        transactions.sort(key=lambda x: x["datetime"], reverse=True)
        
        num_to_mark_pending = random.randint(1, 3)
        for i in range(min(num_to_mark_pending, len(transactions))):
            # Only mark recent transactions (within last 3 days) as pending
            if transactions[i]["datetime"] > datetime.now() - timedelta(days=3):
                transactions[i]["pending"] = True
                
        return transactions
        
    def _generate_liabilities(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates a list of liabilities based on the persona configuration and accounts."""
        liabilities = []
        liability_configs = self.config.get("liabilities", {})

        for account in accounts:
            if account["type"] == "credit" and "credit_card" in liability_configs:
                config = liability_configs["credit_card"]
                last_payment_date = (datetime.now() - timedelta(days=random.randint(15, 25))).strftime("%Y-%m-%d")

                liability = {
                    "account_id": account["account_id"],
                    "aprs": [{
                        "apr_percentage": self._get_random_value(account.get("apr_range", [18, 28])),
                        "apr_type": "purchase_apr"
                    }],
                    "is_overdue": config.get("is_overdue", False),
                    "last_payment_amount": account["balances"]["current"] * random.uniform(0.1, 0.5), # Assume last payment was a fraction of balance
                    "last_payment_date": last_payment_date,
                    "last_statement_balance": account["balances"]["current"] / random.uniform(0.8, 1.0),
                    "minimum_payment_amount": account["balances"]["current"] * 0.05, # ~5% of balance
                    "next_payment_due_date": (datetime.now() + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d"),
                }
                liabilities.append(liability)

            elif account["type"] == "loan" and account["subtype"] in liability_configs:
                config = liability_configs[account["subtype"]]
                liability = {
                    "account_id": account["account_id"],
                    "interest_rate_percentage": self._get_random_value(config["interest_rate_range"]),
                    "next_payment_due_date": (datetime.now() + timedelta(days=random.randint(5, 25))).strftime("%Y-%m-%d"),
                    # ... other loan-specific fields can be added ...
                }
                liabilities.append(liability)

        return liabilities

    def _get_random_account(self, accounts: List[Dict[str, Any]], subtypes: List[str]) -> str:
        """Gets a random account ID of a given subtype."""
        eligible_accounts = [acc for acc in accounts if acc["subtype"] in subtypes]
        if not eligible_accounts:
            # Fallback to any account if no specific subtype is found
            return random.choice(accounts)["account_id"]
        return random.choice(eligible_accounts)["account_id"]

    def validate_and_export(self, profiles: List[Dict[str, Any]], output_dir: str, format: str):
        """Validates the generated profiles and exports them to the specified format."""
        logger.info(f"Starting validation and export for {len(profiles)} profiles.")

        for i, profile in enumerate(profiles):
            # Generate a unique ID for this profile's filename (not included in the JSON)
            file_id = str(uuid.uuid4())
            logger.info(f"Validating profile {i+1}/{len(profiles)} (file_id: {file_id})...")

            is_valid, errors = self.validator.validate(profile)

            if not is_valid:
                logger.error(f"Validation FAILED for profile {i+1} (file_id: {file_id}).")
                for error in errors:
                    logger.error(f"  - {error.to_dict()}")
                # Decide whether to skip export for invalid profiles
                continue

            logger.info(f"Validation PASSED for profile {i+1} (file_id: {file_id}).")

            # --- Exporting ---
            if format == "json" or format == "both":
                self._export_to_json(profile, output_dir, file_id)
            if format == "csv" or format == "both":
                self._export_to_csv(profile, output_dir, file_id)

        logger.info("Export process completed.")

    def _export_to_json(self, profile: Dict[str, Any], output_dir: str, file_id: str):
        """Exports a single profile to a JSON file.
        
        Args:
            profile: Profile dictionary (without user_id)
            output_dir: Output directory
            file_id: Unique identifier for the filename (UUID string)
        """
        filepath = os.path.join(output_dir, f"{file_id}.json")
        logger.info(f"Exporting profile to {filepath}...")
        with open(filepath, "w") as f:
            json.dump(profile, f, indent=2)

    def _export_to_csv(self, profile: Dict[str, Any], output_dir: str, file_id: str):
        """Exports a single profile to multiple CSV files (accounts, transactions, liabilities).
        
        Args:
            profile: Profile dictionary (without user_id)
            output_dir: Output directory
            file_id: Unique identifier for the filename (UUID string)
        """
        logger.info(f"Exporting profile to CSV files in {output_dir} (file_id: {file_id})...")

        # Export Accounts
        if profile["accounts"]:
            accounts_path = os.path.join(output_dir, f"{file_id}_accounts.csv")
            with open(accounts_path, "w", newline="") as f:
                writer = csv.writer(f)
                # Header
                header = profile["accounts"][0].keys()
                writer.writerow(header)
                # Rows
                for account in profile["accounts"]:
                    writer.writerow(account.values())

        # Export Transactions
        if profile["transactions"]:
            transactions_path = os.path.join(output_dir, f"{file_id}_transactions.csv")
            with open(transactions_path, "w", newline="") as f:
                writer = csv.writer(f)
                header = profile["transactions"][0].keys()
                writer.writerow(header)
                for tx in profile["transactions"]:
                    writer.writerow(tx.values())

        # Export Liabilities
        if profile["liabilities"]:
            liabilities_path = os.path.join(output_dir, f"{file_id}_liabilities.csv")
            with open(liabilities_path, "w", newline="") as f:
                writer = csv.writer(f)
                header = profile["liabilities"][0].keys()
                writer.writerow(header)
                for liability in profile["liabilities"]:
                    writer.writerow(liability.values())


# --- Command-Line Interface ---

def main():
    """Main function to run the data generator from the command line."""
    parser = argparse.ArgumentParser(description="Synthetic Plaid Data Generator")
    parser.add_argument(
        "config_dir",
        type=str,
        help="Directory containing the persona YAML configuration files.",
    )
    parser.add_argument(
        "transactions_csv",
        type=str,
        help="Path to the CSV file containing sample transactions for realistic merchant data.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="synthetic_data",
        help="Directory to save the generated data files.",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "both"],
        default="json",
        help="Output format for the generated data.",
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Process each config file in the directory
    for filename in os.listdir(args.config_dir):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            config_path = os.path.join(args.config_dir, filename)

            generator = SyntheticDataGenerator(config_path, args.transactions_csv)
            profiles = generator.generate_profiles()
            generator.validate_and_export(profiles, args.output_dir, args.format)

if __name__ == "__main__":
    main()
