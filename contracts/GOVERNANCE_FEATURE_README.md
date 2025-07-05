# IntentFi Governance Feature

## Overview

La fonctionnalité Governance d'IntentFi fournit un système de gouvernance décentralisé complet pour la gestion des paramètres du protocole, des mises à jour et des décisions communautaires. Le système est conçu avec des mécanismes de sécurité robustes, y compris des délais d'exécution, des seuils de quorum et des capacités d'urgence.

## Architecture

### Composants Principaux

1. **IntentFiGovernance.sol** - Contrat principal de gouvernance
2. **Système de Propositions** - Création et gestion des propositions
3. **Mécanisme de Vote** - Vote pondéré avec délégation
4. **Timelock** - Délai d'exécution pour la sécurité
5. **Multisig d'Urgence** - Actions d'urgence pour la protection du protocole

### Fonctionnalités Clés

#### 🗳️ Système de Gouvernance
- **Propositions** : Création de propositions avec seuil minimum de tokens
- **Vote Pondéré** : Pouvoir de vote basé sur la détention de tokens
- **Délégation** : Possibilité de déléguer son pouvoir de vote
- **Quorum** : Seuil de participation minimum pour valider les votes
- **Timelock** : Délai obligatoire avant l'exécution des propositions

#### 🚨 Sécurité et Urgence
- **Multisig d'Urgence** : Actions d'urgence par multisig
- **Pause d'Urgence** : Capacité de pause d'urgence du protocole
- **Annulation de Propositions** : Annulation par le proposant ou l'admin
- **Validation des Paramètres** : Validation automatique des paramètres

#### ⚙️ Gestion des Paramètres
- **Paramètres de Gouvernance** : Délais de vote, seuils, etc.
- **Paramètres du Protocole** : Frais, durées, limites
- **Mise à Jour Sécurisée** : Processus contrôlé de mise à jour

## Paramètres de Gouvernance

### Paramètres par Défaut

```solidity
GovernanceParams {
    votingDelay: 1 days,           // Délai avant début du vote
    votingPeriod: 3 days,          // Durée de la période de vote
    proposalThreshold: 100000e18,  // 100,000 tokens minimum pour proposer
    quorumThreshold: 400,          // 4% de participation minimum
    executionDelay: 2 days,        // Délai avant exécution
    minExecutionDelay: 1 days,     // Délai minimum d'exécution
    maxExecutionDelay: 7 days      // Délai maximum d'exécution
}
```

### Paramètres du Protocole

```solidity
ProtocolParams {
    maxIntentDuration: 365 days,      // Durée maximum des intents
    minIntentAmount: 1e6,             // Montant minimum (1 USDC)
    protocolFeeRate: 30,              // Taux de frais (0.3%)
    maxSlippageTolerance: 1000,       // Tolérance de slippage max (10%)
    emergencyPauseDuration: 7 days,   // Durée de pause d'urgence
    emergencyPauseEnabled: false      // Statut de pause d'urgence
}
```

## Utilisation

### 1. Création d'une Proposition

```solidity
function propose(
    string memory title,
    string memory description,
    address target,
    uint256 value,
    bytes memory callData
) external returns (uint256 proposalId)
```

**Exemple :**
```solidity
// Proposition pour changer le taux de frais
bytes memory callData = abi.encodeWithSignature(
    "_updateProtocolParams(tuple)",
    newProtocolParams
);

uint256 proposalId = governance.propose(
    "Réduire les frais du protocole",
    "Proposition pour réduire les frais de 0.3% à 0.25%",
    address(protocolContract),
    0,
    callData
);
```

### 2. Vote sur une Proposition

```solidity
function castVote(
    uint256 proposalId,
    bool support,      // true = pour, false = contre
    bool abstain       // true = abstention
) external
```

**Exemple :**
```solidity
// Voter pour la proposition
governance.castVote(proposalId, true, false);

// Voter contre
governance.castVote(proposalId, false, false);

// S'abstenir
governance.castVote(proposalId, false, true);
```

### 3. Délégation de Pouvoir de Vote

```solidity
function delegate(address delegatee) external
```

**Exemple :**
```solidity
// Déléguer son pouvoir de vote
governance.delegate(expertAddress);

// Récupérer son pouvoir de vote
governance.delegate(address(0));
```

### 4. Exécution d'une Proposition

```solidity
function executeProposal(uint256 proposalId) external
```

**Processus d'exécution :**
1. La proposition doit avoir passé le vote
2. Premier appel : initialise le timelock
3. Attendre le délai d'exécution
4. Deuxième appel : exécute la proposition

## Tests

### Structure des Tests

Le fichier `test/IntentFiGovernance.t.sol` contient des tests complets :

- ✅ **Déploiement** : Vérification des paramètres initiaux
- ✅ **Création de Propositions** : Tests des seuils et restrictions
- ✅ **Système de Vote** : Vote pour/contre/abstention
- ✅ **Restrictions de Vote** : Délais, double vote, etc.
- ✅ **Exécution** : Processus complet avec timelock
- ✅ **Délégation** : Mécanisme de délégation de votes
- ✅ **Urgence** : Fonctions d'urgence et multisig
- ✅ **Quorum** : Validation des seuils de participation

### Exécution des Tests

```bash
# Tests complets de la gouvernance
forge test --match-contract IntentFiGovernanceTest -v

# Tests spécifiques
forge test --match-test testProposalExecution -v
forge test --match-test testVoting -v
forge test --match-test testDelegation -v
```

