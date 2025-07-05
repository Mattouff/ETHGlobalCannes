import os
import re
from decimal import Decimal

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

ALCHEMY_API_KEY = "dDOVAvCmh3rX60qNaCjbs"
ALCHEMY_ETH_URL = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_BASE_URL = f"https://base-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_FLOW_URL = f"https://flow-testnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# CoinGecko API configuration
COINGECKO_API_KEY = "CG-mr7yWjrfkrQADpfyEaRDUDMM"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


# Fonctions utilitaires
def is_valid_eth_address(address):
    """Valide si une adresse Ethereum est correcte"""
    if not address:
        return False
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))


def wei_to_eth(wei_hex):
    """Convertit wei (hex) en ETH"""
    try:
        wei = int(wei_hex, 16)
        return wei / 10**18
    except:
        return 0


def get_token_metadata(contract_address, rpc_url):
    """Récupère les métadonnées d'un token ERC-20"""
    default_metadata = {
        "name": "Unknown Token",
        "symbol": "???",
        "decimals": 18
    }
    
    try:
        # Payload pour récupérer les métadonnées
        metadata_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getTokenMetadata",
            "params": [contract_address]
        }
        
        res = requests.post(rpc_url, json=metadata_payload, timeout=5)
        data = res.json()
        
        if "result" in data and data["result"]:
            result = data["result"]
            return {
                "name": result.get("name", "Unknown Token"),
                "symbol": result.get("symbol", "???"),
                "decimals": result.get("decimals", 18)
            }
        else:
            return default_metadata
            
    except Exception as e:
        print(f"Error getting token metadata for {contract_address}: {str(e)}")
        return default_metadata

