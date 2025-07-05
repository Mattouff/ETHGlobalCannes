# 📰 Agent News#### 🌐 API REST Intégrée + Cache Anti-Doublons
- **Endpoint POST /news** : Récupération de news à la demande via API REST
- **Endpoint GET /health** : Monitoring de l'état de l'agent
- **Cache intelligent** : Évite d'afficher les mêmes actualités plusieurs fois
- **Récupération automatique** : Surveillance continue toutes les 3 secondes avec filtrage
- **"No new information"** : Retourne ce message s'il n'y a pas de nouvelles actualités
- **Logging intelligent** : Journalis### 📰 Agent News
L'agent fournit un logging détaillé avec cache anti-doublons :
```bash
🚀 News Agent démarré - news_agent
📍 Adresse: agent1qvk...
🌐 API REST disponible sur http://localhost:8001
📋 Endpoints: POST /news, GET /health
⏰ Récupération automatique toutes les 3 secondes

🔄 Récupération automatique des news...
📰 3 NOUVELLES ACTUALITÉS:
{JSON des nouvelles actualités}

🔄 Récupération automatique des news...
📰 No new information

🌐 API Call - Requête news via REST
🔍 Query: bitcoin regulation, Type: crypto
✅ 2 nouvelles actualités retournées via REST API
```lée de toutes les activités IntentFi - Suite d'Agents Intelligents

## 🎯 Vue d'ensemble

Suite de deux agents autonomes basés sur **uAgents** :

1. **📰 Agent News** : Récupère et analyse automatiquement les actualités ayant un impact potentiel sur les marchés des cryptomonnaies
2. **🧠 Agent IntentFi** : Génère des recommandations d'investissement intelligentes et des stratégies financières automatisées

Les deux agents utilisent des APIs externes (NewsAPI, Claude AI) pour fournir des informations et analyses en temps réel sous format JSON structuré.

## ✨ Fonctionnalités

### � Agent News (`news.py`)

#### �🔄 Récupération Automatique
- **Surveillance continue** : Récupère les actualités toutes les 5 minutes
- **Affichage JSON** : Présente les résultats dans un format structuré avec emojis
- **Logging intelligent** : Journalisation détaillée de toutes les activités

#### 🎯 Recherche Spécialisée Crypto
L'agent est optimisé pour détecter les actualités susceptibles d'influencer les cours des cryptomonnaies :

##### 📊 Types d'actualités surveillées :
- **Régulations** : SEC, ETF Bitcoin, nouvelles lois
- **Adoption institutionnelle** : BlackRock, MicroStrategy, Tesla
- **Politique monétaire** : Fed, taux d'intérêt, inflation
- **Plateformes d'échange** : Binance, Coinbase, réserves
- **Stablecoins** : Tether, USDC, transparence des réserves
- **Aspects légaux** : Interdictions, régulations gouvernementales
- **Personnalités influentes** : Trump, Musk et leurs déclarations

#### 🤖 Intelligence de Recherche + Cache Anti-Doublons
- **Recherche flexible** : Support des paramètres `query` et `search_type`
- **Types de recherche prédéfinis** : crypto, tech, general
- **Recherche avancée** : Support de la syntaxe NewsAPI (AND, OR, NOT, +, -)
- **Cache intelligent** : Mémorisation des articles déjà affichés (basé sur titre + URL)
- **Filtrage automatique** : Seules les nouvelles actualités sont retournées
- **Nettoyage automatique** : Cache limité à 1000 articles avec rotation
- **Fallback intelligent** : Données simulées en cas d'erreur API

### 🧠 Agent IntentFi (`intellect.py`)

#### 💰 Recommandations Financières Intelligentes
- **Analyse de marché en temps réel** : Intégration avec Claude AI pour des analyses sophistiquées
- **Stratégies multi-chaînes** : Recommandations cross-chain avec LayerZero
- **Gestion des risques** : Stop-loss automatiques et diversification

#### 🎯 Types d'Intents Supportés

##### 💹 Price-Based Intents
- **Conditions de prix** : Déclenchement basé sur des seuils ETH/autres cryptos
- **Analyse technique** : Niveaux de support/résistance via Chainlink
- **Transferts conditionnels** : Exécution automatique cross-chain

