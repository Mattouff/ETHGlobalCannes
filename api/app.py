import os
import re
from decimal import Decimal
import json
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

app = Flask(__name__)

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
ALCHEMY_ETH_URL = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_BASE_URL = f"https://base-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_POLYGON_URL = f"https://polygon-amoy.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_ARBITRUM_URL = f"https://arb-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_OPTIMISM_URL = f"https://opt-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
ALCHEMY_FLOW_URL = f"https://flow-testnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# Configuration CCIP
CCIP_CONFIG = {
    "supported_chains": {
        "ethereum_sepolia": {
            "chain_id": 11155111,
            "selector": "16015286601757825753",
            "rpc_url": ALCHEMY_ETH_URL,
            "router": "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59",
            "link_token": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
            "native_symbol": "ETH"
        },
        "base_sepolia": {
            "chain_id": 84532,
            "selector": "10344971235874465080",
            "rpc_url": ALCHEMY_BASE_URL,
            "router": "0xD3b06cEbF099CE7DA4AcCf578aaebFDBd6e88a93",
            "link_token": "0xE4aB69C077896252FAFBD49EFD26B5D171A32410",
            "native_symbol": "ETH"
        },
        "polygon_amoy": {
            "chain_id": 80002,
            "selector": "16281711391670634445",
            "rpc_url": ALCHEMY_POLYGON_URL,
            "router": "0x9C32fCB86BF0f4a1A8921a9Fe46de3198bb884B2",
            "link_token": "0x0Fd9e8d3aF1aaee056EB9e802c3A762a667b1904",
            "native_symbol": "MATIC"
        },
        "arbitrum_sepolia": {
            "chain_id": 421614,
            "selector": "3478487238524512106",
            "rpc_url": ALCHEMY_ARBITRUM_URL,
            "router": "0x2a9C5afB0d0e4BAb2BCdaE109EC4b0c4Be15a165",
            "link_token": "0xb1D4538B4571d411F07960EF2838Ce337FE1E80E",
            "native_symbol": "ETH"
        },
        "optimism_sepolia": {
            "chain_id": 11155420,
            "selector": "5224473277236331295",
            "rpc_url": ALCHEMY_OPTIMISM_URL,
            "router": "0x114A20A10b43D4115e5aeef7345a1A71d2a60C57",
            "link_token": "0xE4aB69C077896252FAFBD49EFD26B5D171A32410",
            "native_symbol": "ETH"
        },
        "flow_testnet": {
            "chain_id": 747,
            "selector": "FLOW_CCIP_NOT_AVAILABLE",
            "rpc_url": ALCHEMY_FLOW_URL,
            "router": "FLOW_CUSTOM_BRIDGE",
            "link_token": "FLOW_NATIVE_BRIDGE",
            "native_symbol": "FLOW",
            "ccip_enabled": False,
            "note": "Flow uses custom bridging, not standard CCIP"
        }
    },
    "fee_estimates": {
        "base_fee": 0.001,  # LINK
        "per_byte": 0.0001  # LINK per byte
    }
}

# Configuration des contrats IntentFi
INTENTFI_CONTRACTS = {
    "ethereum_sepolia": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée
        "intentfi_ccip": "0x..."  # À remplacer par l'adresse déployée
    },
    "base_sepolia": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée  
        "intentfi_ccip": "0x..."  # À remplacer par l'adresse déployée
    },
    "polygon_amoy": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée
        "intentfi_ccip": "0x..."  # À remplacer par l'adresse déployée
    },
    "arbitrum_sepolia": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée
        "intentfi_ccip": "0x..."  # À remplacer par l'adresse déployée
    },
    "optimism_sepolia": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée
        "intentfi_ccip": "0x..."  # À remplacer par l'adresse déployée
    },
    "flow_testnet": {
        "intentfi": "0x...",  # À remplacer par l'adresse déployée
        "intentfi_flow": "0x..."  # Bridge Flow custom
    }
}

# Store des transactions en cours (en production, utiliser une DB)
CCIP_TRANSACTIONS = {}
INTENT_STORAGE = {}

# CoinGecko API configuration (from develop branch)
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL")

# === CCIP UTILITY FUNCTIONS ===

def get_chain_config(chain_name):
    """Récupère la configuration d'une chaîne"""
    return CCIP_CONFIG["supported_chains"].get(chain_name)

def validate_ccip_params(source_chain, dest_chain, amount, token_address=None):
    """Valide les paramètres pour un transfert CCIP"""
    if source_chain not in CCIP_CONFIG["supported_chains"]:
        return False, f"Source chain {source_chain} not supported"
    
    if dest_chain not in CCIP_CONFIG["supported_chains"]:
        return False, f"Destination chain {dest_chain} not supported"
    
    if amount <= 0:
        return False, "Amount must be positive"
    
    if token_address and not is_valid_eth_address(token_address):
        return False, "Invalid token address"
    
    return True, "Valid"

def calculate_ccip_fees(source_chain, dest_chain, data_length):
    """Calcule les frais CCIP estimés"""
    base_fee = CCIP_CONFIG["fee_estimates"]["base_fee"]
    per_byte_fee = CCIP_CONFIG["fee_estimates"]["per_byte"]
    
    total_fee = base_fee + (data_length * per_byte_fee)
    return total_fee

def generate_tx_id():
    """Génère un ID de transaction unique"""
    return f"ccip_{int(time.time() * 1000)}_{hash(str(time.time())) % 10000}"

def call_contract_method(chain_name, contract_address, method_data, from_address=None):
    """Appel générique de méthode de contrat"""
    chain_config = get_chain_config(chain_name)
    if not chain_config:
        return None, "Chain not supported"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [
            {
                "to": contract_address,
                "data": method_data
            } | ({"from": from_address} if from_address else {}),
            "latest"
        ]
    }
    
    try:
        response = requests.post(chain_config["rpc_url"], json=payload, timeout=10)
        data = response.json()
        
        if "result" in data:
            return data["result"], None
        else:
            return None, data.get("error", {}).get("message", "Unknown error")
    except Exception as e:
        return None, str(e)

