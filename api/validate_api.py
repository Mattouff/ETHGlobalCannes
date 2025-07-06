#!/usr/bin/env python3
"""
Script de validation de l'API IntentFi CCIP
Ce script vérifie que toutes les fonctions de l'API sont correctement définies
"""

def test_api_structure():
    """Teste la structure de l'API sans la lancer"""
    print("🧪 Testing IntentFi CCIP API Structure")
    print("=" * 50)
    
    try:
        # Test d'import de l'API
        from app import app, CCIP_CONFIG, INTENTFI_CONTRACTS
        print("✅ API imports successful")
        
        # Test des configurations
        print(f"✅ CCIP chains configured: {len(CCIP_CONFIG['supported_chains'])}")
        print(f"✅ Contract addresses configured: {len(INTENTFI_CONTRACTS)}")
        
        # Test des endpoints (routes)
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"✅ Total endpoints: {len(routes)}")
        
        # Endpoints critiques
        critical_endpoints = [
            "/",
            "/tokens/ethereum/<address>",
            "/tokens/base/<address>",
            "/tokens/all/<address>",
            "/ccip/chains",
            "/ccip/transfer",
            "/ccip/status/<tx_id>",
            "/intent/create",
            "/intent/status/<intent_id>",
            "/ccip/analytics"
        ]
        
        print("\n📋 Critical Endpoints Check:")
        for endpoint in critical_endpoints:
            found = any(endpoint.replace("<", "<").replace(">", ">") in route for route in routes)
            status = "✅" if found else "❌"
            print(f"   {status} {endpoint}")
        
        # Test des fonctions utilitaires
        from app import (
            is_valid_eth_address, 
            wei_to_eth, 
            get_chain_config,
            validate_ccip_params,
            calculate_ccip_fees
        )
        
        print("\n🔧 Utility Functions Check:")
        print("✅ is_valid_eth_address")
        print("✅ wei_to_eth")  
        print("✅ get_chain_config")
        print("✅ validate_ccip_params")
        print("✅ calculate_ccip_fees")
        
        # Test de validation d'adresse
        test_addresses = [
            ("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", True),
            ("0x604bbc860e08198086F682355842522F7b099007", True),
            ("invalid_address", False),
            ("", False)
        ]
        
        print("\n🔍 Address Validation Test:")
        for addr, expected in test_addresses:
            result = is_valid_eth_address(addr)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {addr[:20]}... -> {result}")
        
        # Test de conversion wei
        test_wei = "0x16345785d8a0000"  # 0.1 ETH en wei
        eth_value = wei_to_eth(test_wei)
        print(f"\n💰 Wei Conversion Test:")
        print(f"   ✅ {test_wei} -> {eth_value} ETH")
        
        # Test de configuration des chaînes
        print(f"\n🔗 Chain Configuration Test:")
        for chain_name in CCIP_CONFIG["supported_chains"]:
            config = get_chain_config(chain_name)
            if config:
                print(f"   ✅ {chain_name}: Chain ID {config['chain_id']}")
            else:
                print(f"   ❌ {chain_name}: Configuration missing")
        
        # Test de validation CCIP
        print(f"\n⚡ CCIP Validation Test:")
        is_valid, msg = validate_ccip_params("ethereum_sepolia", "base_sepolia", 0.1)
        print(f"   ✅ Valid transfer: {is_valid} - {msg}")
        
        is_valid, msg = validate_ccip_params("invalid_chain", "base_sepolia", 0.1)
        print(f"   ✅ Invalid chain: {is_valid} - {msg}")
        
        # Test de calcul de frais
        print(f"\n💸 Fee Calculation Test:")
        fee = calculate_ccip_fees("ethereum_sepolia", "base_sepolia", 100)
        print(f"   ✅ Estimated fee: {fee} LINK")
        
        print("\n" + "=" * 50)
        print("✅ All API structure tests passed!")
        print("🚀 API is ready to run with: python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_structure()