##### ⏰ Time-Based Intents  
- **DCA (Dollar Cost Averaging)** : Investissements programmés optimisés
- **Scheduling intelligent** : Fréquence adaptée à la volatilité du marché
- **Allocation multi-chaînes** : Distribution optimisée des fonds

##### 🛡️ Risk Management Intents
- **Protection automatique** : Stop-loss adaptatifs
- **Diversification** : Répartition cross-chain intelligente  
- **Monitoring continu** : Surveillance du portfolio via Chainlink

#### 🌐 API REST Intégrée
- **GET `/health`** : Statut de l'agent
- **POST `/recommend`** : Génération de recommandations
- **GET `/intents/popular`** : Intents populaires de la communauté

#### 🤖 Intelligence Artificielle
- **Intégration Claude AI** : Analyses sophistiquées en temps réel
- **Fallback intelligent** : Recommandations de secours si AI indisponible
- **Prompts spécialisés** : Contexte financier et crypto optimisé

## 🚀 Installation

### Prérequis
- Python 3.11+
- Clé API NewsAPI (gratuite sur [newsapi.org](https://newsapi.org))
- Accès à Claude AI pour IntentFi (optionnel, fallback disponible)

### Configuration de l'environnement
```bash
# Navigation vers le répertoire
cd /Users/matteo/ETHGlobalCannes/agents/intellect

# Installation des dépendances
/Users/matteo/ETHGlobalCannes/.venv/bin/python -m pip install -r requirements.txt

# Configuration des variables d'environnement
cp .env.example .env
# Puis éditez le fichier .env avec vos vraies clés API
```

### Dépendances
```txt
requests==2.31.0
uagents==0.22.5
python-dotenv==1.0.0
```

## 🔧 Configuration

### Agent News (`news.py`)

#### Configuration de l'API NewsAPI
Utilisation sécurisée via variables d'environnement :
```bash
# Fichier .env
NEWSAPI_KEY="YOUR_API_KEY"
```

#### Paramètres de l'agent (avec cache et récupération automatique)
```python
agent = Agent(
    name="news_agent",
    seed="news_secret_seed_phrase",
    port=8001,
    endpoint=["http://localhost:8001/submit"]  # Communication inter-agents
)

# Cache global pour éviter les doublons
displayed_news_cache = set()
```

#### Endpoints REST disponibles
- `POST http://localhost:8001/news` - Récupération de news (avec filtrage anti-doublons)
- `GET http://localhost:8001/health` - Statut de l'agent

#### Récupération automatique
- **Fréquence** : Toutes les 3 secondes
- **Filtrage** : Seules les nouvelles actualités sont affichées
- **Logs** : "No new information" si aucune nouveauté

### Agent IntentFi (`intellect.py`)

#### Configuration de base
```python
agent = Agent(
    name="intellect",
    port=8001,
    seed="intentfi-agent-seed-phrase",
    endpoint=["http://localhost:8001/submit"]
)
```

#### Intégration Claude AI
```python
AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"
```

#### API REST Endpoints
- `GET http://localhost:8001/health` - Statut de l'agent
- `POST http://localhost:8001/recommend` - Génération de recommandations
- `GET http://localhost:8001/intents/popular` - Intents populaires

## 🎮 Utilisation

### 📰 Lancement de l'Agent News
```bash
# Méthode recommandée
cd /Users/matteo/ETHGlobalCannes/agents/intellect
/Users/matteo/ETHGlobalCannes/.venv/bin/python news.py

# Alternative avec script wrapper
./run_news_agent.sh
```

### 🧠 Lancement de l'Agent IntentFi
```bash
# Lancement de l'agent IntentFi
cd /Users/matteo/ETHGlobalCannes/agents/intellect
/Users/matteo/ETHGlobalCannes/.venv/bin/python intellect.py
```

### 💬 API REST Agent News

#### Récupération de news (POST /news)
```bash
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bitcoin regulation",
    "search_type": "crypto"
  }'
```

#### Paramètres de recherche
```json
{
  "query": "votre_recherche_personnalisée",    // Optionnel
  "search_type": "crypto"                      // crypto, tech, general
}
```

#### Types de recherche prédéfinis avec cache anti-doublons
- **"crypto"** : Actualités optimisées pour l'impact marché crypto
- **"tech"** : Actualités technologiques (AI, innovation)  
- **"general"** : Actualités générales (top headlines US)

**⚠️ Important** : Chaque appel REST filtre automatiquement les articles déjà retournés précédemment

#### Exemples de réponses avec cache anti-doublons

**1er appel** - 5 nouvelles actualités :
```json
{
  "news": [
    {
      "title": "Bitcoin ETF Approval...",
      "description": "The SEC has...",
      "url": "https://...",
      "source": "Reuters",
      "published_at": "2025-07-05T..."
    }
  ],
  "total_articles": 5,
  "timestamp": "2025-07-05T..."
}
```

**2ème appel immédiat** - Aucune nouvelle :
```json
{
  "news": [
    {
      "title": "No new information",
      "description": "No new articles found since last request",
      "url": "",
      "source": "System",
      "published_at": "2025-07-05T..."
    }
  ],
  "total_articles": 0,
  "timestamp": "2025-07-05T..."
}
```

**3ème appel plus tard** - 2 nouvelles actualités :
```json
{
  "news": [
    /* Seulement les 2 nouveaux articles */
  ],
  "total_articles": 2,
  "timestamp": "2025-07-05T..."
}
```

### 🧠 API IntentFi

#### Demande de recommandation (POST /recommend)
```json
{
  "user_id": "user123",
  "intent_type": "price_based",
  "parameters": {
    "target_price": 3200,
    "amount": 100
  }
}
```

#### Réponse type
```json
{
  "success": true,
  "recommendation": {
    "type": "conditional_transfer",
    "condition": "ETH > $3200",
    "action": "Transfer 50 USDC to Optimism via LayerZero",
    "confidence": 0.85,
    "reasoning": "Analyse technique détaillée...",
    "cross_chain_details": {
      "source_chain": "Ethereum",
      "target_chain": "Optimism",
      "estimated_gas": "$3-6 USD"
    }
  }
}

## 📋 Structure des données

### 📰 Agent News

#### Modèles REST
```python
class NewsRequest(Model):
    query: str = None           # Recherche personnalisée (optionnel)
    search_type: str = "crypto" # crypto, tech, general

class NewsData(Model):
    title: str           # Titre de l'article
    description: str     # Description/résumé
    url: str            # URL de l'article
    source: str         # Source (ex: Reuters, Bloomberg)
    published_at: str   # Date de publication (ISO format)

class NewsResponse(Model):
    news: list[NewsData]    # Liste des articles
    total_articles: int     # Nombre total d'articles
    timestamp: str          # Horodatage de la requête

class HealthResponse(Model):
    status: str        # Statut de l'agent
    agent: str         # Nom de l'agent
    address: str       # Adresse uAgents
    timestamp: str     # Timestamp
```

### 🧠 Agent IntentFi

#### Modèles de requête
```python
class IntentRequest(Model):
    user_id: str                    # Identifiant utilisateur
    intent_type: str               # Type: price_based, time_based, risk_management
    parameters: dict[str, Any]     # Paramètres spécifiques à l'intent

class TextPrompt(Model):
    text: str                      # Prompt textuel pour Claude AI

class StructuredOutputPrompt(Model):
    prompt: str                    # Prompt détaillé
    output_schema: dict[str, Any]  # Schéma JSON attendu
```

#### Modèles de réponse
```python
class IntentResponse(Model):
    success: bool                   # Statut de la requête
    recommendation: dict[str, Any]  # Recommandation générée
    message: str                   # Message descriptif

class HealthResponse(Model):
    status: str        # Statut de l'agent
    agent: str         # Nom de l'agent
    address: str       # Adresse uAgents
    timestamp: str     # Timestamp
```

## 🔍 Exemples d'utilisation

### 📰 Agent News - Recherche crypto avec impact marché
```bash
# Recherche crypto par défaut via REST API
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"search_type": "crypto"}'

# Recherche personnalisée optimisée
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"query": "(cryptocurrency OR bitcoin OR ethereum) AND (regulation OR SEC OR ETF)"}'
```

#### Exemples de requêtes REST News
```bash
# 1. Actualités crypto par défaut
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"search_type": "crypto"}'