def send_transaction(chain_name, tx_data, private_key=None):
    """Envoie une transaction (placeholder - nécessite une clé privée)"""
    # En production, cette fonction utiliserait web3.py pour signer et envoyer
    # Pour le moment, on simule
    tx_id = generate_tx_id()
    
    CCIP_TRANSACTIONS[tx_id] = {
        "id": tx_id,
        "chain": chain_name,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tx_data": tx_data,
        "confirmations": 0
    }
    
    return tx_id, None

def estimate_gas(chain_name, tx_data):
    """Estime le gas nécessaire pour une transaction"""
    chain_config = get_chain_config(chain_name)
    if not chain_config:
        return None, "Chain not supported"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_estimateGas",
        "params": [tx_data]
    }
    
    try:
        response = requests.post(chain_config["rpc_url"], json=payload, timeout=10)
        data = response.json()
        
        if "result" in data:
            return int(data["result"], 16), None
        else:
            return None, data.get("error", {}).get("message", "Gas estimation failed")
    except Exception as e:
        return None, str(e)


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
            # Ensure decimals is always a valid integer
            decimals = result.get("decimals")
            if decimals is None or not isinstance(decimals, int):
                decimals = 18
                
            return {
                "name": result.get("name", "Unknown Token"),
                "symbol": result.get("symbol", "???"),
                "decimals": decimals
            }
        else:
            return default_metadata
            
    except Exception as e:
        print(f"Error getting token metadata for {contract_address}: {str(e)}")
        return default_metadata


