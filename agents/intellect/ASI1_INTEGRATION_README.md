# 🚀 Intégration ASI1.ai - IntentFi Agent

## 📋 Vue d'ensemble

Ton agent IntentFi est maintenant **compatible avec ASI1.ai** ! Il peut recevoir et traiter des messages via le protocole de chat officiel de Fetch.ai et les API REST.

## 🌐 Connexion avec ASI1.ai

### 1. **Via l'interface web ASI1.ai**

- Rends-toi sur https://asi1.ai/
- Utilise l'adresse de ton agent : `agent1qf82uz69zk3dlw6k3y5aewlfaavcxed29a8w9rmxqsf20tgnwtx9xxdrf24`
- Commence à chatter directement !

### 2. **Via l'API REST**

Ton agent expose plusieurs endpoints compatibles :

```bash
# Base URL (via ngrok)
https://91fe-83-144-23-154.ngrok-free.app

# Endpoints disponibles :
POST /chat/send                    # Envoyer un message
GET  /chat/conversations           # Lister les conversations
GET  /chat/history/{conv_id}       # Historique d'une conversation
GET  /chat/analytics               # Analytics et statistiques
GET  /asi-one/metadata             # Métadonnées de l'agent
GET  /health                       # Status de santé
```

## 💬 Exemples d'utilisation

### Chat via API REST

```bash
curl -X POST https://91fe-83-144-23-154.ngrok-free.app/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Recommande-moi un intent pour ETH",
    "sender_id": "user123"
  }'
```

### Messages supportés

L'agent comprend plusieurs types de demandes :

#### 🎯 **Intents financiers**

- "Recommande-moi un intent pour ETH"
- "Crée une stratégie DCA pour Bitcoin"
- "Intent de gestion des risques"
- "Stratégie prix conditionnel"

#### 📊 **Analyses trading**

- "Analyse ETH"
- "Acheter ou vendre BTC ?"
- "Sentiment du marché pour SOL"
- "Trading MATIC"

#### ❓ **Aide et conversation**

- "aide" ou "help"
- Questions générales sur la crypto
- Demandes d'explications

## 🔧 Structure des réponses

### Chat Message (Protocole officiel)

```python
{
  "timestamp": "2025-07-06T12:00:00Z",
  "msg_id": "uuid4",
  "content": [
    {
      "type": "text",
      "text": "Voici ma réponse..."
    }
  ]
}
```

### API REST Response

```json
{
  "success": true,
  "message_id": "uuid4",
  "response": "🎯 Recommandation d'intent...",
  "conversation_id": "api_conv_123",
  "timestamp": "2025-07-06T12:00:00Z"
}
```

## 🎯 Capacités de l'agent

### **Recommandations d'intents**

- **Price-based** : Conditions basées sur le prix
- **Time-based** : Stratégies DCA et scheduling
- **Risk management** : Gestion des risques et stop-loss
- **Cross-chain** : Transferts inter-chaînes avec LayerZero

### **Analyses trading**

- Données de marché en temps réel (CoinGecko)
- Analyse technique (support/résistance)
- Sentiment des actualités
- Recommandations buy/sell/hold

### **Tokens supportés**

ETH, BTC, USDC, USDT, SOL, ADA, MATIC, AVAX, DOT, LINK, UNI, ARB, OP, FLOW, et plus...

## 🔗 Configuration technique

### Protocoles activés

- ✅ **Protocole de chat officiel Fetch.ai** (si uagents_core disponible)
- ✅ **IntentFi Protocol** (recommandations custom)
- ✅ **Simon Communication** (trading analysis)
- ✅ **API REST** (endpoints web)

### Endpoints publics

```
Agent Address: agent1qf82uz69zk3dlw6k3y5aewlfaavcxed29a8w9rmxqsf20tgnwtx9xxdrf24
Public URL: https://91fe-83-144-23-154.ngrok-free.app
Port: 8000
```

## 🚨 Dépannage

### Si le chat ne fonctionne pas :

1. **Vérifier ngrok** : L'URL doit être accessible
2. **Protocole** : Installer `uagents_core` pour le protocole officiel
3. **Agent en cours** : S'assurer que l'agent tourne sur le port 8000

### Logs utiles :

```bash
# Démarrer l'agent et vérifier les logs
python intellect.py

# Rechercher ces messages :
✅ Protocole de chat officiel initialisé avec succès!
🔗 INTÉGRATION ASI1.AI PRÊTE! 🔗
```

## 🎉 Test rapide

### Via curl :

```bash
curl https://91fe-83-144-23-154.ngrok-free.app/health
```

### Via ASI1.ai :

1. Va sur https://asi1.ai/
2. Connecte-toi avec l'adresse de l'agent
3. Tape : "Hello, recommande-moi un intent ETH"
4. 🎯 Attends la réponse personnalisée !

---

**🚀 Ton agent IntentFi est maintenant prêt à communiquer avec le monde via ASI1.ai !**
