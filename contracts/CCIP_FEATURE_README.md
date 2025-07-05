# IntentFi CCIP - Cross-Chain Intent Execution

## 🌉 Overview

IntentFiCCIP extends the core IntentFi contract with Chainlink CCIP (Cross-Chain Interoperability Protocol) integration, enabling seamless cross-chain intent execution across multiple EVM networks.

## 🔗 Key Features

### Cross-Chain Capabilities
- **Multi-Chain Support**: Execute intents across Ethereum, Base, Arbitrum, Optimism
- **CCIP Integration**: Secure cross-chain messaging via Chainlink CCIP
- **LINK Token Management**: Built-in LINK funding and fee management
- **Destination Chain Allowlisting**: Admin-controlled supported chains

### Enhanced Intent Types
- All core IntentFi functionality
- Cross-chain token transfers (ERC20 + Native)
- Cross-chain message passing
- Automated fee calculation and payment

## 🏗️ Architecture

```
IntentFiCCIP.sol
├── Inherits: IntentFi.sol (core functionality)
├── CCIP Router Integration
├── LINK Token Management
├── Cross-Chain Message Handling
└── Fee Calculation & Payment
```

## 🚀 Quick Start

### Installation & Setup

```bash
# Compile contracts
forge build

# Run CCIP-specific tests
forge test --match-contract IntentFiCCIPTest

# Deploy to a specific network
forge script script/DeployIntentFiCCIP.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast
```

### Cross-Chain Intent Example

```solidity
// Create cross-chain intent: Send 50 USDC from Ethereum to Base when ETH > $3500
uint256 intentId = intentFiCCIP.createIntent(
    IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
    3500 * 1e8, // $3500 trigger
    50 * 1e6,   // 50 USDC
    address(usdc),
    10344971235874465080, // Base Sepolia chain selector
    receiverAddress
);
```

### LINK Token Management

```solidity
// Fund contract with LINK for CCIP fees
mockLINK.approve(address(intentFiCCIP), 10e18);
intentFiCCIP.fundLINK(10e18);

// Check LINK balance
uint256 linkBalance = intentFiCCIP.getLINKBalance();

// Withdraw LINK (owner only)
intentFiCCIP.withdrawLINK(ownerAddress, 5e18);
```

## 🌐 Supported Networks

### Testnets (Configured)
| Network | Chain ID | CCIP Chain Selector | Status |
|---------|----------|-------------------|---------|
| Sepolia | 11155111 | 16015286601757825753 | ✅ Ready |
| Base Sepolia | 84532 | 10344971235874465080 | ✅ Ready |
| Arbitrum Sepolia | 421614 | 3478487238524512106 | ✅ Ready |
| Optimism Sepolia | 11155420 | 5224473277236331295 | ✅ Ready |

### Contract Addresses
Each network has pre-configured:
- Chainlink Price Feeds (ETH/USD)
- CCIP Router addresses
- LINK token addresses

## 🧪 Testing

### Test Coverage
- LINK token funding and withdrawal
- Cross-chain intent creation
- CCIP message simulation
- Fee calculation
- Multi-chain deployment
- Error conditions and access controls

```bash
# Run all CCIP tests
forge test --match-contract IntentFiCCIPTest -v

# Run specific test
forge test --match-test testCrossChainIntentExecution -vvv
```

## 📊 Contract Details

### New State Variables
- `ccipRouter`: CCIP router contract address
- `linkToken`: LINK token for paying CCIP fees
- Enhanced intent execution with cross-chain messaging

### New Functions
- `fundLINK(uint256 amount)`: Fund contract with LINK tokens
- `withdrawLINK(address to, uint256 amount)`: Withdraw LINK (owner only)
- `getLINKBalance()`: Get contract's LINK balance
- `getCCIPRouter()`: Get CCIP router address
- `getLINKToken()`: Get LINK token address
- `calculateCCIPFees(Intent memory intent)`: Calculate cross-chain fees

### Events
- `CCIPMessageSent`: Cross-chain message sent
- `LINKFunded`: LINK tokens funded to contract
- `LINKWithdrawn`: LINK tokens withdrawn

## 🔧 Deployment

### Single Chain Deployment

```bash
# Deploy to Sepolia
forge script script/DeployIntentFiCCIP.s.sol \
  --rpc-url $SEPOLIA_RPC_URL \
  --broadcast \
  --verify

# Deploy to Base Sepolia
forge script script/DeployIntentFiCCIP.s.sol \
  --rpc-url $BASE_SEPOLIA_RPC_URL \
  --broadcast \
  --verify
```

### Multi-Chain Deployment

```bash
# Deploy to all supported testnets
forge script script/DeployIntentFiCCIP.s.sol:DeployIntentFiCCIP \
  --sig "deployMultiChain()" \
  --rpc-url $SEPOLIA_RPC_URL \
  --broadcast
```

## 🔐 Security Features

### Access Controls
- Owner-only LINK withdrawal
- Chain allowlisting system
- Input validation for all functions

### CCIP Security
- Secure cross-chain messaging
- Automatic fee calculation
- Revert protection for failed transfers

### Error Handling
- Custom errors for gas efficiency
- Comprehensive input validation
- Safe token transfers

## 🛠️ Development Status

### ✅ Completed
- CCIP router integration
- LINK token management
- Cross-chain intent execution
- Comprehensive test suite
- Multi-chain deployment scripts
- Documentation and examples

### 🔄 Next Steps
- Advanced CCIP features integration
- Real CCIP router testing on testnets
- Gas optimization for cross-chain calls
- Integration with IntentFiAdvanced

## 📝 Technical Notes

### CCIP Integration
- Currently uses placeholder CCIP implementation
- Ready for real CCIP router integration
- Includes fee calculation and management
- Supports both token and native transfers

### Gas Optimization
- Efficient cross-chain message packing
- Optimized LINK token management
- Minimal additional gas overhead

### Compatibility
- Fully backward compatible with IntentFi
- Can be extended by IntentFiAdvanced
- Modular architecture for easy updates

---

**Built for ETH Global Cannes 2025 - Cross-Chain DeFi Innovation** 🌉