def safe_decimals(decimals):
    """Ensure decimals is always a valid integer for power operations"""
    if decimals is None or not isinstance(decimals, int) or decimals < 0:
        return 18
    return decimals

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
                
                # Calculer le montant lisible avec sécurité pour les décimales
                decimals = safe_decimals(metadata["decimals"])
                readable_balance = token_balance_int / (10 ** decimals)
                
                token_info = {
                    "contractAddress": balance["contractAddress"],
                    "tokenBalance": balance["tokenBalance"],
                    "readableBalance": readable_balance,
                    "name": metadata["name"],
                    "symbol": metadata["symbol"],
                    "decimals": decimals  # Use the safe decimals value
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
                
                # Calculer le montant lisible avec sécurité pour les décimales
                decimals = safe_decimals(metadata["decimals"])
                readable_balance = token_balance_int / (10 ** decimals)
                
                token_info = {
                    "contractAddress": balance["contractAddress"],
                    "tokenBalance": balance["tokenBalance"],
                    "readableBalance": readable_balance,
                    "name": metadata["name"],
                    "symbol": metadata["symbol"],
                    "decimals": decimals  # Use the safe decimals value
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
                    
                    # Calculer le montant lisible avec sécurité pour les décimales
                    raw_balance = int(balance["tokenBalance"], 16)
                    decimals = safe_decimals(metadata["decimals"])
                    readable_balance = raw_balance / (10 ** decimals)
                    
                    token_info = {
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": decimals,  # Use the safe decimals value
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

@app.route("/tokens/polygon/<address>")
def get_polygon_token_balances(address):
    """Récupère les tokens Polygon Amoy testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
        
    # D'abord récupérer le balance MATIC natif
    matic_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    matic_balance = 0
    try:
        res = requests.post(ALCHEMY_POLYGON_URL, json=matic_payload)
        data = res.json()
        if "result" in data:
            matic_balance = wei_to_eth(data["result"])
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
        res = requests.post(ALCHEMY_POLYGON_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        
        print(f"🔍 DEBUG Polygon - URL: {ALCHEMY_POLYGON_URL}")
        print(f"🔍 DEBUG Polygon - Response status: {res.status_code}")

        if "error" in data:
            return jsonify(create_standard_response(
                chain="polygon_amoy",
                address=address,
                tokens=[],
                error=data["error"]["message"]
            )), 400

        balances = data.get("result", {}).get("tokenBalances", [])
        print(f"🔍 DEBUG Polygon - Total tokens found: {len(balances)}")
        
        non_zero_balances = []
        
        for i, balance in enumerate(balances):
            token_balance_int = int(balance["tokenBalance"], 16)
            
            if token_balance_int > 0:
                # Récupérer les métadonnées du token
                metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_POLYGON_URL)
                
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

        # Ajouter MATIC natif s'il y en a
        result_tokens = []
        if matic_balance > 0:
            result_tokens.append({
                "contractAddress": "native",
                "tokenBalance": hex(int(matic_balance * 10**18)),
                "readableBalance": matic_balance,
                "name": "Polygon",
                "symbol": "MATIC",
                "decimals": 18
            })
        
        result_tokens.extend(non_zero_balances)
        
        # Si aucun token ERC-20 trouvé, essayer avec des tokens spécifiques
        if len(non_zero_balances) == 0:
            print("🔍 DEBUG Polygon - No tokens found with alchemy_getTokenBalances, trying specific tokens...")
            specific_tokens = check_specific_token_balances(address, ALCHEMY_POLYGON_URL, POLYGON_AMOY_POPULAR_TOKENS)
            result_tokens.extend(specific_tokens)

        return jsonify(create_standard_response(
            chain="polygon_amoy",
            address=address,
            tokens=result_tokens,
            native_balance=matic_balance,
            debug_info={
                "total_tokens_checked": len(balances),
                "non_zero_tokens": len(non_zero_balances),
                "specific_tokens_checked": len(POLYGON_AMOY_POPULAR_TOKENS) if len(non_zero_balances) == 0 else 0,
                "api_url": ALCHEMY_POLYGON_URL,
                "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
            }
        ))

    except Exception as e:
        return jsonify(create_standard_response(
            chain="polygon_amoy",
            address=address,
            tokens=[],
            error=str(e)
        )), 500

@app.route("/tokens/arbitrum/<address>")
def get_arbitrum_token_balances(address):
    """Récupère les tokens Arbitrum Sepolia testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
        
    # D'abord récupérer le balance ETH natif sur Arbitrum
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    eth_balance = 0
    try:
        res = requests.post(ALCHEMY_ARBITRUM_URL, json=eth_payload)
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
        res = requests.post(ALCHEMY_ARBITRUM_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        
        print(f"🔍 DEBUG Arbitrum - URL: {ALCHEMY_ARBITRUM_URL}")
        print(f"🔍 DEBUG Arbitrum - Response status: {res.status_code}")

        if "error" in data:
            return jsonify(create_standard_response(
                chain="arbitrum_sepolia",
                address=address,
                tokens=[],
                error=data["error"]["message"]
            )), 400

        balances = data.get("result", {}).get("tokenBalances", [])
        print(f"🔍 DEBUG Arbitrum - Total tokens found: {len(balances)}")
        
        non_zero_balances = []
        
        for i, balance in enumerate(balances):
            token_balance_int = int(balance["tokenBalance"], 16)
            
            if token_balance_int > 0:
                # Récupérer les métadonnées du token
                metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_ARBITRUM_URL)
                
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
        
        # Si aucun token ERC-20 trouvé, essayer avec des tokens spécifiques
        if len(non_zero_balances) == 0:
            print("🔍 DEBUG Arbitrum - No tokens found with alchemy_getTokenBalances, trying specific tokens...")
            specific_tokens = check_specific_token_balances(address, ALCHEMY_ARBITRUM_URL, ARBITRUM_SEPOLIA_POPULAR_TOKENS)
            result_tokens.extend(specific_tokens)

        return jsonify(create_standard_response(
            chain="arbitrum_sepolia",
            address=address,
            tokens=result_tokens,
            native_balance=eth_balance,
            debug_info={
                "total_tokens_checked": len(balances),
                "non_zero_tokens": len(non_zero_balances),
                "specific_tokens_checked": len(ARBITRUM_SEPOLIA_POPULAR_TOKENS) if len(non_zero_balances) == 0 else 0,
                "api_url": ALCHEMY_ARBITRUM_URL,
                "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
            }
        ))

    except Exception as e:
        return jsonify(create_standard_response(
            chain="arbitrum_sepolia",
            address=address,
            tokens=[],
            error=str(e)
        )), 500

@app.route("/tokens/optimism/<address>")
def get_optimism_token_balances(address):
    """Récupère les tokens Optimism Sepolia testnet avec métadonnées"""
    if not is_valid_eth_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
        
    # D'abord récupérer le balance ETH natif sur Optimism
    eth_payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "eth_getBalance",
        "params": [address, "latest"]
    }
    
    eth_balance = 0
    try:
        res = requests.post(ALCHEMY_OPTIMISM_URL, json=eth_payload)
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
        res = requests.post(ALCHEMY_OPTIMISM_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        
        print(f"🔍 DEBUG Optimism - URL: {ALCHEMY_OPTIMISM_URL}")
        print(f"🔍 DEBUG Optimism - Response status: {res.status_code}")

        if "error" in data:
            return jsonify(create_standard_response(
                chain="optimism_sepolia",
                address=address,
                tokens=[],
                error=data["error"]["message"]
            )), 400

        balances = data.get("result", {}).get("tokenBalances", [])
        print(f"🔍 DEBUG Optimism - Total tokens found: {len(balances)}")
        
        non_zero_balances = []
        
        for i, balance in enumerate(balances):
            token_balance_int = int(balance["tokenBalance"], 16)
            
            if token_balance_int > 0:
                # Récupérer les métadonnées du token
                metadata = get_token_metadata(balance["contractAddress"], ALCHEMY_OPTIMISM_URL)
                
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
        
        # Si aucun token ERC-20 trouvé, essayer avec des tokens spécifiques
        if len(non_zero_balances) == 0:
            print("🔍 DEBUG Optimism - No tokens found with alchemy_getTokenBalances, trying specific tokens...")
            specific_tokens = check_specific_token_balances(address, ALCHEMY_OPTIMISM_URL, OPTIMISM_SEPOLIA_POPULAR_TOKENS)
            result_tokens.extend(specific_tokens)

        return jsonify(create_standard_response(
            chain="optimism_sepolia",
            address=address,
            tokens=result_tokens,
            native_balance=eth_balance,
            debug_info={
                "total_tokens_checked": len(balances),
                "non_zero_tokens": len(non_zero_balances),
                "specific_tokens_checked": len(OPTIMISM_SEPOLIA_POPULAR_TOKENS) if len(non_zero_balances) == 0 else 0,
                "api_url": ALCHEMY_OPTIMISM_URL,
                "api_key_preview": f"{ALCHEMY_API_KEY[:8]}..."
            }
        ))

    except Exception as e:
        return jsonify(create_standard_response(
            chain="optimism_sepolia",
            address=address,
            tokens=[],
            error=str(e)
        )), 500

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
        "message": "🚀 IntentFi Multi-Chain API with CCIP Integration (TESTNET)",
        "description": "API complète pour les intents financiers cross-chain avec Chainlink CCIP",
        "version": "2.0.0-ccip",
        "features": [
            "✅ Multi-chain token balances",
            "🔗 CCIP cross-chain transfers",
            "🎯 Automated financial intents",
            "📊 Real-time monitoring",
            "⚡ Chainlink Automation integration"
        ],
        "endpoints": {
            "tokens": {
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
                    "description": "Tokens sur Flow testnet",
                    "example": "/tokens/flow/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                },
                "polygon_tokens": {
                    "url": "/tokens/polygon/<address>",
                    "description": "Tokens sur Polygon Amoy testnet",
                    "example": "/tokens/polygon/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                },
                "arbitrum_tokens": {
                    "url": "/tokens/arbitrum/<address>",
                    "description": "Tokens sur Arbitrum Sepolia testnet",
                    "example": "/tokens/arbitrum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                },
                "optimism_tokens": {
                    "url": "/tokens/optimism/<address>",
                    "description": "Tokens sur Optimism Sepolia testnet",
                    "example": "/tokens/optimism/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                }
            },
            "ccip": {
                "supported_chains": {
                    "url": "/ccip/chains",
                    "description": "Liste des chaînes supportées pour CCIP",
                    "method": "GET"
                },
                "calculate_fees": {
                    "url": "/ccip/fees/<source_chain>/<dest_chain>",
                    "description": "Calcule les frais pour un transfert CCIP",
                    "method": "POST",
                    "example": "/ccip/fees/ethereum_sepolia/base_sepolia"
                },
                "initiate_transfer": {
                    "url": "/ccip/transfer",
                    "description": "Initie un transfert cross-chain via CCIP",
                    "method": "POST",
                    "body": {
                        "source_chain": "ethereum_sepolia",
                        "destination_chain": "base_sepolia", 
                        "amount": 0.1,
                        "token_address": None,
                        "receiver": "0x...",
                        "sender": "0x..."
                    }
                },
                "transaction_status": {
                    "url": "/ccip/status/<tx_id>",
                    "description": "Statut d'une transaction CCIP",
                    "example": "/ccip/status/ccip_1234567890_1234"
                },
                "user_history": {
                    "url": "/ccip/history/<address>",
                    "description": "Historique CCIP d'un utilisateur",
                    "example": "/ccip/history/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                }
            },
            "intents": {
                "create_intent": {
                    "url": "/intent/create",
                    "description": "Crée un intent financier automatisé",
                    "method": "POST",
                    "body": {
                        "owner": "0x...",
                        "intent_type": "SEND_IF_PRICE_ABOVE",
                        "trigger_price": 3500,
                        "amount": 0.1,
                        "source_chain": "ethereum_sepolia",
                        "destination_chain": "base_sepolia",
                        "receiver": "0x..."
                    }
                },
                "intent_status": {
                    "url": "/intent/status/<intent_id>",
                    "description": "Statut d'un intent",
                    "example": "/intent/status/intent_1234567890_1234"
                },
                "execute_intent": {
                    "url": "/intent/execute/<intent_id>",
                    "description": "Exécute un intent manuellement",
                    "method": "POST"
                },
                "list_intents": {
                    "url": "/intent/list/<owner_address>",
                    "description": "Liste les intents d'un utilisateur",
                    "example": "/intent/list/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                },
                "cancel_intent": {
                    "url": "/intent/cancel/<intent_id>",
                    "description": "Annule un intent",
                    "method": "POST"
                }
            },
            "monitoring": {
                "ccip_analytics": {
                    "url": "/ccip/analytics",
                    "description": "Statistiques des transactions CCIP"
                },
                "intent_analytics": {
                    "url": "/intent/analytics", 
                    "description": "Statistiques des intents"
                },
                "health_check": {
                    "url": "/ccip/health",
                    "description": "Santé du système CCIP"
                },
                "supported_tokens": {
                    "url": "/ccip/supported-tokens/<chain_name>",
                    "description": "Tokens supportés par chaîne",
                    "example": "/ccip/supported-tokens/ethereum_sepolia"
                },
                "estimate_time": {
                    "url": "/ccip/estimate-time/<source_chain>/<dest_chain>",
                    "description": "Estime le temps de transfert",
                    "example": "/ccip/estimate-time/ethereum_sepolia/base_sepolia"
                }
            },
            "utilities": {
                "quick_check": {
                    "url": "/check-balance/<address>",
                    "description": "Vérification rapide du balance",
                    "example": "/check-balance/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                },
                "faucet_info": {
                    "url": "/faucet-sepolia",
                    "description": "Guide pour obtenir des tokens testnet"
                },
                "test_api": {
                    "url": "/test-api",
                    "description": "Test de connectivité des APIs"
                }
            }
        },
        "smart_contracts": {
            "intentfi": "Contrat principal pour les intents financiers",
            "intentfi_ccip": "Extension CCIP pour les transferts cross-chain",
            "supported_chains": ["Ethereum Sepolia", "Base Sepolia"]
        },
        "chainlink_integration": {
            "price_feeds": "ETH/USD real-time price data",
            "automation": "Automated intent execution",
            "ccip": "Cross-chain interoperability"
        },
        "ai_agent": {
            "recommend": "http://localhost:8001/recommend",
            "health": "http://localhost:8001/health"
        },
        "networks": {
            "ethereum_sepolia": {
                "chain_id": 11155111,
                "explorer": "https://sepolia.etherscan.io",
                "faucet": "https://sepoliafaucet.com"
            },
            "base_sepolia": {
                "chain_id": 84532,
                "explorer": "https://sepolia.basescan.org",
                "faucet": "https://bridge.base.org"
            }
        },
        "usage": "Remplacez <address> par une adresse Ethereum valide (0x...)",
        "documentation": "Voir les endpoints ci-dessus pour l'utilisation complète de l'API"
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
                    decimals = safe_decimals(metadata["decimals"])
                    readable_balance = balance_int / (10 ** decimals)
                    
                    tokens_with_balance.append({
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": decimals  # Use the safe decimals value
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
                    
                    # Calculer le montant lisible avec sécurité pour les décimales
                    raw_balance = int(balance["tokenBalance"], 16)
                    decimals = safe_decimals(metadata["decimals"])
                    readable_balance = raw_balance / (10 ** decimals)
                    
                    token_info = {
                        "contractAddress": balance["contractAddress"],
                        "tokenBalance": balance["tokenBalance"],
                        "readableBalance": readable_balance,
                        "name": metadata["name"],
                        "symbol": metadata["symbol"],
                        "decimals": decimals,  # Use the safe decimals value
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

# Tokens populaires sur Polygon Amoy pour tests
POLYGON_AMOY_POPULAR_TOKENS = [
    {
        "address": "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582", # USDC sur Polygon Amoy
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6
    },
    {
        "address": "0x360ad4f9a9A8EFe9A8DCB5f461c4Cc1047E1Dcf9", # WETH sur Polygon Amoy
        "name": "Wrapped Ether",
        "symbol": "WETH",
        "decimals": 18
    },
    {
        "address": "0x0Fd9e8d3aF1aaee056EB9e802c3A762a667b1904", # LINK sur Polygon Amoy
        "name": "Chainlink Token",
        "symbol": "LINK",
        "decimals": 18
    }
]

# Tokens populaires sur Arbitrum Sepolia pour tests
ARBITRUM_SEPOLIA_POPULAR_TOKENS = [
    {
        "address": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d", # USDC sur Arbitrum Sepolia
        "name": "USD Coin", 
        "symbol": "USDC",
        "decimals": 6
    },
    {
        "address": "0x980B62Da83eFf3D4576C647993b0c1D7faf17c73", # WETH sur Arbitrum Sepolia
        "name": "Wrapped Ether",
        "symbol": "WETH",
        "decimals": 18
    },
    {
        "address": "0xb1D4538B4571d411F07960EF2838Ce337FE1E80E", # LINK sur Arbitrum Sepolia
        "name": "Chainlink Token",
        "symbol": "LINK",
        "decimals": 18
    }
]

# Tokens populaires sur Optimism Sepolia pour tests
OPTIMISM_SEPOLIA_POPULAR_TOKENS = [
    {
        "address": "0x5fd84259d66Cd46123540766Be93DFE6D43130D7", # USDC sur Optimism Sepolia
        "name": "USD Coin",
        "symbol": "USDC", 
        "decimals": 6
    },
    {
        "address": "0x4200000000000000000000000000000000000006", # WETH sur Optimism Sepolia
        "name": "Wrapped Ether",
        "symbol": "WETH",
        "decimals": 18
    },
    {
        "address": "0xE4aB69C077896252FAFBD49EFD26B5D171A32410", # LINK sur Optimism Sepolia
        "name": "Chainlink Token",
        "symbol": "LINK",
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
                    # Use safe decimals to prevent NoneType errors
                    decimals = safe_decimals(token["decimals"])
                    readable_balance = balance_int / (10 ** decimals)
                    
                    token_info = {
                        "contractAddress": token["address"],
                        "tokenBalance": balance_hex,
                        "readableBalance": readable_balance,
                        "name": token["name"],
                        "symbol": token["symbol"],
                        "decimals": decimals
                    }
                    tokens_found.append(token_info)
                    print(f"✅ Found specific token: {token['symbol']} = {readable_balance}")
                    
        except Exception as e:
            print(f"❌ Error checking token {token['symbol']}: {str(e)}")
            continue
            
    return tokens_found

# === CCIP ENDPOINTS ===

@app.route("/ccip/chains")
def get_supported_chains():
    """Liste toutes les chaînes supportées pour CCIP"""
    chains_info = []
    for chain_name, config in CCIP_CONFIG["supported_chains"].items():
        chains_info.append({
            "name": chain_name,
            "chain_id": config["chain_id"],
            "selector": config["selector"],
            "native_symbol": config["native_symbol"],
            "router": config["router"],
            "link_token": config["link_token"]
        })
    
    return jsonify({
        "success": True,
        "chains": chains_info,
        "total_chains": len(chains_info),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/ccip/fees/<source_chain>/<dest_chain>", methods=["POST"])
def calculate_transfer_fees(source_chain, dest_chain):
    """Calcule les frais pour un transfert CCIP"""
    try:
        data = request.get_json() or {}
        amount = data.get("amount", 0)
        token_address = data.get("token_address")
        receiver = data.get("receiver", "0x0000000000000000000000000000000000000000")
        
        # Validation
        is_valid, error_msg = validate_ccip_params(source_chain, dest_chain, amount, token_address)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400
        
        # Calculer la taille des données
        message_data = {
            "receiver": receiver,
            "amount": amount,
            "token": token_address or "native"
        }
        data_length = len(json.dumps(message_data).encode())
        
        # Calculer les frais
        estimated_fee = calculate_ccip_fees(source_chain, dest_chain, data_length)
        
        # Récupérer le prix actuel de LINK (simulation)
        link_price_usd = 7.5  # Prix fixe pour la demo
        fee_usd = estimated_fee * link_price_usd
        
        return jsonify({
            "success": True,
            "source_chain": source_chain,
            "destination_chain": dest_chain,
            "fees": {
                "link_amount": estimated_fee,
                "usd_estimate": fee_usd,
                "data_size_bytes": data_length,
                "breakdown": {
                    "base_fee": CCIP_CONFIG["fee_estimates"]["base_fee"],
                    "data_fee": data_length * CCIP_CONFIG["fee_estimates"]["per_byte"]
                }
            },
            "link_token": get_chain_config(source_chain)["link_token"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/ccip/transfer", methods=["POST"])
def initiate_ccip_transfer():
    """Initie un transfert cross-chain via CCIP"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Extraction des paramètres
        source_chain = data.get("source_chain")
        dest_chain = data.get("destination_chain")
        amount = float(data.get("amount", 0))
        token_address = data.get("token_address")  # None pour native token
        receiver = data.get("receiver")
        sender = data.get("sender")
        
        # Validation
        if not all([source_chain, dest_chain, receiver, sender]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: source_chain, destination_chain, receiver, sender"
            }), 400
        
        if not is_valid_eth_address(receiver) or not is_valid_eth_address(sender):
            return jsonify({"success": False, "error": "Invalid address format"}), 400
        
        is_valid, error_msg = validate_ccip_params(source_chain, dest_chain, amount, token_address)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400
        
        # Générer un ID de transaction
        tx_id = generate_tx_id()
        
        # Préparer les données de transaction
        source_config = get_chain_config(source_chain)
        dest_config = get_chain_config(dest_chain)
        
        # Calculer les frais
        message_data = {"receiver": receiver, "amount": amount, "token": token_address or "native"}
        data_length = len(json.dumps(message_data).encode())
        estimated_fee = calculate_ccip_fees(source_chain, dest_chain, data_length)
        
        # Créer la transaction CCIP (simulation)
        ccip_tx_data = {
            "to": source_config["router"],
 "data": f"0xcrosschain_{dest_config['selector']}_{receiver}_{amount}",
            "value": hex(int(amount * 10**18)) if not token_address else "0x0",
            "gas": "0x5208"  # Gas estimation simplifiée
        }
        
        # Stocker la transaction
        CCIP_TRANSACTIONS[tx_id] = {
            "id": tx_id,
            "source_chain": source_chain,
            "destination_chain": dest_chain,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token_address": token_address,
            "estimated_fee": estimated_fee,
            "status": "initiated",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tx_hash": None,
            "ccip_message_id": None,
            "confirmations": 0
        }
        
        # Simuler l'envoi (en production, utiliser web3.py)
        simulated_tx_hash = f"0x{hash(tx_id) % (16**64):064x}"
        CCIP_TRANSACTIONS[tx_id]["tx_hash"] = simulated_tx_hash
        CCIP_TRANSACTIONS[tx_id]["status"] = "pending"
        
        return jsonify({
            "success": True,
            "transaction_id": tx_id,
            "tx_hash": simulated_tx_hash,
            "source_chain": source_chain,
            "destination_chain": dest_chain,
            "amount": amount,
            "token": token_address or "native",
            "estimated_fee_link": estimated_fee,
            "status": "pending",
            "message": "CCIP transfer initiated successfully",
            "monitoring_url": f"/ccip/status/{tx_id}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/ccip/status/<tx_id>")
def get_ccip_status(tx_id):
    """Récupère le statut d'un transfert CCIP"""
    if tx_id not in CCIP_TRANSACTIONS:
        return jsonify({
            "success": False,
            "error": "Transaction not found"
        }), 404
    
    tx_data = CCIP_TRANSACTIONS[tx_id]
    
    # Simuler l'évolution du statut basé sur l'âge de la transaction
    created_time = datetime.fromisoformat(tx_data["created_at"].replace('Z', '+00:00'))
    age_seconds = (datetime.now(timezone.utc) - created_time).total_seconds()
    
    # Mise à jour du statut simulé
    if age_seconds > 300:  # 5 minutes
        tx_data["status"] = "completed"
        tx_data["confirmations"] = 12
        tx_data["ccip_message_id"] = f"0x{hash(tx_id + 'message') % (16**64):064x}"
    elif age_seconds > 120:  # 2 minutes
        tx_data["status"] = "confirming"
        tx_data["confirmations"] = 6
    elif age_seconds > 60:  # 1 minute
        tx_data["status"] = "sent"
        tx_data["confirmations"] = 1
    
    return jsonify({
        "success": True,
        "transaction": tx_data,
        "age_seconds": int(age_seconds),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/ccip/history/<address>")
def get_ccip_history(address):
    """Récupère l'historique CCIP pour une adresse"""
    if not is_valid_eth_address(address):
        return jsonify({"success": False, "error": "Invalid address"}), 400
    
    # Filtrer les transactions pour cette adresse
    user_transactions = []
    for tx_id, tx_data in CCIP_TRANSACTIONS.items():
        if tx_data.get("sender") == address or tx_data.get("receiver") == address:
            user_transactions.append(tx_data)
    
    # Trier par date de création (plus récent en premier)
    user_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return jsonify({
        "success": True,
        "address": address,
        "transactions": user_transactions,
        "total_count": len(user_transactions),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# === MONITORING & ANALYTICS ENDPOINTS ===

@app.route("/ccip/analytics")
def get_ccip_analytics():
    """Fournit des statistiques sur les transactions CCIP"""
    total_txs = len(CCIP_TRANSACTIONS)
    completed_txs = len([tx for tx in CCIP_TRANSACTIONS.values() if tx["status"] == "completed"])
    pending_txs = len([tx for tx in CCIP_TRANSACTIONS.values() if tx["status"] in ["pending", "sent", "confirming"]])
    failed_txs = len([tx for tx in CCIP_TRANSACTIONS.values() if tx["status"] == "failed"])
    
    # Calculer le volume total
    total_volume = sum([tx.get("amount", 0) for tx in CCIP_TRANSACTIONS.values()])
    
    # Analyse par chaîne
    chain_stats = {}
    for tx in CCIP_TRANSACTIONS.values():
        source = tx.get("source_chain", "unknown")
        dest = tx.get("destination_chain", "unknown")
        
        if source not in chain_stats:
            chain_stats[source] = {"sent": 0, "received": 0, "volume_sent": 0, "volume_received": 0}
        if dest not in chain_stats:
            chain_stats[dest] = {"sent": 0, "received": 0, "volume_sent": 0, "volume_received": 0}
        
        chain_stats[source]["sent"] += 1
        chain_stats[dest]["received"] += 1
        chain_stats[source]["volume_sent"] += tx.get("amount", 0)
        chain_stats[dest]["volume_received"] += tx.get("amount", 0)
    
    return jsonify({
        "success": True,
        "analytics": {
            "total_transactions": total_txs,
            "completed_transactions": completed_txs,
            "pending_transactions": pending_txs,
            "failed_transactions": failed_txs,
            "success_rate": (completed_txs / total_txs * 100) if total_txs > 0 else 0,
            "total_volume": total_volume,
            "chain_statistics": chain_stats,
            "average_completion_time": "2.5 minutes"  # Simulé
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/intent/analytics")
def get_intent_analytics():
    """Fournit des statistiques sur les intents"""
    total_intents = len(INTENT_STORAGE)
    active_intents = len([i for i in INTENT_STORAGE.values() if i["status"] == "active"])
    executed_intents = len([i for i in INTENT_STORAGE.values() if i["status"] == "executed"])
    cancelled_intents = len([i for i in INTENT_STORAGE.values() if i["status"] == "cancelled"])
    
    # Analyse par type d'intent
    type_stats = {}
    for intent in INTENT_STORAGE.values():
        intent_type = intent.get("intent_type", "unknown")
        if intent_type not in type_stats:
            type_stats[intent_type] = {"count": 0, "executed": 0, "total_volume": 0}
        
        type_stats[intent_type]["count"] += 1
        if intent["status"] == "executed":
            type_stats[intent_type]["executed"] += 1
        type_stats[intent_type]["total_volume"] += intent.get("amount", 0)
    
    # Calculer les intents cross-chain
    ccip_intents = len([i for i in INTENT_STORAGE.values() if i.get("is_ccip", False)])
    
    return jsonify({
        "success": True,
        "analytics": {
            "total_intents": total_intents,
            "active_intents": active_intents,
            "executed_intents": executed_intents,
            "cancelled_intents": cancelled_intents,
            "ccip_intents": ccip_intents,
            "execution_rate": (executed_intents / total_intents * 100) if total_intents > 0 else 0,
            "intent_type_breakdown": type_stats
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/ccip/supported-tokens/<chain_name>")
def get_supported_tokens(chain_name):
    """Liste les tokens supportés pour CCIP sur une chaîne"""
    chain_config = get_chain_config(chain_name)
    if not chain_config:
        return jsonify({
            "success": False,
            "error": f"Chain {chain_name} not supported"
        }), 400
    
    # Tokens couramment supportés par CCIP (exemples)
    supported_tokens = [
        {
            "symbol": "ETH",
            "name": "Ethereum",
            "address": "native",
            "decimals": 18,
            "is_native": True
        },
        {
            "symbol": "LINK",
            "name": "Chainlink",
            "address": chain_config["link_token"],
            "decimals": 18,
            "is_native": False
        },
        {
            "symbol": "USDC",
            "name": "USD Coin",
            "address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e" if "base" in chain_name else "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "decimals": 6,
            "is_native": False
        }
    ]
    
    return jsonify({
        "success": True,
        "chain": chain_name,
        "chain_id": chain_config["chain_id"],
        "supported_tokens": supported_tokens,
        "total_tokens": len(supported_tokens),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/ccip/estimate-time/<source_chain>/<dest_chain>")
def estimate_transfer_time(source_chain, dest_chain):
    """Estime le temps de transfert CCIP entre deux chaînes"""
    if source_chain not in CCIP_CONFIG["supported_chains"] or dest_chain not in CCIP_CONFIG["supported_chains"]:
        return jsonify({
            "success": False,
            "error": "One or both chains not supported"
        }), 400
    
    # Estimations basées sur les performances CCIP observées
    time_estimates = {
        ("ethereum_sepolia", "base_sepolia"): {"min": 90, "avg": 150, "max": 300},
        ("base_sepolia", "ethereum_sepolia"): {"min": 120, "avg": 180, "max": 360},
        # Ajouter d'autres paires au besoin
    }
    
    key = (source_chain, dest_chain)
    reverse_key = (dest_chain, source_chain)
    
    if key in time_estimates:
        estimate = time_estimates[key]
    elif reverse_key in time_estimates:
        estimate = time_estimates[reverse_key]
    else:
        # Estimation par défaut
        estimate = {"min": 120, "avg": 240, "max": 480}
    
    return jsonify({
        "success": True,
        "source_chain": source_chain,
        "destination_chain": dest_chain,
        "estimated_time_seconds": estimate,
        "estimated_time_human": {
            "min": f"{estimate['min']//60}m {estimate['min']%60}s",
            "avg": f"{estimate['avg']//60}m {estimate['avg']%60}s",
            "max": f"{estimate['max']//60}m {estimate['max']%60}s"
        },
        "factors": [
            "Network congestion",
            "Gas prices",
            "CCIP lane activity",
            "Destination chain block time"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/ccip/health")
def ccip_health_check():
    """Vérifie la santé du système CCIP"""
    health_status = {
        "overall": "healthy",
        "chains": {},
        "services": {
            "ccip_router": "operational",
            "price_feeds": "operational",
            "automation": "operational"
        }
    }
    
    # Vérifier chaque chaîne
    for chain_name, config in CCIP_CONFIG["supported_chains"].items():
        try:
            # Test de connectivité RPC
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_blockNumber",
                "params": []
            }
            
            response = requests.post(config["rpc_url"], json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    block_number = int(data["result"], 16)
                    health_status["chains"][chain_name] = {
                        "status": "healthy",
                        "latest_block": block_number,
                        "rpc_responsive": True
                    }
                else:
                    health_status["chains"][chain_name] = {
                        "status": "degraded",
                        "rpc_responsive": False,
                        "error": data.get("error", "Unknown error")
                    }
            else:
                health_status["chains"][chain_name] = {
                    "status": "unhealthy",
                    "rpc_responsive": False,
                    "http_status": response.status_code
                }
        except Exception as e:
            health_status["chains"][chain_name] = {
                "status": "unhealthy",
                "rpc_responsive": False,
                "error": str(e)
            }
    
    # Déterminer le statut global
    unhealthy_chains = [name for name, status in health_status["chains"].items() if status["status"] == "unhealthy"]
    if unhealthy_chains:
        health_status["overall"] = "degraded" if len(unhealthy_chains) < len(health_status["chains"]) else "unhealthy"
    
    return jsonify({
        "success": True,
        "health": health_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "99.9%"  # Simulé
    })

# === INTENT ENDPOINTS ===

@app.route("/intent/create", methods=["POST"])
def create_intent():
    """Crée un intent financier automatisé"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Extraction des paramètres
        owner = data.get("owner")
        intent_type = data.get("intent_type")
        trigger_price = data.get("trigger_price")
        amount = float(data.get("amount", 0))
        source_chain = data.get("source_chain")
        destination_chain = data.get("destination_chain")
        receiver = data.get("receiver")
        token_address = data.get("token_address")
        
        # Validation
        if not all([owner, intent_type, trigger_price, amount, source_chain, receiver]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: owner, intent_type, trigger_price, amount, source_chain, receiver"
            }), 400
        
        if not is_valid_eth_address(owner) or not is_valid_eth_address(receiver):
            return jsonify({"success": False, "error": "Invalid address format"}), 400
        
        # Générer un ID d'intent
        intent_id = f"intent_{int(time.time() * 1000)}_{hash(owner) % 10000}"
        
        # Créer l'intent
        intent_data = {
            "id": intent_id,
            "owner": owner,
            "intent_type": intent_type,
            "trigger_price": trigger_price,
            "amount": amount,
            "source_chain": source_chain,
            "destination_chain": destination_chain,
            "receiver": receiver,
            "token_address": token_address,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "executed_at": None,
            "tx_hash": None,
            "execution_count": 0
        }
        
        # Stocker l'intent
        INTENT_STORAGE[intent_id] = intent_data
        
        return jsonify({
            "success": True,
            "intent_id": intent_id,
            "intent": intent_data,
            "message": "Intent created successfully",
            "monitoring_url": f"/intent/status/{intent_id}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/intent/status/<intent_id>")
def get_intent_status(intent_id):
    """Récupère le statut d'un intent"""
    if intent_id not in INTENT_STORAGE:
        return jsonify({
            "success": False,
            "error": "Intent not found"
        }), 404
    
    intent_data = INTENT_STORAGE[intent_id]
    
    # Simuler la vérification du prix ETH pour l'exécution automatique
    current_eth_price = 3450  # Prix simulé
    
    # Vérifier si l'intent doit être exécuté
    if (intent_data["status"] == "active" and 
        intent_data["intent_type"] == "SEND_IF_PRICE_ABOVE" and 
        current_eth_price > intent_data["trigger_price"]):
        
        intent_data["status"] = "ready_to_execute"
        intent_data["current_price"] = current_eth_price
    
    return jsonify({
        "success": True,
        "intent": intent_data,
        "current_eth_price": current_eth_price,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/intent/execute/<intent_id>", methods=["POST"])
def execute_intent(intent_id):
    """Exécute un intent manuellement ou automatiquement"""
    if intent_id not in INTENT_STORAGE:
        return jsonify({
            "success": False,
            "error": "Intent not found"
        }), 404
    
    intent_data = INTENT_STORAGE[intent_id]
    
    if intent_data["status"] != "active":
        return jsonify({
            "success": False,
            "error": f"Intent is not active (current status: {intent_data['status']})"
        }), 400
    
    try:
        # Simuler l'exécution de l'intent via CCIP
        if intent_data.get("destination_chain"):
            # Cross-chain intent - utiliser CCIP
            ccip_data = {
                "source_chain": intent_data["source_chain"],
                "destination_chain": intent_data["destination_chain"],
                "amount": intent_data["amount"],
                "token_address": intent_data.get("token_address"),
                "receiver": intent_data["receiver"],
                "sender": intent_data["owner"]
            }
            
            # Simuler l'appel CCIP
            tx_id = generate_tx_id()
            simulated_tx_hash = f"0x{hash(intent_id + str(time.time())) % (16**64):064x}"
            
            # Mettre à jour l'intent
            intent_data["status"] = "executed"
            intent_data["executed_at"] = datetime.now(timezone.utc).isoformat()
            intent_data["tx_hash"] = simulated_tx_hash
            intent_data["ccip_tx_id"] = tx_id
            intent_data["execution_count"] += 1
            
            return jsonify({
                "success": True,
                "intent_id": intent_id,
                "execution_result": "success",
                "tx_hash": simulated_tx_hash,
                "ccip_tx_id": tx_id,
                "message": "Intent executed successfully via CCIP"
            })
        
        else:
            # Same-chain intent
            simulated_tx_hash = f"0x{hash(intent_id + str(time.time())) % (16**64):064x}"
            
            intent_data["status"] = "executed"
            intent_data["executed_at"] = datetime.now(timezone.utc).isoformat()
            intent_data["tx_hash"] = simulated_tx_hash
            intent_data["execution_count"] += 1
            
            return jsonify({
                "success": True,
                "intent_id": intent_id,
                "execution_result": "success",
                "tx_hash": simulated_tx_hash,
                "message": "Intent executed successfully"
            })
            
    except Exception as e:
        intent_data["status"] = "failed"
        intent_data["error"] = str(e)
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/intent/list/<owner_address>")
def list_user_intents(owner_address):
    """Liste les intents d'un utilisateur"""

    if not is_valid_eth_address(owner_address):
        return jsonify({"success": False, "error": "Invalid address"}), 400
    
    # Filtrer les intents pour cet utilisateur
    user_intents = []
    for intent_id, intent_data in INTENT_STORAGE.items():
        if intent_data.get("owner") == owner_address:
            user_intents.append(intent_data)
    
    # Trier par date de création (plus récent en premier)
    user_intents.sort(key=lambda x: x["created_at"], reverse=True)
    
    return jsonify({
        "success": True,
        "owner": owner_address,
        "intents": user_intents,
        "total_count": len(user_intents),
        "active_count": len([i for i in user_intents if i["status"] == "active"]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/intent/cancel/<intent_id>", methods=["POST"])
def cancel_intent(intent_id):
    """Annule un intent"""
    if intent_id not in INTENT_STORAGE:
        return jsonify({
            "success": False,
            "error": "Intent not found"
        }), 404
    
    intent_data = INTENT_STORAGE[intent_id]
    
    if intent_data["status"] not in ["active", "ready_to_execute"]:
        return jsonify({
            "success": False,
            "error": f"Cannot cancel intent with status: {intent_data['status']}"
        }), 400
    
    intent_data["status"] = "cancelled"
    intent_data["cancelled_at"] = datetime.now(timezone.utc).isoformat()
    
    return jsonify({
        "success": True,
        "intent_id": intent_id,
        "message": "Intent cancelled successfully",
        "intent": intent_data
    })

# === ADDITIONAL UTILITY ENDPOINTS ===

@app.route("/admin/reset-data", methods=["POST"])
def reset_data():
    """Reset toutes les données (utile pour les tests)"""
    global CCIP_TRANSACTIONS, INTENT_STORAGE
    
    CCIP_TRANSACTIONS.clear()
    INTENT_STORAGE.clear()
    
    return jsonify({
        "success": True,
        "message": "All data reset successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/admin/mock-data", methods=["POST"])
def create_mock_data():
    """Crée des données de test pour la démo"""
    # Créer quelques transactions CCIP de test
    for i in range(3):
        tx_id = f"ccip_mock_{int(time.time())}_{i}"
        CCIP_TRANSACTIONS[tx_id] = {
            "id": tx_id,
            "source_chain": "ethereum_sepolia",
            "destination_chain": "base_sepolia",
            "sender": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "receiver": "0x604bbc860e08198086F682355842522F7b099007",
            "amount": 0.1 * (i + 1),
            "token_address": None,
            "estimated_fee": 0.001,
            "status": ["completed", "pending", "failed"][i],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tx_hash": f"0x{hash(tx_id) % (16**64):064x}",
            "confirmations": [12, 3, 0][i]
        }
    
    # Créer quelques intents de test
    for i in range(2):
        intent_id = f"intent_mock_{int(time.time())}_{i}"
        INTENT_STORAGE[intent_id] = {
            "id": intent_id,
            "owner": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "intent_type": "SEND_IF_PRICE_ABOVE",
            "trigger_price": 3400 + (i * 100),
            "amount": 0.05 * (i + 1),
            "source_chain": "ethereum_sepolia",
            "destination_chain": "base_sepolia",
            "receiver": "0x604bbc860e08198086F682355842522F7b099007",
            "token_address": None,
            "status": ["active", "executed"][i],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "executed_at": datetime.now(timezone.utc).isoformat() if i == 1 else None,
            "tx_hash": f"0x{hash(intent_id) % (16**64):064x}" if i == 1 else None,
            "execution_count": i
        }
    
    return jsonify({
        "success": True,
        "message": "Mock data created successfully",
        "created": {
            "ccip_transactions": len([tx for tx in CCIP_TRANSACTIONS.keys() if "mock" in tx]),
            "intents": len([intent for intent in INTENT_STORAGE.keys() if "mock" in intent])
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

if __name__ == "__main__":
    print("🚀 Starting IntentFi Multi-Chain API with CCIP Integration")
    print("📊 Available endpoints:")
    print("   - Token balances: /tokens/{chain}/{address}")
    print("   - CCIP transfers: /ccip/transfer")
    print("   - Intent creation: /intent/create")
    print("   - Analytics: /ccip/analytics, /intent/analytics")
    print("   - Health check: /ccip/health")
    print("   - Full documentation: /")
    app.run(host="0.0.0.0", port=5001, debug=True)