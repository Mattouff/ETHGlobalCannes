# IntentFi Smart Contract

## Vue d'ensemble

IntentFi est un système de planification autonome pour les intents financiers développé pour ETHGlobal Cannes 2025. Le projet intègre trois technologies clés :

- **🔗 Chainlink** : Price Feeds temps réel (ETH/USD) et exécution automatisée via Chainlink Automation
- **🌐 CCIP Cross-Chain** : Exécution cross-chain des intents avec capacité de transfert vers d'autres chaînes  
- **🤖 ASI Agent** : Recommandations d'intents basées sur l'analyse de sentiment et les données de marché

## Architecture des Contrats

### 1. IntentFi.sol (Contrat Principal)
- Gestion des intents financiers
- Intégration Chainlink Automation pour l'exécution automatique
- Price Feeds pour les déclencheurs de prix
- Système de permissions et de sécurité

### 2. IntentFiCCIP.sol (Extension CCIP)
- Extension avec fonctionnalités CCIP complètes
- Gestion des tokens cross-chain
- Paiement des frais avec LINK
- Support multi-chaînes

### 3. IntentFiUsageExample.sol (Exemples d'utilisation)
- Interface simplifiée pour l'application React Native
- Intégration avec les recommandations de l'agent ASI
- Fonctions utilitaires pour l'UX

## Configuration des Variables d'Environnement

Créez un fichier `.env` dans le répertoire `contracts/` :

```env
# Clés privées
PRIVATE_KEY=your_private_key_here

# RPC URLs
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your-api-key
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/your-api-key
OPTIMISM_SEPOLIA_RPC_URL=https://opt-sepolia.g.alchemy.com/v2/your-api-key
ARBITRUM_SEPOLIA_RPC_URL=https://arb-sepolia.g.alchemy.com/v2/your-api-key

# Etherscan API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key
BASESCAN_API_KEY=your_basescan_api_key
OPTIMISM_ETHERSCAN_API_KEY=your_optimism_etherscan_api_key
ARBISCAN_API_KEY=your_arbiscan_api_key
```

## Adresses des Contrats Chainlink

### Sepolia Testnet
- CCIP Router: `0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59`
- LINK Token: `0x779877A7B0D9E8603169DdbD7836e478b4624789`
- ETH/USD Price Feed: `0x694AA1769357215DE4FAC081bf1f309aDC325306`
- Chain Selector: `16015286601757825753`

### Base Sepolia Testnet
- CCIP Router: `0xd3b06CEBF099Ce7Da4acCf578AAEfd5f4e89C8bA`
- LINK Token: `0xE4aB69C077896252FAFBD49EFD26B5D171A32410`
- ETH/USD Price Feed: `0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1`
- Chain Selector: `10344971235874465080`

### Optimism Sepolia Testnet
- CCIP Router: `0x114A20A10b43D4115e5aeef7345a1A71d2a60C57`
- LINK Token: `0xE4aB69C077896252FAFBD49EFD26B5D171A32410`
- ETH/USD Price Feed: `0x61Ec26aA57019C486B10502285c5A3D4A4750AD7`
- Chain Selector: `5224473277236331295`

### Arbitrum Sepolia Testnet
- CCIP Router: `0x2a9C5afB0d0e4BAb2BCdaE109EC4b0c4Be15a165`
- LINK Token: `0xb1D4538B4571d411F07960EF2838Ce337FE1E80E`
- ETH/USD Price Feed: `0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165`
- Chain Selector: `3478487238524512106`

## Installation et Compilation

```bash
# Installation des dépendances
forge install

# Compilation des contrats
forge build

# Exécution des tests
forge test -vvv
```

## Déploiement

### Déploiement sur Sepolia
```bash
forge script script/DeployIntentFi.s.sol --rpc-url sepolia --broadcast --verify
```