## Déploiement

### Script de Déploiement

Le script `script/DeployIntentFiGovernance.s.sol` gère le déploiement :

#### Configuration des Réseaux

```bash
# Variables d'environnement requises
export PRIVATE_KEY="your_private_key"
export GOVERNANCE_TOKEN_ADDRESS="0x..." # Optionnel
export GOVERNANCE_OWNER="0x..."         # Optionnel
```

#### Déploiement Production

```bash
# Mainnet Ethereum
forge script script/DeployIntentFiGovernance.s.sol:DeployIntentFiGovernance \
    --rpc-url $MAINNET_RPC_URL \
    --broadcast \
    --verify \
    --etherscan-api-key $ETHERSCAN_API_KEY

# Polygon
forge script script/DeployIntentFiGovernance.s.sol:DeployIntentFiGovernance \
    --rpc-url $POLYGON_RPC_URL \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

#### Déploiement Test

```bash
# Déploiement avec token mock
forge script script/DeployIntentFiGovernance.s.sol:DeployIntentFiGovernance \
    --sig "deployForTesting()" \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast
```

### Vérification du Déploiement

```bash
# Vérification automatique
forge verify-contract <CONTRACT_ADDRESS> \
    src/IntentFiGovernance.sol:IntentFiGovernance \
    --chain-id <CHAIN_ID> \
    --constructor-args $(cast abi-encode "constructor(address,address,address[])" <GOVERNANCE_TOKEN> <OWNER> <MULTISIG_ARRAY>)
```

## Configuration Post-Déploiement

### 1. Configuration des Tokens de Gouvernance

```solidity
// Distribuer les tokens aux parties prenantes
governanceToken.transfer(daoTreasury, 1000000e18);
governanceToken.transfer(teamMultisig, 500000e18);
governanceToken.transfer(communityPool, 2000000e18);
```

### 2. Test du Multisig d'Urgence

```solidity
// Vérifier les adresses du multisig
require(governance.emergencyMultisig(multisig1), "Multisig 1 not set");
require(governance.emergencyMultisig(multisig2), "Multisig 2 not set");
require(governance.emergencyMultisig(multisig3), "Multisig 3 not set");
```

### 3. Première Proposition de Test

```solidity
// Créer une proposition simple pour tester le système
uint256 proposalId = governance.propose(
    "Première Proposition de Test",
    "Test du système de gouvernance",
    address(testContract),
    0,
    abi.encodeWithSignature("setValue(uint256)", 42)
);
```

## Sécurité

### Considérations de Sécurité

1. **Timelock Obligatoire** : Toutes les propositions ont un délai d'exécution
2. **Seuils de Quorum** : Protection contre les attaques de gouvernance
3. **Multisig d'Urgence** : Capacité d'intervention rapide
4. **Validation des Paramètres** : Contrôles automatiques des limites

### Bonnes Pratiques

1. **Révision des Propositions** : Examiner soigneusement avant vote
2. **Participation Active** : Encourager la participation de la communauté
3. **Délégation Responsable** : Déléguer à des participants actifs
4. **Monitoring** : Surveiller les propositions et votes

### Risques et Mitigations

| Risque | Mitigation |
|--------|------------|
| Attaque de gouvernance | Seuils de quorum et timelock |
| Centralisation des votes | Incitations à la délégation |
| Propositions malveillantes | Période de révision et annulation |
| Urgences non gérées | Multisig d'urgence dédié |

## Intégration avec l'Écosystème IntentFi

### Connexion avec les Autres Contrats

```solidity
// Configuration dans IntentFi principal
contract IntentFi {
    IntentFiGovernance public governance;
    
    modifier onlyGovernance() {
        require(msg.sender == address(governance), "Only governance");
        _;
    }
    
    function updateProtocolFee(uint256 newFee) external onlyGovernance {
        // Mise à jour via gouvernance uniquement
    }
}
```

### Paramètres Gouvernés

- **Frais du Protocole** : Ajustement des taux de commission
- **Limites des Intents** : Montants min/max, durées
- **Partenaires Autorisés** : Liste des intégrateurs approuvés
- **Paramètres de Sécurité** : Délais, seuils de validation

## Évolutions Futures

### Roadmap

1. **V1** : Gouvernance de base avec timelock ✅
2. **V2** : Gouvernance optimiste (en cours)
3. **V3** : Gouvernance multi-chaînes
4. **V4** : Gouvernance adaptative

### Améliorations Prévues

- **Vote Quadratique** : Réduction de l'influence des gros détenteurs
- **Gouvernance Optimiste** : Exécution plus rapide avec période de contestation
- **Cross-Chain Governance** : Votes et exécution multi-chaînes
- **Liquid Democracy** : Délégation flexible et révocable

## Support et Communauté

### Documentation
- [Whitepaper Gouvernance](./docs/governance-whitepaper.md)
- [Guide Utilisateur](./docs/user-guide.md)
- [API Reference](./docs/api-reference.md)

### Communauté
- Discord : [IntentFi Community](https://discord.gg/intentfi)
- Forum : [Governance Forum](https://forum.intentfi.com)
- GitHub : [Issues et Discussions](https://github.com/intentfi/governance)

---

**Note** : Cette fonctionnalité de gouvernance est conçue pour évoluer avec la communauté IntentFi et s'adapter aux besoins du protocole. La participation active de la communauté est essentielle pour le succès de la gouvernance décentralisée.
