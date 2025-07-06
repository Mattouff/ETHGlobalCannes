#!/usr/bin/env python3
"""
Script de test pour l'API IntentFi CCIP
Teste tous les endpoints principaux
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5001"
TEST_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Teste un endpoint et affiche le résultat"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n🧪 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Success")
            result = response.json()
            if "success" in result:
                print(f"API Success: {result['success']}")
            return result
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def run_tests():
    """Exécute tous les tests"""
    print("🚀 IntentFi CCIP API Tests")
    print("=" * 50)
    
    # 1. Test de base - Home
    print("\n📍 1. Testing basic endpoints")
    test_endpoint("GET", "/")
    
    # 2. Test CCIP chains
    print("\n📍 2. Testing CCIP endpoints")
    test_endpoint("GET", "/ccip/chains")
    test_endpoint("GET", "/ccip/health")
    test_endpoint("GET", "/ccip/analytics")
    
    # 3. Test fees calculation
    fee_data = {
        "amount": 0.1,
        "token_address": None,
        "receiver": TEST_ADDRESS
    }
    test_endpoint("POST", "/ccip/fees/ethereum_sepolia/base_sepolia", fee_data)
    
    # 4. Test CCIP transfer (simulation)
    transfer_data = {
        "source_chain": "ethereum_sepolia",
        "destination_chain": "base_sepolia",
        "amount": 0.1,
        "token_address": None,
        "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630",
        "sender": TEST_ADDRESS
    }
    transfer_result = test_endpoint("POST", "/ccip/transfer", transfer_data)
    
    # 5. Test transfer status (si le transfert a été créé)
    if transfer_result and "transaction_id" in transfer_result:
        tx_id = transfer_result["transaction_id"]
        time.sleep(1)  # Attendre un peu
        test_endpoint("GET", f"/ccip/status/{tx_id}")
    
    # 6. Test CCIP history
    test_endpoint("GET", f"/ccip/history/{TEST_ADDRESS}")
    
    # 7. Test Intent creation
    print("\n📍 3. Testing Intent endpoints")
    intent_data = {
        "owner": TEST_ADDRESS,
        "intent_type": "SEND_IF_PRICE_ABOVE",
        "trigger_price": 3500,
        "amount": 0.1,
        "token_address": None,
        "source_chain": "ethereum_sepolia",
        "destination_chain": "base_sepolia",
        "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630"
    }
    intent_result = test_endpoint("POST", "/intent/create", intent_data)
    
    # 8. Test Intent status
    if intent_result and "intent_id" in intent_result:
        intent_id = intent_result["intent_id"]
        test_endpoint("GET", f"/intent/status/{intent_id}")
        
        # 9. Test Intent execution
        test_endpoint("POST", f"/intent/execute/{intent_id}")
        
        # 10. Test Intent cancellation (sur un autre intent)
        intent_data2 = intent_data.copy()
        intent_data2["trigger_price"] = 4000
        intent_result2 = test_endpoint("POST", "/intent/create", intent_data2)
        
        if intent_result2 and "intent_id" in intent_result2:
            intent_id2 = intent_result2["intent_id"]
            test_endpoint("POST", f"/intent/cancel/{intent_id2}")
    
    # 11. Test Intent list
    test_endpoint("GET", f"/intent/list/{TEST_ADDRESS}")
    
    # 12. Test Intent analytics
    test_endpoint("GET", "/intent/analytics")
    
    # 13. Test monitoring endpoints
    print("\n📍 4. Testing monitoring endpoints")
    test_endpoint("GET", "/ccip/supported-tokens/ethereum_sepolia")
    test_endpoint("GET", "/ccip/estimate-time/ethereum_sepolia/base_sepolia")
    
    # 14. Test token endpoints (existing)
    print("\n📍 5. Testing token endpoints")
    test_endpoint("GET", f"/tokens/ethereum/{TEST_ADDRESS}")
    test_endpoint("GET", f"/check-balance/{TEST_ADDRESS}")
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
    print("\n📊 Pour voir les données créées:")
    print(f"   - Transactions CCIP: GET {API_BASE_URL}/ccip/analytics")
    print(f"   - Intents créés: GET {API_BASE_URL}/intent/list/{TEST_ADDRESS}")
    print(f"   - Santé du système: GET {API_BASE_URL}/ccip/health")

if __name__ == "__main__":
    run_tests()