### Déploiement sur Base Sepolia
```bash
forge script script/DeployIntentFi.s.sol --rpc-url base_sepolia --broadcast --verify
```

### Déploiement sur Optimism Sepolia
```bash
forge script script/DeployIntentFi.s.sol --rpc-url optimism_sepolia --broadcast --verify
```

### Déploiement sur Arbitrum Sepolia
```bash
forge script script/DeployIntentFi.s.sol --rpc-url arbitrum_sepolia --broadcast --verify
```

## Types d'Intents Supportés

### 1. SEND_IF_PRICE_ABOVE
Envoie des fonds quand le prix dépasse un seuil :
```solidity
// Exemple : Envoyer 50 USDC vers Optimism si ETH > $3500
createIntent(
    IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
    3500 * 1e8, // $3500 avec 8 décimales
    50e6,       // 50 USDC avec 6 décimales
    usdcAddress,
    optimismChainSelector,
    receiverAddress
);
```

### 2. SEND_IF_PRICE_BELOW
Envoie des fonds quand le prix descend sous un seuil :
```solidity
// Exemple : Envoyer 1 ETH vers Base si ETH < $2500
createIntent{value: 1 ether}(
    IntentFi.IntentType.SEND_IF_PRICE_BELOW,
    2500 * 1e8, // $2500 avec 8 décimales
    1 ether,
    address(0), // ETH natif
    baseChainSelector,
    receiverAddress
);
```

### 3. CROSS_CHAIN_SWAP (À venir)
Swap automatique cross-chain basé sur les conditions de marché.

### 4. AUTOMATED_DCA (À venir)
Dollar Cost Averaging automatisé cross-chain.

## Intégration avec l'Interface React Native

### Événements à écouter
```javascript
// Écouter la création d'intents
contract.on("IntentCreated", (intentId, owner, intentType, triggerPrice, amount, destinationChain, receiver) => {
    console.log(`Nouvel intent créé: ${intentId}`);
    // Mettre à jour l'UI
});

// Écouter l'exécution d'intents
contract.on("IntentExecuted", (intentId, destinationChain, receiver, amount) => {
    console.log(`Intent ${intentId} exécuté avec succès`);
    // Notifier l'utilisateur
});

// Écouter les messages cross-chain
contract.on("CrossChainMessageSent", (intentId, destinationChain, receiver, amount) => {
    console.log(`Message cross-chain envoyé pour l'intent ${intentId}`);
});
```

### Fonctions utiles pour l'app mobile
```javascript
// Obtenir les intents d'un utilisateur
const getUserIntents = async (userAddress) => {
    return await contract.getUserIntents(userAddress);
};

// Vérifier le prix actuel
const getCurrentPrice = async () => {
    const price = await contract.getCurrentPrice();
    return Number(price) / 1e8; // Convertir en USD
};

// Créer un intent simple
const createSimpleIntent = async (triggerPriceUSD, amountUSDC, isAbove, destinationChain, receiver) => {
    return await usageContract.createSimpleIntent(
        triggerPriceUSD * 100, // Convertir en format 2 décimales
        amountUSDC * 1e6,      // Convertir en format 6 décimales
        isAbove,
        destinationChain,
        receiver,
        usdcAddress,
        description
    );
};
```

## Intégration avec l'Agent ASI

### Structure de Recommandation
```solidity
struct AIRecommendation {
    IntentFi.IntentType intentType;
    int256 triggerPrice;
    uint256 amount;
    address tokenAddress;
    uint64 destinationChain;
    address receiver;
    uint256 confidence;     // 0-100
    string marketReason;    // Analyse de l'IA
}
```

### Exemple d'utilisation avec l'agent ASI
```javascript
// L'agent ASI analyse le marché et retourne une recommandation
const aiRecommendation = await fetchAIRecommendation(userProfile, marketData);

