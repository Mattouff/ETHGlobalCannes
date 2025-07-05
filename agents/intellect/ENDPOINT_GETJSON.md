# 🔗 Endpoint /getJson pour le Frontend

## Description
L'endpoint `/getJson` permet au frontend de récupérer toutes les actualités crypto stockées dans `news_logs.json`.

## URL
```
GET http://localhost:8000/getJson
```

## Réponse
```json
{
  "articles": [
    {
      "title": "Titre de l'actualité",
      "description": "Description complète",
      "source": "Source (ex: CoinDesk, Forbes, etc.)",
      "url": "URL complète de l'article",
      "timestamp": "2025-07-04T12:05:00Z"
    }
  ],
  "total_articles": 11,
  "timestamp": "2025-07-05T14:09:12.632667",
  "status": "success"
}
```

## Status possibles
- `"success"` : Articles récupérés avec succès
- `"no_data"` : Fichier news_logs.json non trouvé
- `"json_error"` : Erreur de format JSON
- `"error"` : Erreur système

## Exemple d'utilisation JavaScript
```javascript
// Récupérer les actualités
fetch('http://localhost:8000/getJson')
  .then(response => response.json())
  .then(data => {
    console.log(`📰 ${data.total_articles} articles trouvés`);
    
    if (data.status === 'success') {
      data.articles.forEach(article => {
        console.log(`${article.title} (${article.source})`);
      });
    }
  })
  .catch(error => console.error('Erreur:', error));
```

## Exemple d'utilisation Python
```python
import requests

response = requests.get('http://localhost:8000/getJson')
data = response.json()

print(f"📰 {data['total_articles']} articles")
for article in data['articles'][:5]:
    print(f"• {article['title'][:60]}... ({article['source']})")
```

## Test rapide
```bash
# Test avec curl
curl http://localhost:8000/getJson

# Test avec script Python
python3 test_get_json.py
```

## Notes
- Les articles sont triés du plus récent au plus ancien
- Maximum 100 articles stockés (rotation automatique)
- Déduplication automatique basée sur titre + URL
- Actualisation automatique via news.py toutes les heures