def get_token_price_simple(token_symbol, contract_address=None, platform="ethereum"):
    """Simplified token price fetching - contract address first, then symbol for native tokens"""
    try:
        # For native tokens (no contract address), use symbol
        if not contract_address or contract_address == "native":
            # Map symbols to CoinGecko IDs for native tokens
            native_coin_ids = {
                "ETH": "ethereum",
                "FLOW": "flow",
                "BTC": "bitcoin"
            }
            
            coin_id = native_coin_ids.get(token_symbol.upper())
            if not coin_id:
                return 0
                
            url = f"{COINGECKO_BASE_URL}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "x_cg_demo_api_key": COINGECKO_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get(coin_id, {}).get("usd", 0)
        
        else:
            # For ERC-20 tokens, use contract address
            platform_mapping = {
                "ethereum": "ethereum",
                "base": "base", 
                "flow": "flow"
            }
            
            coingecko_platform = platform_mapping.get(platform, "ethereum")
            
            url = f"{COINGECKO_BASE_URL}/simple/token_price/{coingecko_platform}"
            params = {
                "contract_addresses": contract_address,
                "vs_currencies": "usd",
                "x_cg_demo_api_key": COINGECKO_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get(contract_address.lower(), {}).get("usd", 0)
            
    except Exception as e:
        print(f"Error getting price for {token_symbol}/{contract_address}: {str(e)}")
        return 0

def calculate_token_usd_value(token, platform="ethereum"):
    """Calculate USD value for a single token - simplified"""
    try:
        balance = float(token.get("readableBalance", 0))
        if balance <= 0:
            token["price_usd"] = 0
            token["value_usd"] = 0
            return 0
        
        symbol = token.get("symbol", "")
        contract_address = token.get("contractAddress", "")
        
        # Single price lookup function
        price = get_token_price_simple(symbol, contract_address, platform)
        
        usd_value = balance * price
        
        token["price_usd"] = price
        token["value_usd"] = usd_value
        
        return usd_value
        
    except Exception as e:
        print(f"Error calculating USD value for token: {str(e)}")
        token["price_usd"] = 0
        token["value_usd"] = 0
        return 0

def calculate_total_wallet_value(tokens, platform="ethereum"):
    """Calculate total USD value of all tokens in wallet"""
    total_value = 0
    
    for token in tokens:
        token_value = calculate_token_usd_value(token, platform)
        total_value += token_value
    
    return round(total_value, 2)

def create_standard_response(chain, address, tokens, native_balance=0, debug_info=None, error=None, platform="ethereum"):
    """Crée une réponse standardisée pour toutes les routes"""
    base_response = {
        "success": error is None,
        "chain": chain,
        "address": address,
        "timestamp": "2024-12-15T14:30:00Z",
        "api_version": "1.0"
    }
    
    if error:
        base_response.update({
            "error": error,
            "tokens": [],
            "token_count": 0,
            "native_balance": 0,
            "total_value_usd": 0
        })
    else:
        # Calculate actual USD value of all tokens
        total_value_usd = calculate_total_wallet_value(tokens, platform)
        
        base_response.update({
            "tokens": tokens,
            "token_count": len(tokens),
            "native_balance": native_balance,
            "total_value_usd": total_value_usd
        })
    
    if debug_info:
        base_response["debug"] = debug_info
        
    return base_response


@app.route("/tokens/ethereum/<address>")
def get_eth_tokens_balances(address):
    """Récupère les tokens ETH Sepolia testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify(create_standard_response(
            chain="ethereum_sepolia",
            address=address,
            tokens=[],
            platform="ethereum",
            error="Invalid Ethereum address"
        )), 400
        
    # D'abord récupérer le balance ETH natif
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    eth_balance = 0
    try:
        res = requests.post(ALCHEMY_ETH_URL, json=eth_payload)
        data = res.json()
        if "result" in data:
            eth_balance = wei_to_eth(data["result"])
    except:
        pass

    # Maintenant récupérer les tokens ERC-20
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [address]
    }

    try:
        res = requests.post(ALCHEMY_ETH_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        
        # Debug: Log de la réponse complète
        print(f"🔍 DEBUG Sepolia - URL: {ALCHEMY_ETH_URL}")
        print(f"🔍 DEBUG Sepolia - Response status: {res.status_code}")
        print(f"🔍 DEBUG Sepolia - Response data: {data}")

        if "error" in data:
            return jsonify({
                "error": data["error"]["message"],
                "chain": "ethereum_sepolia",
                "address": address,
                "debug": {
                    "api_url": ALCHEMY_ETH_URL,
                    "api_key_preview": f"{ALCHEMY_API_KEY[:8]}...",
                    "full_response": data
                }
            }), 400

        balances = data.get("result", {}).get("tokenBalances", [])
        print(f"🔍 DEBUG Sepolia - Total tokens found: {len(balances)}")
        
        non_zero_balances = []
        
        for i, balance in enumerate(balances):
            token_balance_int = int(balance["tokenBalance"], 16)
            print(f"🔍 DEBUG Sepolia - Token {i}: {balance['contractAddress']} = {token_balance_int} ({balance['tokenBalance']})")
            
            if token_balance_int > 0:
                # Récupérer les métadonnées du token
                metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_ETH_URL)
                
                # Calculer le montant lisible
                readable_balance = token_balance_int / (10 ** metadata["decimals"])
                
                token_info = {
                    "contractAddress": balance["contractAddress"],
                    "tokenBalance": balance["tokenBalance"],
                    "readableBalance": readable_balance,
                    "name": metadata["name"],
                    "symbol": metadata["symbol"],
                    "decimals": metadata["decimals"]
                }
                non_zero_balances.append(token_info)
                print(f"✅ Added token: {metadata['symbol']} = {readable_balance}")

        # Ajouter ETH natif s'il y en a
        result_tokens = []
        if eth_balance > 0:
            result_tokens.append({
                "contractAddress": "native",
                "tokenBalance": hex(int(eth_balance * 10**18)),
                "readableBalance": eth_balance,
                "name": "Ethereum",
                "symbol": "ETH",
                "decimals": 18
            })
        
        result_tokens.extend(non_zero_balances)

        return jsonify(create_standard_response(
            chain="ethereum_sepolia",
            address=address,
            tokens=result_tokens,
            native_balance=eth_balance,
            platform="ethereum",
            debug_info={
                "total_tokens_checked": len(balances),
                "non_zero_tokens": len(non_zero_balances),
                "api_url": ALCHEMY_ETH_URL,
                "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
            }
        ))

    except Exception as e:
        return jsonify(create_standard_response(
            chain="ethereum_sepolia",
            address=address,
            tokens=[],
            platform="ethereum",
            error=str(e)
        )), 500

@app.route("/tokens/base/<address>")
def get_base_token_balances(address):
    """Récupère les tokens Base Sepolia testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify(create_standard_response(
            chain="base_sepolia",
            address=address,
            tokens=[],
            platform="base",
            error="Invalid Ethereum address"
        )), 400
        
    # D'abord récupérer le balance ETH natif sur Base
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    eth_balance = 0
    try:
        res = requests.post(ALCHEMY_BASE_URL, json=eth_payload)
        data = res.json()
        if "result" in data:
            eth_balance = wei_to_eth(data["result"])
    except:
        pass

    # Maintenant récupérer les tokens ERC-20
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [address]
    }

    try:
        res = requests.post(ALCHEMY_BASE_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        
        # Debug: Log de la réponse complète
        print(f"🔍 DEBUG Base - URL: {ALCHEMY_BASE_URL}")
        print(f"🔍 DEBUG Base - Response status: {res.status_code}")
        print(f"🔍 DEBUG Base - Response data: {data}")

        if "error" in data:
            return jsonify(create_standard_response(
                chain="base_sepolia",
                address=address,
                tokens=[],
                platform="base",
                error=data["error"]["message"]
            )), 400

        balances = data.get("result", {}).get("tokenBalances", [])
        print(f"🔍 DEBUG Base - Total tokens found: {len(balances)}")
        
        non_zero_balances = []
        
        for i, balance in enumerate(balances):
            token_balance_int = int(balance["tokenBalance"], 16)
            print(f"🔍 DEBUG Base - Token {i}: {balance['contractAddress']} = {token_balance_int} ({balance['tokenBalance']})")
            
            if token_balance_int > 0:
                # Récupérer les métadonnées du token
                metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_BASE_URL)
                
                # Calculer le montant lisible
                readable_balance = token_balance_int / (10 ** metadata["decimals"])
                
                token_info = {
                    "contractAddress": balance["contractAddress"],
                    "tokenBalance": balance["tokenBalance"],
                    "readableBalance": readable_balance,
                    "name": metadata["name"],
                    "symbol": metadata["symbol"],
                    "decimals": metadata["decimals"]
                }
                non_zero_balances.append(token_info)
                print(f"✅ Added token: {metadata['symbol']} = {readable_balance}")

        # Ajouter ETH natif s'il y en a
        result_tokens = []
        if eth_balance > 0:
            result_tokens.append({
                "contractAddress": "native",
                "tokenBalance": hex(int(eth_balance * 10**18)),
                "readableBalance": eth_balance,
                "name": "Ethereum",
                "symbol": "ETH",
                "decimals": 18
            })
        
        result_tokens.extend(non_zero_balances)
        
        # Si aucun token ERC-20 trouvé avec alchemy_getTokenBalances, essayer avec des tokens spécifiques
        if len(non_zero_balances) == 0:
            print("🔍 DEBUG Base - No tokens found with alchemy_getTokenBalances, trying specific tokens...")
            specific_tokens = check_specific_token_balances(address, ALCHEMY_BASE_URL, BASE_SEPOLIA_POPULAR_TOKENS)
            result_tokens.extend(specific_tokens)
            print(f"🔍 DEBUG Base - Found {len(specific_tokens)} specific tokens")

        return jsonify(create_standard_response(
            chain="base_sepolia",
            address=address,
            tokens=result_tokens,
            native_balance=eth_balance,
            platform="base",
            debug_info={
                "total_tokens_checked": len(balances),
                "non_zero_tokens": len(non_zero_balances),
                "specific_tokens_checked": len(BASE_SEPOLIA_POPULAR_TOKENS) if len(non_zero_balances) == 0 else 0,
                "api_url": ALCHEMY_BASE_URL,
                "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
            }
        ))

    except Exception as e:
        return jsonify(create_standard_response(
            chain="base_sepolia", 
            address=address,
            tokens=[],
            platform="base",
            error=str(e)
        )), 500