# 2. ETF Bitcoin spécifique
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"query": "ETF bitcoin SEC"}'

# 3. Adoption institutionnelle
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"query": "BlackRock OR MicroStrategy OR Tesla bitcoin"}'

# 4. Actualités tech
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"search_type": "tech"}'

# 5. Actualités générales
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"search_type": "general"}'
```

### 🧠 Agent IntentFi - Cas d'usage

#### 1. Intent basé sur le prix
```bash
curl -X POST http://localhost:8001/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "trader123",
    "intent_type": "price_based",
    "parameters": {
      "target_price": 3500,
      "amount": 200,
      "token": "ETH"
    }
  }'
```

#### 2. Intent DCA temporel
```bash
curl -X POST http://localhost:8001/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "investor456",
    "intent_type": "time_based",
    "parameters": {
      "frequency": "weekly",
      "amount": 50,
      "token": "ETH"
    }
  }'
```

#### 3. Gestion des risques
```bash
curl -X POST http://localhost:8001/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "hodler789",
    "intent_type": "risk_management",
    "parameters": {
      "stop_loss_percent": 15,
      "diversification": true
    }
  }'
```

#### 4. Vérification de santé
```bash
curl http://localhost:8001/health
```

#### 5. Intents populaires
```bash
curl http://localhost:8001/intents/popular
```

## 🧪 Tests et débogage

### 📰 Agent News

#### Système de cache intelligent
- **Cache global** : `displayed_news_cache = set()` mémorise les articles déjà affichés
- **Identifiant unique** : Basé sur `titre + URL` de chaque article
- **Filtrage automatique** : Les articles déjà vus ne sont plus retournés
- **Nettoyage automatique** : Cache limité à 1000 articles, rotation des 500 plus récents
- **Séparation des modes** :
  - **Récupération automatique** : Filtre les doublons (`filter_displayed=True`)
  - **API REST** : Filtre également les doublons pour éviter la surcharge frontend

#### Gestion des nouvelles actualités
- **Récupération automatique** : Affiche "No new information" si aucune nouveauté
- **API REST** : Retourne un objet JSON avec "No new information" si aucune nouveauté
- **PageSize optimisé** : Récupère 10 articles, filtre les doublons, retourne les nouveaux
- **Fallback automatique** : Données simulées avec ID unique en cas d'erreur API

### 🧠 Agent IntentFi

#### Système de fallback intelligent
- **Timeout de 5 secondes** pour Claude AI
- **Recommandations de secours** basées sur l'analyse de marché
- **Logging détaillé** de toutes les interactions

#### Tests de connectivité
L'agent teste automatiquement :
- Connectivité avec Claude AI au démarrage
- Réponses structurées et textuelles
- Endpoints REST fonctionnels

#### Exemples de recommandations fallback
```json
{
  "type": "conditional_transfer",
  "condition": "ETH > $3200", 
  "action": "Transfer 50 USDC to Optimism via LayerZero",
  "confidence": 0.7,
  "reasoning": "Recommandation IntentFi basée sur l'analyse technique",
  "fallback": true,
  "chainlink_trigger": true
}
```

## 📊 Surveillance et logs

### 📰 Agent News
L'agent fournit un logging détaillé via API REST :
```bash
� News REST API démarré - Agent news_agent
📍 Adresse: agent1qvk...
🌐 API REST disponible sur http://localhost:8001
📋 Endpoints: POST /news, GET /health

