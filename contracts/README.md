# IntentFi - Autonomous Financial Intent Protocol

## 🎯 Overview

IntentFi is a smart contract protocol that enables users to create autonomous financial intents that execute automatically based on market conditions. Built for ETH Global Cannes 2025.

## 🔗 Core Features

### Chainlink Integration
- **Price Feeds**: Real-time ETH/USD price data for triggers
- **Automation**: Automated intent execution via `checkUpkeep`/`performUpkeep`
- **Cross-Chain Ready**: Prepared for CCIP integration

### Intent Types
- `SEND_IF_PRICE_ABOVE`: Execute when price goes above threshold
- `SEND_IF_PRICE_BELOW`: Execute when price goes below threshold
- `CROSS_CHAIN_SWAP`: Cross-chain token swaps (coming soon)
- `AUTOMATED_DCA`: Dollar cost averaging (coming soon)

### Supported Assets
- **ETH**: Native Ethereum transfers
- **ERC20 Tokens**: Any standard token (USDC, WETH, etc.)

## 📊 Contract Details

### State Variables
- `intents`: Mapping of intent ID to Intent struct
- `userIntents`: User's intent IDs
- `allowlistedDestinationChains`: Approved destination chains
- `activeIntentIds`: Currently active intents

### Events
- `IntentCreated`: New intent registered
- `IntentExecuted`: Intent successfully executed
- `CrossChainMessageSent`: Cross-chain transfer initiated

### Security Features
- Custom errors for gas efficiency
- Reentrancy protection planned for extensions
- Owner-only admin functions
- Input validation and modifiers

## 🏗️ Architecture

```
IntentFi.sol
├── Chainlink Price Feeds (ETH/USD)
├── Chainlink Automation (checkUpkeep/performUpkeep)
├── Intent Management (create/cancel/execute)
├── Multi-chain Allowlisting
└── Admin Functions
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd contracts

# Install dependencies
forge install

# Compile contracts
forge build

# Run tests
forge test
```

### Usage Example

```solidity
// Create an intent: Send 50 USDC when ETH > $3500
uint256 intentId = intentFi.createIntent(
    IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
    3500 * 1e8, // $3500 (8 decimals)
    50 * 1e6,   // 50 USDC (6 decimals)
    address(usdc),
    destinationChainSelector,
    receiverAddress
);
```

## 🌐 Deployment

Currently configured for:
- Sepolia Testnet
- Base Sepolia
- Optimism Sepolia
- Arbitrum Sepolia

Use the deployment script:
```bash
forge script script/DeployIntentFi.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast
```

## 🛠️ Development Status

### ✅ Completed
- Core intent logic
- Chainlink Price Feeds integration
- Chainlink Automation integration
- Comprehensive test suite
- Basic deployment scripts

### 🔄 In Progress
- CCIP cross-chain integration
- Advanced intent types (DCA, etc.)
- Frontend integration

### 📋 Roadmap
- Governance system
- Advanced trading strategies
- Mobile app integration
- Mainnet deployment

## 📝 License

MIT License - Built for ETH Global Cannes 2025

---

**Note**: This is the core IntentFi contract implementation. Additional features and contracts will be added in subsequent releases.

## Documentation

https://book.getfoundry.sh/

## Usage

### Build

```shell
$ forge build
```

### Test

```shell
$ forge test
```

### Format

```shell
$ forge fmt
```

### Gas Snapshots

```shell
$ forge snapshot
```

### Anvil

```shell
$ anvil
```

### Deploy

```shell
$ forge script script/Counter.s.sol:CounterScript --rpc-url <your_rpc_url> --private-key <your_private_key>
```

### Cast

```shell
$ cast <subcommand>
```

### Help

```shell
$ forge --help
$ anvil --help
$ cast --help
```
