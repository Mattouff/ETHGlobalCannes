# IntentFi CCIP API - Documentation Complète

## 🚀 Vue d'ensemble

Cette API Flask fournit une interface complète pour :
- **Récupération de tokens multi-chaînes** (Ethereum, Base, Flow)
- **Transferts cross-chain via CCIP** (Chainlink Cross-Chain Interoperability Protocol)
- **Intents financiers automatisés** avec déclencheurs de prix
- **Monitoring et analytics en temps réel**

## 📋 Configuration

### Variables d'environnement
```bash
ALCHEMY_API_KEY="dDOVAvCmh3rX60qNaCjbs"
FLASK_ENV=development
FLASK_DEBUG=True
```

### Dépendances
```bash
pip install flask requests
```

### Lancement de l'API
```bash
python app.py
# API disponible sur http://localhost:5001
```

## 🔗 Endpoints Principaux

### 1. Token Balances

#### GET /tokens/ethereum/{address}
Récupère les tokens sur Ethereum Sepolia testnet
```bash
curl http://localhost:5001/tokens/ethereum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

#### GET /tokens/base/{address}
Récupère les tokens sur Base Sepolia testnet
```bash
curl http://localhost:5001/tokens/base/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

#### GET /tokens/all/{address}
Récupère les tokens de toutes les chaînes supportées
```bash
curl http://localhost:5001/tokens/all/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

### 2. CCIP (Cross-Chain)

#### GET /ccip/chains
Liste des chaînes supportées pour CCIP
```bash
curl http://localhost:5001/ccip/chains
```

#### POST /ccip/fees/{source_chain}/{dest_chain}
Calcule les frais pour un transfert CCIP
```bash
curl -X POST http://localhost:5001/ccip/fees/ethereum_sepolia/base_sepolia \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.1,
    "token_address": null,
    "receiver": "0x604bbc860e08198086F682355842522F7b099007"
  }'
```

#### POST /ccip/transfer
Initie un transfert cross-chain
```bash
curl -X POST http://localhost:5001/ccip/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "source_chain": "ethereum_sepolia",
    "destination_chain": "base_sepolia",
    "amount": 0.1,
    "token_address": null,
    "receiver": "0x604bbc860e08198086F682355842522F7b099007",
    "sender": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
  }'
```

#### GET /ccip/status/{tx_id}
Vérifie le statut d'un transfert CCIP
```bash
curl http://localhost:5001/ccip/status/ccip_1234567890_1234
```

### 3. Intents Financiers

#### POST /intent/create
Crée un intent financier automatisé
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
    "receiver": "0x604bbc860e08198086F682355842522F7b099007"
  }'
```

#### GET /intent/status/{intent_id}
Vérifie le statut d'un intent
```bash
curl http://localhost:5001/intent/status/intent_1234567890_1234
```

#### POST /intent/execute/{intent_id}
Exécute un intent manuellement
```bash
curl -X POST http://localhost:5001/intent/execute/intent_1234567890_1234
```

#### GET /intent/list/{owner_address}
Liste les intents d'un utilisateur
```bash
curl http://localhost:5001/intent/list/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

### 4. Monitoring & Analytics

#### GET /ccip/analytics
Statistiques des transactions CCIP
```bash
curl http://localhost:5001/ccip/analytics
```

#### GET /intent/analytics
Statistiques des intents
```bash
curl http://localhost:5001/intent/analytics
```

#### GET /ccip/health
Santé du système CCIP
```bash
curl http://localhost:5001/ccip/health
```

### 5. Utilitaires

#### GET /check-balance/{address}
Vérification rapide du balance
```bash
curl http://localhost:5001/check-balance/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

#### GET /faucet-sepolia
Guide pour obtenir des tokens testnet
```bash
curl http://localhost:5001/faucet-sepolia
```

#### POST /admin/mock-data
Crée des données de test pour la démo
```bash
curl -X POST http://localhost:5001/admin/mock-data
```

## 🔧 Configuration des Chaînes

### Chaînes Supportées
- **Ethereum Sepolia** (Chain ID: 11155111)
- **Base Sepolia** (Chain ID: 84532)
- **Flow Testnet** (Chain ID: 747)

### Contrats CCIP
```javascript
const CCIP_CONFIG = {
  "ethereum_sepolia": {
    "router": "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59",
    "link_token": "0x779877A7B0D9E8603169DdbD7836e478b4624789"
  },
  "base_sepolia": {
    "router": "0xD3b06cEbF099CE7DA4AcCf578aaebFDBd6e88a93",
    "link_token": "0xE4aB69C077896252FAFBD49EFD26B5D171A32410"
  }
}
```

## 📱 Intégration Frontend (React Native)

### Exemple d'utilisation
```typescript
// Récupérer les tokens d'un utilisateur
const fetchUserTokens = async (address: string) => {
  const response = await fetch(`http://localhost:5001/tokens/all/${address}`);
  const data = await response.json();
  return data;
};

// Initier un transfert CCIP
const initiateCCIPTransfer = async (transferData: any) => {
  const response = await fetch('http://localhost:5001/ccip/transfer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(transferData),
  });
  return response.json();
};

// Créer un intent financier
const createIntent = async (intentData: any) => {
  const response = await fetch('http://localhost:5001/intent/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(intentData),
  });
  return response.json();
};
```

## 🧪 Tests

### Lancer les tests automatisés
```bash
python test_api.py
```

### Tests manuels avec curl
```bash
# Test de base
curl http://localhost:5001/

# Test avec une adresse réelle
curl http://localhost:5001/tokens/ethereum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Test CCIP
curl http://localhost:5001/ccip/chains
```

## 🚨 Gestion des Erreurs

### Codes d'erreur communs
- `400` : Paramètres invalides ou manquants
- `404` : Ressource non trouvée (transaction, intent)
- `500` : Erreur serveur interne

### Format des réponses d'erreur
```json
{
  "success": false,
  "error": "Description de l'erreur",
  "timestamp": "2024-12-15T14:30:00Z"
}
```

## 🔒 Sécurité

### Points importants
- Les clés privées ne sont jamais stockées côté API
- Toutes les transactions sont simulées en mode testnet
- Validation stricte des adresses Ethereum
- Rate limiting recommandé en production

### Production
Pour la production, ajoutez :
- Variables d'environnement sécurisées
- Base de données persistante (PostgreSQL/MongoDB)
- Authentification JWT
- Rate limiting avec Redis
- Monitoring avec Prometheus

## 🚀 Déploiement

### Développement
```bash
python app.py
```

### Production avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## 📊 Monitoring

### Endpoints de santé
- `/ccip/health` : Santé du système CCIP
- `/ccip/analytics` : Métriques de performance
- `/intent/analytics` : Statistiques des intents

### Logs importants
- Erreurs de connectivité RPC
- Échecs de transaction CCIP
- Exécutions d'intents
- Erreurs de validation

## 🤝 Support

Pour des questions ou des problèmes :
1. Vérifiez la documentation
2. Testez avec `/test-api`
3. Consultez les logs d'erreur
4. Utilisez les endpoints de debug

---

**Version API :** 2.0.0-ccip  
**Dernière mise à jour :** Juillet 2025  
**Compatibilité :** Ethereum Sepolia, Base Sepolia, Flow Testnet
