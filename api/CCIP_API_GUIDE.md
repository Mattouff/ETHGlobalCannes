# IntentFi API CCIP - Guide d'utilisation

## Vue d'ensemble

L'API IntentFi avec intégration CCIP permet de gérer des intents financiers cross-chain en utilisant Chainlink CCIP pour les transferts entre différentes blockchains.

## Installation

```bash
cd api/
pip install -r requirements.txt
python app.py
```

L'API sera disponible sur `http://localhost:5001`

## Endpoints CCIP

### 1. Chaînes supportées

```bash
GET /ccip/chains
```

Retourne la liste des chaînes supportées pour CCIP.

### 2. Calculer les frais CCIP

```bash
POST /ccip/fees/ethereum_sepolia/base_sepolia
Content-Type: application/json

{
  "amount": 0.1,
  "token_address": null,
  "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630"
}
```

### 3. Initier un transfert CCIP

```bash
POST /ccip/transfer
Content-Type: application/json

{
  "source_chain": "ethereum_sepolia",
  "destination_chain": "base_sepolia",
  "amount": 0.1,
  "token_address": null,
  "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630",
  "sender": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
}
```

### 4. Vérifier le statut d'un transfert

```bash
GET /ccip/status/{transaction_id}
```

### 5. Historique des transferts

```bash
GET /ccip/history/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

## Endpoints Intents

### 1. Créer un intent

```bash
POST /intent/create
Content-Type: application/json

{
  "owner": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "intent_type": "SEND_IF_PRICE_ABOVE",
  "trigger_price": 3500,
  "amount": 0.1,
  "token_address": null,
  "source_chain": "ethereum_sepolia",
  "destination_chain": "base_sepolia",
  "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630"
}
```

Types d'intents supportés :
- `SEND_IF_PRICE_ABOVE` : Envoyer si le prix ETH est au-dessus du seuil
- `SEND_IF_PRICE_BELOW` : Envoyer si le prix ETH est en-dessous du seuil
- `CROSS_CHAIN_SWAP` : Swap cross-chain automatique
- `AUTOMATED_DCA` : Dollar Cost Averaging automatisé

### 2. Vérifier le statut d'un intent

```bash
GET /intent/status/{intent_id}
```

### 3. Exécuter un intent

```bash
POST /intent/execute/{intent_id}
```

### 4. Lister les intents d'un utilisateur

```bash
GET /intent/list/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

### 5. Annuler un intent

```bash
POST /intent/cancel/{intent_id}
```

## Endpoints de monitoring

### 1. Statistiques CCIP

```bash
GET /ccip/analytics
```

### 2. Statistiques des intents

```bash
GET /intent/analytics
```

### 3. Santé du système

```bash
GET /ccip/health
```

### 4. Tokens supportés par chaîne

```bash
GET /ccip/supported-tokens/ethereum_sepolia
```

### 5. Estimation du temps de transfert

```bash
GET /ccip/estimate-time/ethereum_sepolia/base_sepolia
```

## Exemple d'usage complet

### Scénario : Transfert automatique si ETH > $3500

1. **Créer l'intent** :
```bash
curl -X POST http://localhost:5001/intent/create \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "intent_type": "SEND_IF_PRICE_ABOVE",
    "trigger_price": 3500,
    "amount": 0.1,
    "source_chain": "ethereum_sepolia",
    "destination_chain": "base_sepolia",
    "receiver": "0x742d35Cc6639C17FcD8c9DE5c2a3d94b2fC30630"
  }'
```

2. **Monitorer l'intent** :
```bash
curl http://localhost:5001/intent/status/{intent_id}
```

3. **Vérifier l'exécution CCIP** (si déclenché) :
```bash
curl http://localhost:5001/ccip/status/{ccip_tx_id}
```

## Intégration avec les smart contracts

### Configuration des contrats

L'API est conçue pour interagir avec les contrats IntentFi déployés :

- **IntentFi.sol** : Contrat principal pour les intents
- **IntentFiCCIP.sol** : Extension CCIP pour les transferts cross-chain

### Adresses des contrats (à configurer)

```python
INTENTFI_CONTRACTS = {
    "ethereum_sepolia": {
        "intentfi": "0x...",  # Adresse à remplacer
        "intentfi_ccip": "0x..."  # Adresse à remplacer
    },
    "base_sepolia": {
        "intentfi": "0x...",
        "intentfi_ccip": "0x..."
    }
}
```

## Configuration CCIP

### Chaînes supportées

- **Ethereum Sepolia** : Chain ID 11155111
- **Base Sepolia** : Chain ID 84532

### Routers CCIP

- **Ethereum Sepolia** : `0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59`
- **Base Sepolia** : `0xD3b06cEbF099CE7DA4AcCf578aaebFDBd6e88a93`

### Tokens LINK

- **Ethereum Sepolia** : `0x779877A7B0D9E8603169DdbD7836e478b4624789`
- **Base Sepolia** : `0xE4aB69C077896252FAFBD49EFD26B5D171A32410`

## Sécurité

⚠️ **Important** : Cette API est conçue pour les testnets. Pour la production :

1. Implémenter l'authentification et l'autorisation
2. Utiliser des clés privées sécurisées
3. Ajouter la validation des signatures
4. Implémenter la limitation de taux (rate limiting)
5. Utiliser HTTPS
6. Auditer les smart contracts

## Support

Pour plus d'informations, consultez :
- [Documentation Chainlink CCIP](https://docs.chain.link/ccip)
- [Contrats IntentFi](/contracts/README.md)
- [Guide de déploiement](/contracts/CCIP_README.md)
