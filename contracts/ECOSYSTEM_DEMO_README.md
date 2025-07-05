# IntentFi Ecosystem Demo & Integration Tools

## Overview

Cette branche contient les outils d'écosystème, de démonstration et d'intégration pour IntentFi. Elle regroupe tous les scripts et contrats nécessaires pour déployer l'écosystème complet et démontrer ses capacités lors d'ETHGlobal Cannes 2025.

## Contenu de la Branche

### 📦 **Contrats d'Intégration**

#### **src/IntentFiUsageExample.sol**
Contrat d'exemple montrant comment intégrer IntentFi dans vos applications.

**Fonctionnalités :**
- ✅ **Interface Simplifiée** : Création d'intents avec paramètres user-friendly
- ✅ **Intégration IA** : Support pour les recommandations d'ASI agents
- ✅ **Events Frontend** : Events optimisés pour React Native
- ✅ **Helpers Utilitaires** : Fonctions d'estimation et de monitoring
- ✅ **Market Data** : Données de marché pour les applications

**Usage avec React Native :**
```solidity
// Création d'intent simplifié
usageExample.createSimpleIntent(
    350000,           // $3500.00 (avec 2 décimales)
    100000000,        // 100 USDC (avec 6 décimales)  
    true,             // Trigger si prix au-dessus
    chainSelector,    // Chaîne de destination
    userAddress,      // Adresse de réception
    usdcAddress,      // Token USDC
    "Sell ETH if >$3500" // Description
);
```

### 🚀 **Scripts de Déploiement**

#### **script/DeployIntentFiEcosystem.s.sol**
Script de déploiement orchestré pour l'écosystème complet IntentFi.

**Déploie en une fois :**
- 🏗️ **IntentFi** (contrat de base)
- 🌐 **IntentFiCCIP** (cross-chain)
- 🚀 **IntentFiAdvanced** (stratégies avancées)
- 🏛️ **IntentFiGovernance** (gouvernance)
- 📱 **IntentFiUsageExample** (intégration)

**Configuration Multi-Chaînes :**
- Ethereum Mainnet & Sepolia
- Polygon Mainnet & Mumbai
- Base Mainnet & Sepolia
- Arbitrum One & Sepolia
- Optimism Mainnet & Sepolia

**Usage :**
```bash
# Déploiement production
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $MAINNET_RPC_URL \
    --broadcast \
    --verify

# Déploiement testnet
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

### 🎮 **Scripts de Démonstration**

#### **script/EndToEndDemo.s.sol**
Démonstration complète end-to-end des fonctionnalités IntentFi.

**Scénarios Démontrés :**
- ✅ **Intents Basiques** : Création et exécution d'intents simples
- ✅ **DCA (Dollar Cost Averaging)** : Investissement périodique automatisé
- ✅ **Range Trading** : Trading automatique dans une fourchette de prix
- ✅ **Gouvernance** : Propositions, votes et exécution
- ✅ **Cross-Chain** : Vérification des capacités multi-chaînes
- ✅ **Stress Test** : Test de charge avec multiples intents

**Usage pour ETHGlobal :**
```bash
# Demo complète (parfait pour présentation)
forge script script/EndToEndDemo.s.sol:EndToEndDemo \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast

# Stress test
forge script script/EndToEndDemo.s.sol:EndToEndDemo \
    --sig "stressTest()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

#### **script/InteractIntentFi.s.sol**
Script d'interaction avec les contrats IntentFi déployés.

**Fonctionnalités :**
- ✅ **Création d'Intents** : Interface CLI pour créer des intents
- ✅ **Monitoring** : Vérification du statut des intents
- ✅ **Administration** : Fonctions d'administration et maintenance
- ✅ **Cross-Chain Setup** : Configuration des chaînes supportées

**Usage :**
```bash
# Créer un intent
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "createIntent()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast

# Monitoring
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "monitorIntents()" \
    --rpc-url $SEPOLIA_RPC_URL
```

## Configuration et Usage

### **Variables d'Environnement Requises**

```bash
# Clés privées
export PRIVATE_KEY="0x..."

# URLs RPC
export MAINNET_RPC_URL="https://..."
export SEPOLIA_RPC_URL="https://..."
export POLYGON_RPC_URL="https://..."
export BASE_RPC_URL="https://..."
export ARBITRUM_RPC_URL="https://..."
export OPTIMISM_RPC_URL="https://..."

# API Keys pour vérification
export ETHERSCAN_API_KEY="..."
export POLYGONSCAN_API_KEY="..."
export BASESCAN_API_KEY="..."
export ARBISCAN_API_KEY="..."
export OPTIMISTIC_ETHERSCAN_API_KEY="..."

# Adresses de contrats (après déploiement)
export INTENTFI_CONTRACT_ADDRESS="0x..."
export INTENTFI_ADVANCED_ADDRESS="0x..."
export INTENTFI_GOVERNANCE_ADDRESS="0x..."
export USDC_ADDRESS="0x..."
export GOVERNANCE_TOKEN_ADDRESS="0x..."
```

### **Déploiement Complet pour ETHGlobal**

#### **1. Déploiement sur Sepolia**
```bash
# 1. Déployer l'écosystème complet
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast \
    --verify \
    --etherscan-api-key $ETHERSCAN_API_KEY

# 2. Sauvegarder les adresses dans .env
# (Le script génère automatiquement un fichier .env)

# 3. Lancer la démonstration
forge script script/EndToEndDemo.s.sol:EndToEndDemo \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

#### **2. Déploiement Multi-Chaînes**
```bash
# Base Sepolia
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --broadcast

