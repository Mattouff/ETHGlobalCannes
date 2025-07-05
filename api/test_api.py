#!/usr/bin/env python3
"""
Script de test pour l'API IntentFi CCIP
Ce script teste tous les endpoints principaux de l'API
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"
TEST_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Teste un endpoint de l'API"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n🧪 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'OK')}")
            return result
        else:
            print(f"   ❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def main():
    """Lance tous les tests"""
    print("🚀 IntentFi CCIP API Test Suite")
    print("=" * 50)
    
    # Test 1: Homepage
    print("\n📋 BASIC ENDPOINTS")
    test_endpoint("GET", "/")
    
    # Test 2: Token balances
    print("\n💰 TOKEN BALANCE ENDPOINTS")
    test_endpoint("GET", f"/tokens/ethereum/{TEST_ADDRESS}")
    test_endpoint("GET", f"/tokens/base/{TEST_ADDRESS}")
    test_endpoint("GET", f"/tokens/all/{TEST_ADDRESS}")
    test_endpoint("GET", f"/check-balance/{TEST_ADDRESS}")
    
    # Test 3: CCIP endpoints
    print("\n🔗 CCIP ENDPOINTS")
    test_endpoint("GET", "/ccip/chains")
    test_endpoint("GET", "/ccip/health")
    test_endpoint("GET", "/ccip/supported-tokens/ethereum_sepolia")
    test_endpoint("GET", "/ccip/estimate-time/ethereum_sepolia/base_sepolia")
    
    # Test 4: CCIP fee calculation
    fee_data = {
        "amount": 0.1,
        "token_address": None,
        "receiver": "0x604bbc860e08198086F682355842522F7b099007"
    }
    test_endpoint("POST", "/ccip/fees/ethereum_sepolia/base_sepolia", fee_data)
    
    # Test 5: Create mock data
    print("\n📊 MOCK DATA CREATION")
    test_endpoint("POST", "/admin/mock-data")
    
    # Test 6: CCIP transfer
    print("\n💸 CCIP TRANSFER")
    transfer_data = {
        "source_chain": "ethereum_sepolia",
        "destination_chain": "base_sepolia",
        "amount": 0.05,
        "token_address": None,
        "receiver": "0x604bbc860e08198086F682355842522F7b099007",
        "sender": TEST_ADDRESS
    }
    transfer_result = test_endpoint("POST", "/ccip/transfer", transfer_data)
    
    # Test 7: Check transfer status
    if transfer_result and "transaction_id" in transfer_result:
        tx_id = transfer_result["transaction_id"]
        test_endpoint("GET", f"/ccip/status/{tx_id}")
    
    # Test 8: Create intent
    print("\n🎯 INTENT CREATION")
    intent_data = {
        "owner": TEST_ADDRESS,
        "intent_type": "SEND_IF_PRICE_ABOVE",
        "trigger_price": 3500,
        "amount": 0.1,
        "source_chain": "ethereum_sepolia",
        "destination_chain": "base_sepolia",
        "receiver": "0x604bbc860e08198086F682355842522F7b099007"
    }
    intent_result = test_endpoint("POST", "/intent/create", intent_data)
    
    # Test 9: Check intent status and execute
    if intent_result and "intent_id" in intent_result:
        intent_id = intent_result["intent_id"]
        test_endpoint("GET", f"/intent/status/{intent_id}")
        test_endpoint("POST", f"/intent/execute/{intent_id}")
    
    # Test 10: List user intents
    test_endpoint("GET", f"/intent/list/{TEST_ADDRESS}")
    
    # Test 11: Analytics
    print("\n📈 ANALYTICS")
    test_endpoint("GET", "/ccip/analytics")
    test_endpoint("GET", "/intent/analytics")
    test_endpoint("GET", f"/ccip/history/{TEST_ADDRESS}")
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("🌐 API is running at:", API_BASE_URL)

if __name__ == "__main__":
    main()
