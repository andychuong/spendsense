#!/usr/bin/env python3
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "..")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
print('📊 Database Summary:')
users = db.execute(text("SELECT COUNT(*) FROM users WHERE role = 'user'")).scalar()
profiles = db.execute(text("SELECT COUNT(*) FROM user_profiles")).scalar()
personas = db.execute(text("SELECT COUNT(*) FROM user_persona_assignments")).scalar()
accounts = db.execute(text("SELECT COUNT(*) FROM accounts")).scalar()
transactions = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
recommendations = db.execute(text("SELECT COUNT(*) FROM recommendations")).scalar()
edu_recs = db.execute(text("SELECT COUNT(*) FROM recommendations WHERE type = 'education'")).scalar()
partner_recs = db.execute(text("SELECT COUNT(*) FROM recommendations WHERE type = 'partner_offer'")).scalar()

print(f'  Users: {users}')
print(f'  Profiles: {profiles}')
print(f'  Persona Assignments: {personas}')
print(f'  Accounts: {accounts}')
print(f'  Transactions: {transactions}')
print(f'  Recommendations: {recommendations}')
print(f'    - Education: {edu_recs}')
print(f'    - Partner Offers: {partner_recs}')
db.close()