# Arbitrum Sepolia  
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $ARBITRUM_SEPOLIA_RPC_URL \
    --broadcast

# Optimism Sepolia
forge script script/DeployIntentFiEcosystem.s.sol:DeployIntentFiEcosystem \
    --rpc-url $OPTIMISM_SEPOLIA_RPC_URL \
    --broadcast
```

## Intégration avec React Native

### **Configuration du Frontend**

```typescript
// contracts.ts
export const INTENTFI_CONTRACTS = {
  USAGE_EXAMPLE: "0x...", // Adresse d'IntentFiUsageExample
  INTENTFI_ADVANCED: "0x...", // Adresse d'IntentFiAdvanced
  GOVERNANCE: "0x...", // Adresse d'IntentFiGovernance
};

// ABI pour IntentFiUsageExample
export const USAGE_EXAMPLE_ABI = [
  "function createSimpleIntent(uint256,uint256,bool,uint64,address,address,string) returns (uint256)",
  "function getUserIntentsWithDetails(address) view returns (tuple[])",
  "function getUserReadyIntents(address) view returns (uint256[])",
  "function getMarketSummary() view returns (tuple)",
  "function estimateIntentExecution(int256,bool) view returns (uint256,uint256)"
];
```

### **Exemples d'Usage**

```typescript
// Créer un intent simple
const createIntent = async () => {
  const intentId = await usageExample.createSimpleIntent(
    350000,           // $3500.00
    100000000,        // 100 USDC
    true,             // Si prix au-dessus
    chainSelector,    // Chaîne destination  
    userAddress,      // Adresse réception
    usdcAddress,      // Token USDC
    "Sell ETH if >$3500"  // Description
  );
};

// Obtenir les intents de l'utilisateur
const getUserIntents = async () => {
  const intents = await usageExample.getUserIntentsWithDetails(userAddress);
  return intents;
};

// Vérifier les intents prêts
const checkReadyIntents = async () => {
  const readyIntents = await usageExample.getUserReadyIntents(userAddress);
  return readyIntents;
};

// Obtenir les données de marché
const getMarketData = async () => {
  const marketData = await usageExample.getMarketSummary();
  return {
    ethPrice: marketData.currentETHPriceUSD,
    activeIntents: marketData.totalActiveIntents,
    lastUpdated: marketData.lastUpdated
  };
};
```

## Tests et Validation

### **Tests d'Intégration**

```bash
# Test de l'écosystème complet
forge test --match-contract IntentFi -v

# Test des contrats individuels
forge test --match-contract IntentFiTest -v
forge test --match-contract IntentFiCCIPTest -v
forge test --match-contract IntentFiAdvancedTest -v
forge test --match-contract IntentFiGovernanceTest -v
```

### **Validation de Déploiement**

```bash
# Vérifier que tous les contrats sont déployés
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "validateDeployment()" \
    --rpc-url $SEPOLIA_RPC_URL

# Test de performance
forge script script/EndToEndDemo.s.sol:EndToEndDemo \
    --sig "stressTest()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

## Monitoring et Maintenance

### **Surveillance des Intents**

```bash
# Surveiller les intents actifs
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "monitorIntents()" \
    --rpc-url $SEPOLIA_RPC_URL

# Vérifier les exécutions automatiques
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "checkAutomationStatus()" \
    --rpc-url $SEPOLIA_RPC_URL
```

### **Administration**

```bash
# Mise à jour des paramètres
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "updateProtocolParameters()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast

# Gestion des chaînes supportées
forge script script/InteractIntentFi.s.sol:InteractIntentFi \
    --sig "manageSupportedChains()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

## Démonstration ETHGlobal

### **Scénario de Présentation**

1. **Setup** (2 min)
   - Déploiement rapide sur Sepolia
   - Vérification des contrats

2. **Demo Basique** (3 min)
   - Création d'intent simple
   - Monitoring en temps réel
   - Exécution automatique

3. **Fonctionnalités Avancées** (3 min)
   - DCA automatisé
   - Range trading
   - Cross-chain

4. **Gouvernance** (2 min)
   - Proposition communautaire
   - Vote et exécution

### **Commands de Demo**

```bash
# Setup rapide
./scripts/quick-setup.sh

# Demo complète
forge script script/EndToEndDemo.s.sol:EndToEndDemo \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast

# Monitoring live
./scripts/live-monitor.sh
```

## Ressources et Support

### **Documentation**
- [Architecture Overview](../ECOSYSTEM_README.md)
- [Smart Contracts Docs](../docs/)
- [API Reference](../docs/api-reference.md)

### **Communauté**
- Discord: [IntentFi Community](https://discord.gg/intentfi)
- GitHub: [Issues & Discussions](https://github.com/intentfi)
- Telegram: [Dev Channel](https://t.me/intentfi-dev)

### **Contact ETHGlobal**
- Team: IntentFi
- Track: DeFi + Cross-Chain
- Demo: [Live Demo Link](https://intentfi-demo.vercel.app)

---

**Ready for ETHGlobal Cannes 2025! 🚀**

Cette branche contient tout le nécessaire pour une démonstration complète et impressionnante de l'écosystème IntentFi.
