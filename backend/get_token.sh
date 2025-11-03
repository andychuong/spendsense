#!/bin/bash
# Quick script to register a user and get an access token

echo "Registering user..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "Access Token:"
echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
