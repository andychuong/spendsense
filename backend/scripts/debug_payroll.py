#!/usr/bin/env python3
"""Debug payroll transaction detection."""

import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.account import Account
from sqlalchemy import and_, or_, func
from datetime import date, timedelta

db = SessionLocal()
try:
    # Get first checking account
    account = db.query(Account).filter(
        Account.type == 'depository',
        Account.subtype == 'checking'
    ).first()
    
    if not account:
        print('No checking accounts found')
        sys.exit(1)
    
    user_id = account.user_id
    account_ids = [account.id]
    
    print(f'User: {user_id}')
    print(f'Account ID: {account.id}')
    
    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    
    print(f'\nDate range: {start_date} to {end_date}')
    
    # Check for PAYROLL category transactions
    payroll_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.account_id.in_(account_ids),
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.amount > 0,
        Transaction.category_primary == "PAYROLL"
    ).all()
    
    print(f'\n1. Transactions with category_primary == "PAYROLL": {len(payroll_txns)}')
    
    if payroll_txns:
        print('\nSample PAYROLL transactions:')
        for t in payroll_txns[:5]:
            print(f'  Date: {t.date}, Amount: {t.amount}')
            print(f'    Category Primary: "{t.category_primary}"')
            print(f'    Category Detailed: "{t.category_detailed}"')
            print(f'    Payment Channel: "{t.payment_channel}"')
            print(f'    Merchant: "{t.merchant_name}"')
            print(f'    Pending: {t.pending}')
            print()
    
    # Now test the actual query from income.py
    print('\n2. Testing the actual query from income.py:')
    payroll_transactions = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.account_id.in_(account_ids),
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount > 0,
            Transaction.pending == False,
            or_(
                Transaction.category_primary == "PAYROLL",
                Transaction.category_primary.like("%PAYROLL%"),
                Transaction.category_detailed == "PAYROLL",
                Transaction.category_detailed.like("%PAYROLL%"),
                Transaction.category_detailed == "Financial/Income",
                Transaction.category_detailed.like("%Income%"),
                and_(
                    Transaction.merchant_name.isnot(None),
                    or_(
                        Transaction.merchant_name.like("%Direct Deposit%"),
                        Transaction.merchant_name.like("%Payroll%"),
                        Transaction.merchant_name.like("%Salary%"),
                    ),
                ),
            ),
            or_(
                Transaction.payment_channel == "ACH",
                Transaction.payment_channel == "online",
            ),
        )
    ).all()
    
    print(f'Found {len(payroll_transactions)} transactions with full query')
    
    if len(payroll_transactions) == 0 and len(payroll_txns) > 0:
        print('\n⚠️  ISSUE FOUND: Query is filtering out transactions!')
        print('Checking which filter is causing the issue...\n')
        
        # Test each condition
        test1 = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.account_id.in_(account_ids),
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount > 0,
            Transaction.pending == False,
            Transaction.category_primary == "PAYROLL",
        ).count()
        print(f'  With pending==False: {test1}')
        
        test2 = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.account_id.in_(account_ids),
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount > 0,
            Transaction.category_primary == "PAYROLL",
            or_(
                Transaction.payment_channel == "ACH",
                Transaction.payment_channel == "online",
            ),
        ).count()
        print(f'  With payment channel filter: {test2}')
        
        # Check payment channels
        channels = db.query(
            Transaction.payment_channel,
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.account_id.in_(account_ids),
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount > 0,
            Transaction.category_primary == "PAYROLL",
        ).group_by(Transaction.payment_channel).all()
        
        print(f'\n  Payment channels for PAYROLL transactions:')
        for ch, cnt in channels:
            print(f'    "{ch}": {cnt}')
    
finally:
    db.close()


