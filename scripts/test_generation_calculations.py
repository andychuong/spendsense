#!/usr/bin/env python3
"""Test data generation and calculate income, credit card spending, and liability payments."""

import json
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Add paths for imports
_current_file = os.path.abspath(__file__)
_project_root = os.path.dirname(os.path.dirname(_current_file))
_backend_dir = os.path.join(_project_root, "backend")
_service_dir = os.path.join(_project_root, "service")

for path in [_backend_dir, _service_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from synthetic_data_generator import SyntheticDataGenerator

def calculate_financial_metrics(profile_data):
    """Calculate income, credit card spending, and liability payments from generated profile."""

    user_id = profile_data["user_id"]
    accounts = profile_data["accounts"]
    transactions = profile_data["transactions"]
    liabilities = profile_data["liabilities"]

    # Get account IDs by type
    checking_account_ids = {acc["account_id"] for acc in accounts if acc["subtype"] == "checking"}
    credit_card_account_ids = {acc["account_id"] for acc in accounts if acc["subtype"] == "credit card"}

    # Calculate income (positive amounts, PAYROLL category, in checking accounts)
    income_transactions = [
        t for t in transactions
        if t["account_id"] in checking_account_ids
        and t.get("amount", 0) > 0
        and t.get("personal_finance_category", {}).get("primary") == "PAYROLL"
    ]

    total_income = sum(float(t["amount"]) for t in income_transactions)
    income_count = len(income_transactions)

    # Calculate average monthly income
    if income_transactions:
        # Get date range
        dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in income_transactions]
        min_date = min(dates)
        max_date = max(dates)
        months = max((max_date - min_date).days / 30.0, 1.0)
        avg_monthly_income = total_income / months
    else:
        avg_monthly_income = 0
        months = 0

    # Calculate credit card spending (negative amounts on credit card accounts)
    credit_card_spending = [
        t for t in transactions
        if t["account_id"] in credit_card_account_ids
        and t.get("amount", 0) < 0
    ]

    total_cc_spending = abs(sum(float(t["amount"]) for t in credit_card_spending))
    cc_spending_count = len(credit_card_spending)

    # Calculate average monthly credit card spending
    if credit_card_spending:
        dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in credit_card_spending]
        min_date = min(dates)
        max_date = max(dates)
        months_cc = max((max_date - min_date).days / 30.0, 1.0)
        avg_monthly_cc_spending = total_cc_spending / months_cc
    else:
        avg_monthly_cc_spending = 0
        months_cc = 0

    # Calculate liability payments (credit card payments and loan payments)
    cc_payments = [
        t for t in transactions
        if t["account_id"] in checking_account_ids
        and t.get("amount", 0) < 0
        and "CREDIT_CARD_PAYMENT" in t.get("personal_finance_category", {}).get("detailed", "")
    ]

    loan_payments = [
        t for t in transactions
        if t["account_id"] in checking_account_ids
        and t.get("amount", 0) < 0
        and "LOAN_PAYMENT" in t.get("personal_finance_category", {}).get("detailed", "")
    ]

    total_cc_payments = abs(sum(float(t["amount"]) for t in cc_payments))
    total_loan_payments = abs(sum(float(t["amount"]) for t in loan_payments))
    total_liability_payments = total_cc_payments + total_loan_payments

    # Calculate average monthly liability payments
    all_payments = cc_payments + loan_payments
    if all_payments:
        dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in all_payments]
        min_date = min(dates)
        max_date = max(dates)
        months_payments = max((max_date - min_date).days / 30.0, 1.0)
        avg_monthly_liability_payments = total_liability_payments / months_payments
    else:
        avg_monthly_liability_payments = 0
        months_payments = 0

    # Calculate liability minimum payments from liability data
    liability_minimums = []
    for liability in liabilities:
        if "minimum_payment_amount" in liability:
            liability_minimums.append(float(liability["minimum_payment_amount"]))

    total_monthly_minimums = sum(liability_minimums)

    return {
        "user_id": user_id,
        "income": {
            "total_income": total_income,
            "income_transactions": income_count,
            "avg_monthly_income": avg_monthly_income,
            "months_covered": months,
        },
        "credit_card_spending": {
            "total_spending": total_cc_spending,
            "transactions": cc_spending_count,
            "avg_monthly_spending": avg_monthly_cc_spending,
            "months_covered": months_cc,
        },
        "liability_payments": {
            "total_cc_payments": total_cc_payments,
            "total_loan_payments": total_loan_payments,
            "total_payments": total_liability_payments,
            "avg_monthly_payments": avg_monthly_liability_payments,
            "months_covered": months_payments,
            "monthly_minimums": total_monthly_minimums,
        },
    }