// L'utilisateur valide via l'interface mobile
if (userApproves(aiRecommendation)) {
    await usageContract.createAIRecommendedIntent(
        aiRecommendation,
        "Recommandation basée sur l'analyse de sentiment positif du marché"
    );
}
```

## Chainlink Automation

Le contrat utilise Chainlink Automation pour :

1. **checkUpkeep()** : Vérifie automatiquement les conditions d'exécution
2. **performUpkeep()** : Exécute les intents quand les conditions sont remplies
3. **Price Feeds** : Surveillance continue des prix ETH/USD

### Configuration Automation
1. Déployez le contrat IntentFi
2. Enregistrez-le sur [Chainlink Automation](https://automation.chain.link/)
3. Financez avec LINK pour les frais d'automation
4. Les intents seront exécutés automatiquement

## Intégration CCIP Cross-Chain

### Fonctionnalités CCIP
- **ccipSend()** : Envoi de messages et tokens cross-chain
- **Réception de messages** : Via CCIPReceiver
- **Gestion des frais** : Paiement automatique avec LINK
- **Support multi-tokens** : ETH natif et tokens ERC20

### Exemple d'envoi cross-chain
```solidity
// L'intent se déclenche automatiquement et envoie via CCIP
Intent memory intent = Intent({
    // ... configuration de l'intent
    destinationChainSelector: baseSepoliaChainSelector,
    destinationReceiver: userWalletOnBase,
    amount: 50e6, // 50 USDC
    tokenAddress: usdcAddress
});
```

## Sécurité et Permissions

### Contrôles d'accès
- **onlyOwner** : Fonctions administratives
- **Allowlisting** : Chaînes et tokens autorisés
- **Validation des intents** : Vérifications de solde et d'approbation

### Gestion des fonds
- **Verrouillage sécurisé** : Fonds verrouillés lors de la création d'intent
- **Remboursement automatique** : En cas d'annulation d'intent
- **Gestion des erreurs** : Erreurs personnalisées pour un debugging facile

## Tests et Validation

Le projet inclut des tests complets :

```bash
# Tests unitaires
forge test -vvv

# Tests spécifiques
forge test --match-test testCreateIntentWithUSDC -vvv

# Tests de gas
forge test --gas-report
```

### Couverture des tests
- ✅ Création d'intents avec ETH et tokens
- ✅ Vérification des conditions d'exécution
- ✅ Chainlink Automation (checkUpkeep/performUpkeep)
- ✅ Annulation d'intents et remboursements
- ✅ Contrôles d'accès et permissions
- ✅ Gestion des erreurs

## Déploiement en Production

### Étapes recommandées
1. **Tests approfondis** sur testnets
2. **Audit de sécurité** (recommandé pour la production)
3. **Déploiement mainnet** avec configuration appropriée
4. **Enregistrement Chainlink Automation**
5. **Configuration CCIP** sur toutes les chaînes cibles

### Monitoring
- Surveillance des intents actifs
- Monitoring des prix et déclencheurs
- Alertes pour les échecs d'exécution
- Tracking des frais CCIP et Automation

## Support et Documentation

- **Documentation Chainlink** : [docs.chain.link](https://docs.chain.link/)
- **CCIP Documentation** : [docs.chain.link/ccip](https://docs.chain.link/ccip)
- **Foundry Book** : [book.getfoundry.sh](https://book.getfoundry.sh/)

## Roadmap

### Phase 1 (Actuelle) ✅
- Contrat IntentFi de base
- Intégration Chainlink Price Feeds
- Chainlink Automation
- Tests complets

### Phase 2 (Prochaine)
- Intégration CCIP complète avec vraies librairies
- Support multi-tokens avancé
- Optimisations de gas

### Phase 3 (Future)
- Intents DCA automatisés
- Intégration DEX pour swaps cross-chain
- Interface graphique avancée

Cette implémentation fournit une base solide pour votre projet IntentFi avec toutes les intégrations Chainlink nécessaires pour ETHGlobal Cannes 2025 !
