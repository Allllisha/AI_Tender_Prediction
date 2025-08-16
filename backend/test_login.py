#!/usr/bin/env python3
"""
ログインAPIをローカルでテストするスクリプト
"""

import requests
import json

# ローカルAPIエンドポイント
url = "http://localhost:8000/auth/login"

# テストデータ
data = {
    "email": "demo@example.com",
    "password": "demo123"
}

# POSTリクエストを送信
response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {response.headers}")
print(f"Response Body: {response.text}")

if response.status_code == 200:
    result = response.json()
    print(f"\nLogin successful!")
    print(f"Token: {result.get('token')[:50]}...")
    print(f"Company ID: {result.get('company_id')}")
    print(f"Company Name: {result.get('company_name')}")
else:
    print(f"\nLogin failed!")