@app.route("/tokens/flow/<address>")
def get_flow_token_balances(address):
    """Récupère les tokens Flow testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify(create_standard_response(
            chain="flow_testnet",
            address=address,
            tokens=[],
            platform="flow",
            error="Invalid Flow address format"
        )), 400
        
    # D'abord récupérer le balance FLOW natif
    flow_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    flow_balance = 0
    try:
        res = requests.post(ALCHEMY_FLOW_URL, json=flow_payload, timeout=10)
        data = res.json()
        if "result" in data:
            flow_balance = wei_to_eth(data["result"])
    except Exception as e:
        print(f"Erreur récupération balance FLOW: {e}")

    # Pour Flow, on va essayer différentes méthodes pour récupérer les tokens
    result_tokens = []
    
    # Ajouter FLOW natif s'il y en a
    if flow_balance > 0:
        result_tokens.append({
            "contractAddress": "native",
            "tokenBalance": hex(int(flow_balance * 10**18)),
            "readableBalance": flow_balance,
            "name": "Flow",
            "symbol": "FLOW",
            "decimals": 8,  # Flow utilise 8 décimales
            "type": "native"
        })

    # Essayer de récupérer les tokens ERC-20 style
    erc20_tokens = []
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getTokenBalances",
            "params": [address]
        }
        
        res = requests.post(ALCHEMY_FLOW_URL, json=payload, timeout=15)
        data = res.json()
        
        if "result" in data and "tokenBalances" in data["result"]:
            balances = data["result"]["tokenBalances"]
            for balance in balances:
                if int(balance["tokenBalance"], 16) > 0:
                    # Récupérer les métadonnées du token
                    metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_FLOW_URL)
                    
                    # Calculer le montant lisible
                    raw_balance = int(balance["tokenBalance"], 16)
                    readable_balance = raw_balance / (10 ** metadata["decimals"])
                    
                    token_info = {
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": metadata["decimals"],
                        "type": "erc20"
                    }
                    erc20_tokens.append(token_info)
                    
    except Exception as e:
        print(f"Erreur récupération tokens ERC-20 Flow: {e}")

    # Ajouter des tokens Flow testnet courants (mock data si les APIs ne marchent pas)
    flow_testnet_tokens = [
        {
            "contractAddress": "0x7e60df042a9c0868",
            "tokenBalance": "0x0",
            "readableBalance": 0,
            "name": "Flow Token",
            "symbol": "FLOW",
            "decimals": 8,
            "type": "flow_native",
            "note": "Token natif Flow"
        },
        {
            "contractAddress": "0x0b2a3299cc857e29",
            "tokenBalance": "0x0", 
            "readableBalance": 0,
            "name": "USD Coin",
            "symbol": "USDC",
            "decimals": 8,
            "type": "flow_ft",
            "note": "USDC sur Flow testnet"
        },
        {
            "contractAddress": "0xe467b9dd11fa00df",
            "tokenBalance": "0x0",
            "readableBalance": 0, 
            "name": "Tether USD",
            "symbol": "USDT",
            "decimals": 8,
            "type": "flow_ft",
            "note": "USDT sur Flow testnet"
        }
    ]

    # Si on n'a pas trouvé de tokens ERC-20, utiliser les tokens Flow par défaut
    if not erc20_tokens:
        result_tokens.extend(flow_testnet_tokens)
        note = "Tokens Flow testnet par défaut - utilisez une adresse avec des tokens pour voir les vraies balances"
    else:
        result_tokens.extend(erc20_tokens)
        note = "Tokens récupérés via l'API"

    return jsonify(create_standard_response(
        chain="flow_testnet",
        address=address,
        tokens=result_tokens,
        native_balance=flow_balance,
        platform="flow",
        debug_info={
            "note": note,
            "flow_info": {
                "network": "Flow Testnet",
                "rpc_url": ALCHEMY_FLOW_URL[:50] + "...",
                "native_decimals": 8,
                "supports": ["Flow Fungible Tokens", "Limited ERC-20"]
            },
            "api_url": ALCHEMY_FLOW_URL,
            "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
        }
    ))

@app.route("/test-api")
def test_api():
    """Endpoint de test pour vérifier que l'API Alchemy fonctionne"""
    test_results = {}
    
    # Test avec une adresse Ethereum connue (Vitalik)
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    for chain, url in [
        ("ethereum", ALCHEMY_ETH_URL),
        ("base", ALCHEMY_BASE_URL), 
        ("flow", ALCHEMY_FLOW_URL)
    ]:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getBalance",
            "params": [test_address, "latest"]
        }
        
        try:
            res = requests.post(url, json=payload, timeout=5)
            data = res.json()
            
            test_results[chain] = {
                "status": "success" if "result" in data else "error",
                "response": data,
                "url": url[:50] + "..." if len(url) > 50 else url
            }
        except Exception as e:
            test_results[chain] = {
                "status": "error",
                "error": str(e),
                "url": url[:50] + "..." if len(url) > 50 else url
            }
    
    return jsonify({
        "message": "Alchemy API Test Results",
        "test_address": test_address,
        "results": test_results,
        "note": "If you see errors, check your ALCHEMY_API_KEY"
    })

