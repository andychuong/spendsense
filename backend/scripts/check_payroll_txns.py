#!/usr/bin/env python3
"""Check payroll transactions in database."""

import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.account import Account
from datetime import date, timedelta

db = SessionLocal()
try:
    account = db.query(Account).filter(
        Account.type == 'depository',
        Account.subtype == 'checking'
    ).first()
    
    if not account:
        print('No checking accounts found')
        sys.exit(1)
    
    user_id = account.user_id
    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    
    print(f'User: {user_id}')
    print(f'Account: {account.id}')
    print(f'Date range: {start_date} to {end_date}')
    
    # Get all positive transactions
    all_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.account_id == account.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.amount > 0,
    ).limit(10).all()
    
    print(f'\nFound {len(all_txns)} positive transactions:')
    
    for t in all_txns:
        print(f'\n  Date: {t.date}, Amount: {t.amount}')
        print(f'    Category Primary: "{t.category_primary}"')
        print(f'    Category Detailed: "{t.category_detailed}"')
        print(f'    Payment Channel: "{t.payment_channel}"')
        print(f'    Merchant: "{t.merchant_name}"')
        print(f'    Pending: {t.pending}')
    
    # Check specifically for PAYROLL
    payroll_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.account_id == account.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.amount > 0,
        Transaction.category_primary == "PAYROLL",
    ).all()
    
    print(f'\n\nFound {len(payroll_txns)} transactions with category_primary == "PAYROLL"')
    
finally:
    db.close()


