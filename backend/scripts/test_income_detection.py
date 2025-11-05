#!/usr/bin/env python3
"""Test income detection for specific user."""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add service to path
_project_root = os.path.dirname(backend_path)
_service_dir = os.path.join(_project_root, "service")
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

from app.database import SessionLocal
from app.features.income import IncomeStabilityDetector
import uuid
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SessionLocal()
try:
    user_id_str = 'f1c7330d-6904-4129-9ae4-4c8007a6c7a3'
    user_id = uuid.UUID(user_id_str)
    
    print(f"Testing income detection for user: {user_id}")
    print("="*60)
    
    detector = IncomeStabilityDetector(db_session=db)
    
    # Test 30-day window
    print("\n30-day window:")
    signals_30d = detector.calculate_income_signals(user_id, window_days=30)
    
    payroll_deposits_30d = signals_30d.get('payroll_deposits', [])
    print(f"  Payroll deposits found: {len(payroll_deposits_30d)}")
    
    if payroll_deposits_30d:
        print(f"  Sample deposits:")
        for dep in payroll_deposits_30d[:3]:
            print(f"    - {dep['date']}: ${dep['amount']:.2f}")
    
    payment_frequency = signals_30d.get('payment_frequency', {})
    print(f"\n  Payment frequency: {payment_frequency.get('frequency_type', 'N/A')}")
    print(f"  Median gap days: {payment_frequency.get('median_gap_days', 'N/A')}")
    
    payment_variability = signals_30d.get('payment_variability', {})
    print(f"  Payment variability: {payment_variability.get('variability_level', 'N/A')}")
    print(f"  Mean amount: ${payment_variability.get('mean_amount', 0):.2f}")
    
    # Test 180-day window
    print("\n180-day window:")
    signals_180d = detector.calculate_income_signals(user_id, window_days=180)
    
    payroll_deposits_180d = signals_180d.get('payroll_deposits', [])
    print(f"  Payroll deposits found: {len(payroll_deposits_180d)}")
    
    if payroll_deposits_180d:
        print(f"  Sample deposits:")
        for dep in payroll_deposits_180d[:3]:
            print(f"    - {dep['date']}: ${dep['amount']:.2f}")
    
    payment_frequency = signals_180d.get('payment_frequency', {})
    print(f"\n  Payment frequency: {payment_frequency.get('frequency_type', 'N/A')}")
    print(f"  Median gap days: {payment_frequency.get('median_gap_days', 'N/A')}")
    
    payment_variability = signals_180d.get('payment_variability', {})
    print(f"  Payment variability: {payment_variability.get('variability_level', 'N/A')}")
    print(f"  Mean amount: ${payment_variability.get('mean_amount', 0):.2f}")
    
finally:
    db.close()