@app.route("/")
def home():
    return jsonify({
        "message": "🚀 IntentFi Multi-Chain Token API (TESTNET)",
        "description": "API pour récupérer les balances de tokens sur Ethereum Sepolia, Base Sepolia et Flow Testnet",
        "endpoints": {
            "quick_check": {
                "url": "/check-balance/<address>",
                "description": "Vérification rapide du balance",
                "example": "/check-balance/0x604bbc860e08198086F682355842522F7b099007"
            },
            "faucet_info": {
                "url": "/faucet-sepolia",
                "description": "Guide pour obtenir des tokens Sepolia testnet"
            },
            "test_api": {
                "url": "/test-api",
                "description": "Test de connectivité Alchemy API"
            },
            "debug_sepolia": {
                "url": "/debug-sepolia/<address>",
                "description": "Debug détaillé pour Sepolia testnet",
                "example": "/debug-sepolia/0xYourAddress"
            },
            "test_flow": {
                "url": "/test-flow/<address>",
                "description": "Test spécifique des méthodes Flow",
                "example": "/test-flow/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            },
            "all_tokens": {
                "url": "/tokens/all/<address>",
                "description": "Tous les tokens sur toutes les chaînes testnet",
                "example": "/tokens/all/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            },
            "ethereum_tokens": {
                "url": "/tokens/ethereum/<address>",
                "description": "Tokens sur Ethereum Sepolia testnet",
                "example": "/tokens/ethereum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            },
            "base_tokens": {
                "url": "/tokens/base/<address>",
                "description": "Tokens sur Base Sepolia testnet",
                "example": "/tokens/base/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            },
            "flow_tokens": {
                "url": "/tokens/flow/<address>",
                "description": "Tokens sur Flow testnet (avec fallback)",
                "example": "/tokens/flow/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            }
        },
        "ai_agent": {
            "recommend": "http://localhost:8001/recommend",
            "health": "http://localhost:8001/health"
        },
        "networks": {
            "ethereum": "Sepolia Testnet",
            "base": "Base Sepolia Testnet", 
            "flow": "Flow Testnet"
        },
        "usage": "Remplacez <address> par une adresse Ethereum valide (0x...)"
    })

@app.route("/debug-sepolia/<address>")
def debug_sepolia_tokens(address):
    """Debug détaillé pour Sepolia - voir exactement ce qui se passe"""
    if not is_valid_eth_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
    
    debug_info = {
        "address": address,
        "network": "Sepolia Testnet",
        "api_url": ALCHEMY_ETH_URL,
        "api_key_preview": f"{ALCHEMY_API_KEY[:8]}...",
        "tests": {}
    }
    
    # Test 1: Balance ETH natif
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance", 
        "params": [address, "latest"]
    }
    
    try:
        print(f"🔍 DEBUG: Testing ETH balance for {address}")
        res = requests.post(ALCHEMY_ETH_URL, json=eth_payload, timeout=10)
        eth_data = res.json()
        
        debug_info["tests"]["eth_balance"] = {
            "request": eth_payload,
            "response": eth_data,
            "status_code": res.status_code,
            "success": "result" in eth_data
        }
        
        if "result" in eth_data:
            eth_balance = wei_to_eth(eth_data["result"])
            debug_info["tests"]["eth_balance"]["readable_balance"] = eth_balance
            print(f"✅ ETH Balance: {eth_balance} ETH")
        else:
            print(f"❌ ETH Balance failed: {eth_data}")
            
    except Exception as e:
        debug_info["tests"]["eth_balance"] = {
            "error": str(e),
            "success": False
        }
        print(f"❌ ETH Balance exception: {e}")
    
    # Test 2: alchemy_getTokenBalances
    token_payload = {
        "jsonrpc": "2.0", 
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [address]
    }
    
    try:
        print(f"🔍 DEBUG: Testing token balances for {address}")
        res = requests.post(ALCHEMY_ETH_URL, json=token_payload, timeout=15)
        token_data = res.json()
        
        debug_info["tests"]["token_balances"] = {
            "request": token_payload,
            "response": token_data,
            "status_code": res.status_code,
            "success": "result" in token_data
        }
        
        if "result" in token_data:
            balances = token_data.get("result", {}).get("tokenBalances", [])
            debug_info["tests"]["token_balances"]["total_tokens"] = len(balances)
            debug_info["tests"]["token_balances"]["non_zero_count"] = len([b for b in balances if int(b["tokenBalance"], 16) > 0])
            print(f"✅ Found {len(balances)} total tokens, {len([b for b in balances if int(b['tokenBalance'], 16) > 0])} with balance > 0")
        else:
            print(f"❌ Token balances failed: {token_data}")
            
    except Exception as e:
        debug_info["tests"]["token_balances"] = {
            "error": str(e),
            "success": False
        }
        print(f"❌ Token balances exception: {e}")
    
    # Test 3: Quelques tokens Sepolia courants (USDC, LINK, etc.)
    common_sepolia_tokens = [
        "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238", # USDC Sepolia
        "0x779877A7B0D9E8603169DdbD7836e478b4624789", # LINK Sepolia  
        "0x2d13826359803522c6DcA7a8EA734Ee8F0ee2B1d"  # Autre token Sepolia courant
    ]
    
    debug_info["tests"]["specific_tokens"] = {}
    
    for token_address in common_sepolia_tokens:
        try:
            # Test balance pour ce token spécifique
            specific_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "alchemy_getTokenBalances",
                "params": [address, [token_address]]
            }
            
            res = requests.post(ALCHEMY_ETH_URL, json=specific_payload, timeout=10)
            data = res.json()
            
            debug_info["tests"]["specific_tokens"][token_address] = {
                "response": data,
                "success": "result" in data
            }
            
        except Exception as e:
            debug_info["tests"]["specific_tokens"][token_address] = {
                "error": str(e),
                "success": False
            }
    
    return jsonify(debug_info)

@app.route("/faucet-sepolia")
def sepolia_faucet_info():
    """Informations sur les faucets Sepolia et comment obtenir des tokens testnet"""
    return jsonify({
        "message": "🚰 Guide pour obtenir des tokens Sepolia testnet",
        "your_address": "0x604bbc860e08198086F682355842522F7b099007",
        "current_status": {
            "eth_balance": 0,
            "token_count": 0,
            "note": "Votre adresse n'a actuellement aucun token"
        },
        "faucets": {
            "eth_sepolia": [
                {
                    "name": "Alchemy Sepolia Faucet",
                    "url": "https://sepoliafaucet.com/",
                    "description": "Faucet officiel Alchemy - 0.5 ETH/jour",
                    "requires": "Compte Alchemy"
                },
                {
                    "name": "Chainlink Sepolia Faucet", 
                    "url": "https://faucets.chain.link/sepolia",
                    "description": "0.1 ETH + tokens LINK",
                    "requires": "Connexion wallet"
                },
                {
                    "name": "QuickNode Faucet",
                    "url": "https://faucet.quicknode.com/ethereum/sepolia",
                    "description": "0.05 ETH toutes les 24h",
                    "requires": "Adresse email"
                }
            ],
            "tokens_sepolia": [
                {
                    "name": "USDC Sepolia",
                    "contract": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                    "faucet": "https://faucet.circle.com/",
                    "description": "USDC testnet de Circle"
                },
                {
                    "name": "LINK Sepolia", 
                    "contract": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
                    "faucet": "https://faucets.chain.link/sepolia",
                    "description": "LINK testnet de Chainlink"
                }
            ]
        },
        "steps": [
            "1. Allez sur https://sepoliafaucet.com/",
            "2. Connectez votre wallet ou entrez votre adresse: 0x604bbc860e08198086F682355842522F7b099007",
            "3. Réclamez 0.5 ETH Sepolia",
            "4. Attendez 1-2 minutes pour la confirmation",
            "5. Testez avec /debug-sepolia/0x604bbc860e08198086F682355842522F7b099007",
            "6. Pour les tokens ERC-20, utilisez les faucets spécifiques listés ci-dessus"
        ],
        "test_again": "/debug-sepolia/0x604bbc860e08198086F682355842522F7b099007"
    })

@app.route("/check-balance/<address>")
def quick_balance_check(address):
    """Vérification rapide du balance pour voir si les faucets ont fonctionné"""
    if not is_valid_eth_address(address):
        return jsonify(create_standard_response(
            chain="ethereum_sepolia",
            address=address,
            tokens=[],
            platform="ethereum",
            error="Invalid Ethereum address"
        )), 400
    
    # Vérifier balance ETH
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    eth_balance = 0
    try:
        res = requests.post(ALCHEMY_ETH_URL, json=eth_payload, timeout=10)
        data = res.json()
        if "result" in data:
            eth_balance = wei_to_eth(data["result"])
    except Exception as e:
        return jsonify(create_standard_response(
            chain="ethereum_sepolia",
            address=address,
            tokens=[],
            platform="ethereum",
            error=f"Failed to check balance: {str(e)}"
        )), 500
    
    # Vérifier quelques tokens courants
    token_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [address]
    }
    
    tokens_with_balance = []
    
    try:
        res = requests.post(ALCHEMY_ETH_URL, json=token_payload, timeout=10)
        data = res.json()
        if "result" in data:
            balances = data.get("result", {}).get("tokenBalances", [])
            for balance in balances:
                balance_int = int(balance["tokenBalance"], 16)
                if balance_int > 0:
                    metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_ETH_URL)
                    readable_balance = balance_int / (10 ** metadata["decimals"])
                    
                    tokens_with_balance.append({
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": metadata["decimals"]
                    })
    except:
        pass
    
    # Ajouter ETH natif s'il y en a
    result_tokens = []
    if eth_balance > 0:
        result_tokens.append({
            "contractAddress": "native",
            "tokenBalance": hex(int(eth_balance * 10**18)),
            "readableBalance": eth_balance,
            "name": "Ethereum",
            "symbol": "ETH",
            "decimals": 18
        })
    
    result_tokens.extend(tokens_with_balance)
    
    status = "✅ Ready" if eth_balance > 0 else "⏳ Waiting for faucet"
    
    return jsonify(create_standard_response(
        chain="ethereum_sepolia",
        address=address,
        tokens=result_tokens,
        native_balance=eth_balance,
        platform="ethereum",
        debug_info={
            "eth_status": "✅ Has ETH" if eth_balance > 0 else "❌ No ETH - use faucet",
            "overall_status": status,
            "next_steps": [
                "Use /faucet-sepolia for faucet links" if eth_balance == 0 else "✅ ETH balance detected!",
                f"Visit /tokens/ethereum/{address} to see all tokens" if eth_balance > 0 else "Get ETH first, then check tokens"
            ],
            "refresh_endpoint": f"/check-balance/{address}"
        }
    ))

@app.route("/tokens/all/<address>")
def get_all_tokens(address):
    """Récupère les tokens de toutes les chaînes supportées avec format standardisé"""
    if not is_valid_eth_address(address):
        return jsonify(create_standard_response(
            chain="multi_chain",
            address=address,
            tokens=[],
            platform="ethereum",
            error="Invalid Ethereum address"
        )), 400
    
    all_tokens = []
    total_native_balance = 0
    debug_chains = {}
    
    # Appeler chaque endpoint de chaîne
    chains = [
        ("ethereum_sepolia", ALCHEMY_ETH_URL, "ETH"),
        ("base_sepolia", ALCHEMY_BASE_URL, "ETH"), 
        ("flow_testnet", ALCHEMY_FLOW_URL, "FLOW")
    ]
    
    for chain_name, chain_url, native_symbol in chains:
        try:
            # Récupérer le balance natif
            native_payload = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "eth_getBalance",
                "params": [address, "latest"]
            }
            
            native_balance = 0
            try:
                res = requests.post(chain_url, json=native_payload, timeout=10)
                data = res.json()
                if "result" in data:
                    native_balance = wei_to_eth(data["result"])
                    total_native_balance += native_balance
            except:
                pass

            # Récupérer les tokens ERC-20
            tokens_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getTokenBalances",
                "params": [address]
            }

            res = requests.post(chain_url, json=tokens_payload, timeout=10)
            data = res.json()

            if "error" in data:
                debug_chains[chain_name] = {
                    "error": data["error"]["message"],
                    "native_balance": native_balance,
                    "token_count": 0
                }
                continue

            balances = data.get("result", {}).get("tokenBalances", [])
            chain_tokens = []
            
            # Ajouter le token natif s'il y en a
            if native_balance > 0:
                native_name = "Ethereum" if "ethereum" in chain_name else ("Ethereum" if "base" in chain_name else "Flow")
                chain_tokens.append({
                    "contractAddress": "native",
                    "tokenBalance": hex(int(native_balance * 10**18)),
                    "readableBalance": native_balance,
                    "name": native_name,
                    "symbol": native_symbol,
                    "decimals": 18 if native_symbol != "FLOW" else 8,
                    "chain": chain_name,
                    "type": "native"
                })
            
            # Traiter les tokens ERC-20 (limiter à 5 par chaîne pour la performance)
            processed_count = 0
            for balance in balances:
                if int(balance["tokenBalance"], 16) > 0 and processed_count < 5:
                    # Récupérer les métadonnées du token
                    metadata = get_token_metadata(balance["contractAddress"], chain_url)
                    
                    # Calculer le montant lisible
                    raw_balance = int(balance["tokenBalance"], 16)
                    readable_balance = raw_balance / (10 ** metadata["decimals"])
                    
                    token_info = {
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": metadata["decimals"],
                        "chain": chain_name,
                        "type": "erc20"
                    }
                    chain_tokens.append(token_info)
                    processed_count += 1

            # Ajouter tous les tokens de cette chaîne à la liste globale
            all_tokens.extend(chain_tokens)
            
            debug_chains[chain_name] = {
                "native_balance": native_balance,
                "native_symbol": native_symbol,
                "token_count": len(chain_tokens),
                "success": True
            }

        except Exception as e:
            debug_chains[chain_name] = {
                "error": str(e),
                "native_balance": 0,
                "token_count": 0,
                "success": False
            }

    return jsonify(create_standard_response(
        chain="multi_chain",
        address=address,
        tokens=all_tokens,
        native_balance=total_native_balance,
        platform="ethereum",  # Default to ethereum for multi-chain
        debug_info={
            "chains_tested": list(debug_chains.keys()),
            "chains_detail": debug_chains,
            "performance_limit": "5 ERC-20 tokens per chain",
            "total_chains": len(chains)
        }
    ))

