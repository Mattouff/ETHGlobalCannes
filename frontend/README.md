# AI Agent Cross-Chain Asset Management - Mobile Frontend

## Overview

This React Native application provides a mobile interface for managing cross-chain assets with AI-powered trading recommendations. Built for ETHGlobal Hackathon, it integrates with Fetch.ai uAgents, Chainlink, and LayerZero technologies.

## Key Features

### 🤖 AI Agent Integration

- Real-time AI-generated trading intents
- Market data analysis and news monitoring
- Confidence-based recommendations
- Configurable auto-approval thresholds

### 💰 Portfolio Management

- Multi-chain asset overview
- Real-time portfolio values
- Cross-chain asset distribution
- Performance analytics

### 🔗 Cross-Chain Functionality

- Support for Ethereum, Polygon, Arbitrum, Optimism
- LayerZero-powered cross-chain transfers
- Bridge recommendations
- Gas optimization insights

### 📱 User Experience

- Intuitive wallet connection flow
- Intent approval/rejection interface
- Transaction history tracking
- Comprehensive settings management

## Architecture

### State Management

- **React Context API** for global app state
- **useReducer** for complex state transitions
- Separate contexts for wallet and app state

### Key Components

- **AppContext**: Manages intents, transactions, portfolio data
- **WalletContext**: Handles wallet connection and chain management
- **Screen Components**: Dashboard, Intents, Portfolio, Transactions, Settings

### Data Flow

1. AI agent monitors market conditions
2. Generates trading intents with confidence scores
3. User receives notifications for review
4. Approved intents execute via LayerZero
5. Real-time tracking of cross-chain transactions

## Technical Implementation

### Core Technologies

- **React Native** with TypeScript
- **Expo Router** for navigation
- **WalletConnect** for wallet integration
- **Wagmi/Viem** for Web3 interactions

### Mock Data & Simulation

The current implementation includes:

- Simulated AI agent behavior
- Mock portfolio data across multiple chains
- Fake transaction history
- Demo wallet connection flow

### File Structure

```
app/
├── (tabs)/
│   ├── index.tsx          # Dashboard screen
│   ├── intents.tsx        # AI intents management
│   ├── portfolio.tsx      # Portfolio overview
│   ├── transactions.tsx   # Transaction history
│   └── settings.tsx       # App settings
├── _layout.tsx            # Root layout with providers
└── +not-found.tsx         # 404 page

contexts/
├── AppContext.tsx         # Global app state
└── WalletContext.tsx      # Wallet management

components/                # Reusable UI components
```

## Getting Started

### Prerequisites

- Node.js 20+
- Expo CLI
- React Native development environment

### Installation

```bash
npm install
```

### Development

```bash
# Start development server
npm start

# iOS simulator
npm run ios

# Android emulator
npm run android

# Web browser
npm run web
```