def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"

def main():
    """Generate test data and calculate metrics."""
    print("=" * 80)
    print("Synthetic Data Generation Test - Financial Metrics Calculation")
    print("=" * 80)
    print()

    # Use the high utilization persona config
    config_path = os.path.join(
        os.path.dirname(__file__),
        "persona_configs",
        "1_high_utilization.yaml"
    )

    transactions_csv = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "docs",
        "support",
        "transactions_100_users_2024.csv"
    )

    print(f"Loading configuration: {config_path}")
    print(f"Loading merchant pool: {transactions_csv}")
    print()

    # Generate a single profile
    generator = SyntheticDataGenerator(config_path, transactions_csv)
    profiles = generator.generate_profiles()

    if not profiles:
        print("ERROR: No profiles generated!")
        return

    # We'll use the first profile
    profile = profiles[0]

    print(f"Generated profile for user: {profile['user_id']}")
    print(f"Total accounts: {len(profile['accounts'])}")
    print(f"Total transactions: {len(profile['transactions'])}")
    print(f"Total liabilities: {len(profile['liabilities'])}")
    print()

    # Calculate metrics
    metrics = calculate_financial_metrics(profile)

    # Display results
    print("=" * 80)
    print("FINANCIAL METRICS CALCULATIONS")
    print("=" * 80)
    print()

    # Income
    print("📊 INCOME (Payroll Deposits)")
    print("-" * 80)
    print(f"  Total Income:              {format_currency(metrics['income']['total_income'])}")
    print(f"  Income Transactions:       {metrics['income']['income_transactions']}")
    print(f"  Months Covered:            {metrics['income']['months_covered']:.1f}")
    print(f"  Average Monthly Income:    {format_currency(metrics['income']['avg_monthly_income'])}")
    print()

    # Credit Card Spending
    print("💳 CREDIT CARD SPENDING")
    print("-" * 80)
    print(f"  Total Spending:           {format_currency(metrics['credit_card_spending']['total_spending'])}")
    print(f"  Credit Card Transactions:  {metrics['credit_card_spending']['transactions']}")
    print(f"  Months Covered:           {metrics['credit_card_spending']['months_covered']:.1f}")
    print(f"  Average Monthly Spending:  {format_currency(metrics['credit_card_spending']['avg_monthly_spending'])}")
    print()

    # Liability Payments
    print("💰 LIABILITY PAYMENTS")
    print("-" * 80)
    print(f"  Credit Card Payments:      {format_currency(metrics['liability_payments']['total_cc_payments'])}")
    print(f"  Loan Payments:             {format_currency(metrics['liability_payments']['total_loan_payments'])}")
    print(f"  Total Payments:            {format_currency(metrics['liability_payments']['total_payments'])}")
    print(f"  Months Covered:            {metrics['liability_payments']['months_covered']:.1f}")
    print(f"  Average Monthly Payments:  {format_currency(metrics['liability_payments']['avg_monthly_payments'])}")
    print(f"  Monthly Minimum Payments: {format_currency(metrics['liability_payments']['monthly_minimums'])}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Monthly Income:           {format_currency(metrics['income']['avg_monthly_income'])}")
    print(f"  Monthly CC Spending:       {format_currency(metrics['credit_card_spending']['avg_monthly_spending'])}")
    print(f"  Monthly Liability Payments: {format_currency(metrics['liability_payments']['avg_monthly_payments'])}")
    print(f"  Monthly Minimums:         {format_currency(metrics['liability_payments']['monthly_minimums'])}")
    print()

    # Ratio analysis
    if metrics['income']['avg_monthly_income'] > 0:
        cc_spending_ratio = (metrics['credit_card_spending']['avg_monthly_spending'] /
                            metrics['income']['avg_monthly_income']) * 100
        payment_ratio = (metrics['liability_payments']['avg_monthly_payments'] /
                        metrics['income']['avg_monthly_income']) * 100

        print("RATIOS")
        print("-" * 80)
        print(f"  CC Spending / Income:     {cc_spending_ratio:.1f}%")
        print(f"  Liability Payments / Income: {payment_ratio:.1f}%")
        print()

    print("=" * 80)
    print("✅ Test generation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