# Tokens populaires sur Base Sepolia pour tests
BASE_SEPOLIA_POPULAR_TOKENS = [
    {
        "address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e", # USDC sur Base Sepolia
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6
    },
    {
        "address": "0x4200000000000000000000000000000000000006", # WETH sur Base
        "name": "Wrapped Ether",
        "symbol": "WETH", 
        "decimals": 18
    }
]

def check_specific_token_balances(address, rpc_url, token_contracts):
    """Vérifie les balances pour des tokens spécifiques"""
    tokens_found = []
    
    for token in token_contracts:
        try:
            # Payload pour vérifier le balance d'un token spécifique
            balance_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_call",
                "params": [
                    {
                        "to": token["address"],
                        "data": f"0x70a08231000000000000000000000000{address[2:]}"  # balanceOf(address)
                    },
                    "latest"
                ]
            }
            
            res = requests.post(rpc_url, json=balance_payload, timeout=5)
            data = res.json()
            
            if "result" in data and data["result"] != "0x":
                balance_hex = data["result"]
                balance_int = int(balance_hex, 16)
                
                if balance_int > 0:
                    readable_balance = balance_int / (10 ** token["decimals"])
                    
                    token_info = {
                        "contractAddress": token["address"],
                        "tokenBalance": balance_hex,
                        "readableBalance": readable_balance,
                        "name": token["name"],
                        "symbol": token["symbol"],
                        "decimals": token["decimals"]
                    }
                    tokens_found.append(token_info)
                    print(f"✅ Found specific token: {token['symbol']} = {readable_balance}")
                    
        except Exception as e:
            print(f"❌ Error checking token {token['symbol']}: {str(e)}")
            continue
            
    return tokens_found

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)