🌐 API Call - Requête news via REST
🔍 Query: bitcoin regulation, Type: crypto
✅ 5 articles retournés via REST API
```

### 🧠 Agent IntentFi
Logging avancé des recommandations :
```
💰 Recommandation d'intent financier reçue!
🎯 TYPE: conditional_transfer
⚡ CONDITION: ETH > $3200
🚀 ACTION: Transfer 50 USDC to Optimism via LayerZero
🟢 CONFIANCE: 85.0%
🧠 ANALYSE: Analyse technique détaillée...
🌐 DÉTAILS CROSS-CHAIN:
   📤 Source: Ethereum
   📥 Destination: Optimism  
   ⛽ Gas estimé: $3-6 USD
```

## 🔧 Paramètres configurables

### 📰 Agent News

#### API NewsAPI
- `language=en` : Langue des articles
- `pageSize=5` : Nombre d'articles par requête
- `sortBy=publishedAt` : Tri par date de publication
- `country=us` : Pays pour les actualités générales

#### Agent uAgents (News - Hybrid : REST + Auto + Cache)
- `port=8001` : Port d'écoute de l'agent
- `endpoint=["http://localhost:8001/submit"]` : Communication inter-agents conservée
- `period=3.0` : Récupération automatique toutes les 3 secondes
- `displayed_news_cache` : Cache global anti-doublons
- `filter_displayed` : Filtrage intelligent des articles déjà vus

### 🧠 Agent IntentFi

#### Paramètres Claude AI
- `timeout=5` : Timeout pour les réponses Claude AI (5 secondes)
- `fallback_enabled=true` : Activation des recommandations de secours
- `AI_AGENT_ADDRESS` : Adresse de l'agent Claude AI

#### Types d'intents supportés
- `price_based` : Intents basés sur des conditions de prix
- `time_based` : Intents programmés (DCA, scheduling)
- `risk_management` : Intents de gestion des risques
- `custom` : Intents personnalisés

#### Cross-chain supporté
- **LayerZero** : Transferts inter-chaînes optimisés
- **Chainlink** : Données de prix et automation
- **Chaînes supportées** : Ethereum, Optimism, Arbitrum, Polygon, Base

## 🔐 Sécurité

### 📰 Agent News
- API REST sécurisée avec clés stockées dans `.env`
- Validation des paramètres d'entrée (query, search_type)
- Gestion sécurisée des erreurs API avec fallback
- Timeout et logging pour surveillance

### 🧠 Agent IntentFi
- Communication sécurisée avec Claude AI via uAgents
- Validation des schémas JSON pour les recommandations
- Timeout de sécurité pour éviter les blocages
- Wallet automatiquement financé via `fund_agent_if_low`

## 📈 Optimisations futures

### 📰 Agent News
- [x] Configuration externe des clés API via .env 
- [x] API REST pour intégration externe (Postman, curl, frontend)
- [x] Recherche flexible avec paramètres query et search_type
- [x] Cache anti-doublons intelligent pour éviter la surcharge frontend
- [x] Récupération automatique avec filtrage des actualités déjà vues
- [x] Message "No new information" quand aucune nouveauté
- [ ] Analyse de sentiment des actualités
- [ ] Intégration avec d'autres sources de news
- [ ] Notification push pour actualités critiques
- [ ] Dashboard web pour visualisation
- [ ] Persistance du cache entre redémarrages

### 🧠 Agent IntentFi
- [ ] Intégration avec plus de chaînes blockchain
- [ ] Backtesting automatique des stratégies
- [ ] Machine learning pour améliorer les recommandations
- [ ] Interface graphique pour la création d'intents
- [ ] Intégration avec des DEX pour exécution automatique
- [ ] Système de scoring des performances d'intents
- [ ] Support pour plus de types d'assets (NFTs, tokens exotiques)
- [ ] Intégration avec des protocoles DeFi (lending, staking)

## 🤝 Contribution

Cette suite d'agents fait partie du projet **ETHGlobalCannes** et utilise le framework uAgents pour l'automatisation des tâches de :
- **Veille informationnelle** (Agent News)
- **Conseil financier intelligent** (Agent IntentFi)
- **Exécution automatisée d'intents cross-chain**

### Architecture technique
- **uAgents Framework** : Communication inter-agents
- **NewsAPI** : Source d'actualités en temps réel
- **Claude AI** : Intelligence artificielle pour analyses sophistiquées
- **LayerZero** : Infrastructure cross-chain
- **Chainlink** : Oracles de prix et automation

## 📞 Support

Pour toute question ou amélioration :
- Consultez les logs détaillés des agents pour le débogage
- Référez-vous à la documentation uAgents
- Vérifiez la connectivité des APIs externes (NewsAPI, Claude AI)
- Testez les endpoints REST pour IntentFi

### Dépannage courant

#### Agent News
- **"No new information"** : Vérifier s'il y a vraiment de nouvelles actualités ou si le cache fonctionne correctement
- **Cache trop volumineux** : Le cache se nettoie automatiquement à 1000 articles
- **Pas d'articles retournés** : Vérifier la clé API NewsAPI dans `.env` ou ajuster les paramètres de recherche
- **Erreur de connexion** : API NewsAPI surchargée, utilisation automatique des données fallback
- **Port 8001 occupé** : Changer le port dans le code ou arrêter le processus existant
- **Doublons malgré le cache** : Redémarrer l'agent pour vider le cache en mémoire

#### Agent IntentFi  
- **Claude AI indisponible** : Système de fallback automatique activé
- **Erreur REST** : Vérifier que le port 8001 est libre
- **Recommandations incohérentes** : Ajuster les prompts financiers selon le marché