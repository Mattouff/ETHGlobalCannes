# IntentFi Multi-Chain Token API

A Flask-based API that retrieves token balances across multiple blockchain testnets using Alchemy's infrastructure with real-time USD pricing via CoinGecko.

## Purpose

This API provides a unified interface to query token balances and USD values on:

- **Ethereum Sepolia Testnet**
- **Base Sepolia Testnet**
- **Flow Testnet**

Built for the ETH Global Cannes hackathon to support multi-chain token analysis and portfolio valuation.

## Quick Start

```bash
# Install dependencies
pip install flask requests

# Run the API
python app.py
```

The API runs on `http://localhost:5001`

## Key Endpoints

| Endpoint                         | Description                               |
| -------------------------------- | ----------------------------------------- |
| `GET /`                          | API documentation and available endpoints |
| `GET /tokens/all/<address>`      | Get tokens from all supported chains      |
| `GET /tokens/ethereum/<address>` | Ethereum Sepolia tokens with USD values   |
| `GET /tokens/base/<address>`     | Base Sepolia tokens with USD values       |
| `GET /tokens/flow/<address>`     | Flow testnet tokens with USD values       |
| `GET /check-balance/<address>`   | Quick balance verification                |
| `GET /faucet-sepolia`            | Testnet faucet information                |

## Example Usage

```bash
# Check all tokens for an address with USD values
curl http://localhost:5001/tokens/all/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Get Ethereum tokens with real-time pricing
curl http://localhost:5001/tokens/ethereum/0xYourAddress

# Quick balance check
curl http://localhost:5001/check-balance/0xYourAddress
```

## Features

- ✅ Multi-chain support (Ethereum, Base, Flow testnets)
- ✅ Native token balance detection
- ✅ ERC-20 token metadata retrieval
- ✅ **Real-time USD pricing via CoinGecko API**
- ✅ **Accurate total wallet value calculation**
- ✅ **Contract address-based price lookup**
- ✅ **Platform-aware pricing (ethereum, base, flow)**
- ✅ Standardized response format with USD values
- ✅ Debug endpoints for troubleshooting
- ✅ Testnet faucet guidance

## Pricing Integration

**CoinGecko API Configuration:**

- API Key: `CG-mr7yWjrfkrQADpfyEaRDUDMM` (pre-configured)
- Base URL: `https://api.coingecko.com/api/v3`

**Price Lookup Strategy:**

1. **ERC-20 Tokens**: Uses contract address via `/simple/token_price/{platform}` endpoint
2. **Native Tokens**: Uses coin ID via `/simple/price` endpoint (ETH, FLOW, BTC)
3. **Fallback**: Returns $0 for unknown tokens

**Supported Platforms:**

- `ethereum` - Ethereum Sepolia
- `base` - Base Sepolia
- `flow` - Flow Testnet

## Configuration

Update the following API keys in `app.py`:

- `ALCHEMY_API_KEY`: Your Alchemy API key for blockchain data
- `COINGECKO_API_KEY`: Your CoinGecko API key for pricing data

## Response Format

```json
{
  "success": true,
  "chain": "ethereum_sepolia",
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "timestamp": "2024-12-15T14:30:00Z",
  "api_version": "1.0",
  "tokens": [
    {
      "contractAddress": "native",
      "readableBalance": 1.5,
      "name": "Ethereum",
      "symbol": "ETH",
      "decimals": 18,
      "price_usd": 2516.66,
      "value_usd": 3774.99
    },
    {
      "contractAddress": "0xA0b86a33E6441023f7E97eD5ebD4d1BdEF1a0C8c",
      "readableBalance": 1000.0,
      "name": "USD Coin",
      "symbol": "USDC",
      "decimals": 6,
      "price_usd": 1.0,
      "value_usd": 1000.0
    }
  ],
  "token_count": 2,
  "native_balance": 1.5,
  "total_value_usd": 4774.99
}
```

## USD Value Fields

Each token includes:

- `price_usd`: Real-time USD price per token
- `value_usd`: Total USD value (balance × price)

Response includes:

- `total_value_usd`: Sum of all token values in the wallet

## Error Handling

```json
{
  "success": false,
  "chain": "ethereum_sepolia",
  "address": "invalid_address",
  "error": "Invalid Ethereum address format",
  "tokens": [],
  "token_count": 0,
  "native_balance": 0,
  "total_value_usd": 0
}
```

## Development Notes

- Built with Flask for the ETH Global Cannes hackathon
- Uses Alchemy for blockchain data and CoinGecko for pricing
- Simplified pricing logic: contract address first, symbol fallback for native tokens
- All testnet data with real-time USD valuations
