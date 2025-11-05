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

# Add paths for imports
import sys
import os
_current_file = os.path.abspath(__file__)
_project_root = os.path.dirname(os.path.dirname(_current_file))
_backend_dir = os.path.join(_project_root, "backend")
_service_dir = os.path.join(_project_root, "service")

# Add backend first (service depends on it), then service
for path in [_backend_dir, _service_dir]:
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

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads a YAML configuration file."""
        logger.info(f"Loading persona configuration from: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

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
            logger.info(f"Loaded {len(pool)} merchants into the pool.")
            return pool
        except FileNotFoundError:
            logger.warning(f"Transactions CSV not found at {path}. Transaction generation will be less realistic.")
            return []
        except Exception as e:
            logger.error(f"Error loading merchant pool: {e}")
            return[]

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

        for acc_config in account_configs:
            account_id = f"acct-{uuid.uuid4()}"
            balance = self._get_random_value(acc_config["balance_range"])
            limit = self._get_random_value(acc_config["limit_range"]) if "limit_range" in acc_config else None

            account = {
                "account_id": account_id,
                "name": f"{self.faker.company()} {acc_config['subtype'].replace('_', ' ').title()}",
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

        Plaid Transaction Amount Convention:
        - Deposits (income, transfers in) = POSITIVE amounts (money entering account)
        - Expenses (purchases, payments, transfers out) = NEGATIVE amounts (money leaving account)

        This matches Plaid's API where deposits increase account balance and expenses decrease it.
        """
        transactions = []
        tx_config = self.config.get("transactions", {})
        history_days = tx_config.get("history_days", 180)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=history_days)

        for pattern in tx_config.get("patterns", []):
            if "category" in pattern and self.merchant_pool:
                # Generate general spending transactions
                merchants_in_category = [m for m in self.merchant_pool if pattern["category"] in m["category"]]
                if not merchants_in_category:
                    continue

                num_months = history_days / 30
                freq_min, freq_max = pattern.get("frequency_per_month", [1,1])
                num_transactions = int(random.uniform(freq_min, freq_max) * num_months)

                for _ in range(num_transactions):
                    merchant = random.choice(merchants_in_category)
                    # Spending transactions are negative amounts (money leaving account)
                    amount = -abs(self._get_random_value(pattern["amount_range"]))
                    transaction = {
                        "transaction_id": f"txn-{uuid.uuid4()}",
                        "account_id": self._get_random_account(accounts, ["checking", "credit card"]),
                        "date": self.faker.date_between(start_date=start_date, end_date=end_date).strftime("%Y-%m-%d"),
                        "amount": amount,
                        "merchant_name": merchant["name"],
                        "merchant_entity_id": None, # Can be enhanced later
                        "payment_channel": random.choice(["online", "in_store", "other"]),
                        "personal_finance_category": {
                            "primary": merchant["category"].split('/')[0],
                            "detailed": merchant["category"],
                        },
                        "pending": False,
                        "iso_currency_code": "USD",
                    }
                    transactions.append(transaction)

            elif "payment_type" in pattern:
                # Generate special transaction types
                num_months = history_days / 30
                freq_min, freq_max = pattern.get("frequency_per_month", [1,1])
                num_transactions = int(random.uniform(freq_min, freq_max) * num_months)

                for _ in range(num_transactions):
                    amount = self._get_random_value(pattern.get("amount_range", [50, 200])) # Default amount

                    # Custom logic for each payment type
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
                        # Don't negate - deposits are positive amounts
                        payment_channel = "ACH"
                    elif pattern["payment_type"] == "transfer_to_savings":
                        # Create transfer out from checking (negative)
                        checking_account_id = self._get_random_account(accounts, ["checking"])
                        savings_account_id = self._get_random_account(accounts, ["savings"])

                        # First transaction: transfer out from checking (negative)
                        transaction_out = {
                            "transaction_id": f"txn-{uuid.uuid4()}",
                            "account_id": checking_account_id,
                            "date": self.faker.date_between(start_date=start_date, end_date=end_date).strftime("%Y-%m-%d"),
                            "amount": -abs(amount),  # Negative - money leaving checking
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
                            "date": transaction_out["date"],  # Same date as transfer out
                            "amount": abs(amount),  # Positive - money entering savings
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

                        # Skip creating the single transaction below, we already created both
                        continue
                    elif pattern["payment_type"] == "credit_card_payment":
                        merchant_name = "Credit Card Payment"
                        category_primary = "GENERAL_MERCHANDISE"
                        category_detailed = "CREDIT_CARD_PAYMENT"
                        account_id = self._get_random_account(accounts, ["checking"])
                        # Payments are negative amounts (money leaving checking)
                        amount = -abs(amount)
                        payment_channel = "other"
                    elif pattern["payment_type"] == "loan_payment":
                        merchant_name = f"{pattern['loan_type'].title()} Loan Payment"
                        category_primary = "GENERAL_MERCHANDISE"
                        category_detailed = "LOAN_PAYMENT"
                        account_id = self._get_random_account(accounts, ["checking"])
                        # Payments are negative amounts (money leaving checking)
                        amount = -abs(amount)
                        payment_channel = "other"
                    else:
                        continue # Skip unknown payment types

                    transaction = {
                        "transaction_id": f"txn-{uuid.uuid4()}",
                        "account_id": account_id,
                        "date": self.faker.date_between(start_date=start_date, end_date=end_date).strftime("%Y-%m-%d"),
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

        # Sort transactions by date
        transactions.sort(key=lambda x: x["date"])
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
