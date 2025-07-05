# 🚀 Lancement des Agents IntentFi

## Méthode recommandée : News Agent avec logging JSON

### Launcher automatique (Recommandé)
```bash
cd /Users/matteo/ETHGlobalCannes/agents/intellect
python3 news_launcher.py
```

**Avantages :**
- ✅ Lance automatiquement `news.py`
- ✅ Affiche logs en temps réel avec timestamps
- ✅ **Génère automatiquement `news_logs.json`** avec tous les événements
- ✅ Rotation automatique (garde 1000 derniers événements)
- ✅ Arrêt propre avec Ctrl+C

### Surveillance des logs JSON
```bash
# Voir les logs en temps réel
tail -f news_logs.json | jq .

# Compter les événements par type
cat news_logs.json | jq '.[] | .event_type' | sort | uniq -c

# Filtrer les nouvelles actualités
cat news_logs.json | jq '.[] | select(.event_type=="new_articles_found")'
```

## Alternative : Lancement manuel 2 terminaux

### Terminal 1 - IntentFi Agent (port 8000)
```bash
cd /Users/matteo/ETHGlobalCannes/agents/intellect
/usr/local/opt/python@3.11/bin/python3.11 intellect.py
```

### Terminal 2 - News Agent (port 8001)
```bash
cd /Users/matteo/ETHGlobalCannes/agents/intellect
/usr/local/opt/python@3.11/bin/python3.11 news.py
```

## 📊 Types d'événements dans news_logs.json

Le launcher génère automatiquement les événements suivants :
- `launcher_startup` : Démarrage du launcher
- `agent_startup` : Démarrage du News Agent
- `api_ready` : API REST prête
- `new_articles_found` : Nouvelles actualités (avec nombre)
- `no_new_news` : Aucune nouvelle actualité
- `api_request` : Requête API REST reçue
- `error` : Erreurs système
- `shutdown_request` : Arrêt demandé
- `shutdown_complete` : Arrêt terminé

## � Endpoints disponibles

### IntentFi Agent (port 8000)
- `GET /health` - Status de l'agent
- `POST /recommend` - Recommandations d'intents
- `GET /intents/popular` - Intents populaires

### News Agent (port 8001)
- `GET /health` - Status de l'agent
- `POST /news` - Récupération des actualités

## � Test rapide des APIs

```bash
# Test IntentFi Agent
curl http://localhost:8000/health

# Test News Agent
curl http://localhost:8001/health

# Récupérer des news crypto
curl -X POST http://localhost:8001/news \
  -H "Content-Type: application/json" \
  -d '{"search_type": "crypto"}'
```

## 📁 Fichiers utiles

- `intellect.py` - Agent IntentFi principal
- `news.py` - Agent News avec API
- `news_launcher.py` - Launcher News avec logs formatés
- `monitor_logs.py` - Monitor des logs JSON
- `news_logs.json` - Logs JSON (auto-généré)

## �️ Configuration

Assurez-vous d'avoir :
- Fichier `.env` avec `NEWS_API_KEY`
- Python packages : `pip3 install python-dotenv requests uagents`
