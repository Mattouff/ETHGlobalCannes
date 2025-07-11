from typing import Any
import json
import uuid
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

# Charger les variables d'environnement
load_dotenv()

# Cache global pour éviter de réafficher les mêmes news
displayed_news_cache = set()

# Fichier de log JSON pour les articles uniquement
ARTICLES_FILE = "news_logs.json"

def save_articles_to_json(new_articles: list):
    """Sauvegarde les nouveaux articles au début du fichier JSON (sans doublons)"""
    try:
        # Lire les articles existants
        existing_data = {"articles": []}
        if os.path.exists(ARTICLES_FILE):
            try:
                with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if "articles" not in existing_data:
                        existing_data = {"articles": []}
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = {"articles": []}
        
        # Créer un set des articles existants pour éviter les doublons (basé sur titre + url)
        existing_keys = {f"{article.get('title', '')}-{article.get('url', '')}" for article in existing_data["articles"]}
        
        # Filtrer les nouveaux articles pour éviter les doublons
        truly_new_articles = []
        for article in new_articles:
            article_key = f"{article.get('title', '')}-{article.get('url', '')}"
            if article_key not in existing_keys:
                truly_new_articles.append(article)
        
        # Ajouter seulement les vrais nouveaux articles au début (plus récent en premier)
        all_articles = truly_new_articles + existing_data["articles"]
        
        # Limiter à 100 articles pour éviter un fichier trop volumineux
        if len(all_articles) > 100:
            all_articles = all_articles[:100]
        
        # Préparer la structure finale simplifiée
        articles_data = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": len(all_articles),
            "articles": all_articles
        }
        
        # Écrire les articles mis à jour
        with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des articles: {e}")

def log_to_json(event_type: str, data: dict = None, message: str = None):
    """Log les événements dans un fichier JSON pour monitoring (système interne seulement)"""
    # Cette fonction est maintenant utilisée seulement pour les événements système
    # Les articles sont gérés par save_articles_to_json()
    pass

# instantiate agent
agent = Agent(
    name="news_agent",
    seed="news_secret_seed_phrase",
    port=8002,
    endpoint=["http://localhost:8002/submit"]
)

# Modèle pour les données de news
class NewsData(Model):
    title: str
    description: str
    url: str
    source: str
    published_at: str

class NewsResponse(Model):
    news: list[NewsData]
    total_articles: int
    timestamp: str

class TextMessage(Model):
    message: str

class NewsRequest(Model):
    query: str = None
    search_type: str = "crypto"  # crypto, tech, general

class HealthResponse(Model):
    status: str
    agent: str
    address: str
    timestamp: str

AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"

def fetch_top_news(query=None, search_in=None, filter_displayed=False):
    """Récupère les news à la une depuis l'API NewsAPI"""
    try:
        # Configuration de l'API NewsAPI depuis les variables d'environnement
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            raise ValueError("Clé API NewsAPI manquante. Vérifiez votre fichier .env")
        
        # Construire l'URL avec des paramètres flexibles
        if query:
            # Si une recherche spécifique est demandée
            search_params = f"q={query}"
            if search_in:
                search_params += f"&searchIn={search_in}"
            url = f"https://newsapi.org/v2/everything?{search_params}&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            # Formater les articles pour correspondre à notre modèle
            formatted_news = []
            for article in articles:
                # Créer un identifiant unique pour l'article (basé sur titre + URL)
                article_id = f"{article.get('title', '')}-{article.get('url', '')}"
                
                # Si filter_displayed est activé, ignorer les articles déjà affichés
                if filter_displayed and article_id in displayed_news_cache:
                    continue
                
                formatted_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "") if article.get("source") else "",
                    "published_at": article.get("publishedAt", datetime.now().isoformat()),
                    "article_id": article_id
                }
                formatted_news.append(formatted_article)
                
                # Ajouter l'ID au cache si on filtre
                if filter_displayed:
                    displayed_news_cache.add(article_id)
            
            return formatted_news
        else:
            print(f"Erreur API: {response.status_code} - {response.text}")
            # Fallback vers les données simulées en cas d'erreur
            return get_mock_news()
            
    except Exception as e:
        print(f"Erreur lors de la récupération des news: {e}")
        # Fallback vers les données simulées en cas d'erreur
        return get_mock_news()

def get_mock_news():
    """Données de news simulées en cas de fallback"""
    mock_id = f"mock-{datetime.now().timestamp()}"
    return [
        {
            "title": "ERROR - to get data from NewsAPI",
            "description": "NewsApi is not available, using mock data",
            "url": "",
            "source": "Internal Mock",
            "published_at": datetime.now().isoformat(),
            "article_id": mock_id
        }
    ]

def clear_old_cache():
    """Nettoie le cache pour éviter qu'il devienne trop volumineux"""
    global displayed_news_cache
    if len(displayed_news_cache) > 1000:  # Limite à 1000 articles en cache
        # Garde seulement les 500 plus récents (approximation)
        cache_list = list(displayed_news_cache)
        displayed_news_cache = set(cache_list[-500:])

# startup handler
@agent.on_event("startup")
async def startup_function(ctx: Context):
    ctx.logger.info(f"🚀 News Agent démarré - {agent.name}")
    ctx.logger.info(f"📍 Adresse: {agent.address}")
    ctx.logger.info(f"🌐 API REST disponible sur http://localhost:8002")
    ctx.logger.info(f"📋 Endpoints: POST /news, GET /health")
    ctx.logger.info(f"🎯 Focus sur: ARBITRUM, ETH, FLOW, OPTI")
    ctx.logger.info(f"⏰ Récupération automatique toutes les 3 secondes")

# Handler pour récupérer et afficher les news
@agent.on_interval(period=3.0)  # Toutes les 5 minutes
async def fetch_and_display_news(ctx: Context):
    """Récupère les news toutes les 5 minutes et affiche seulement les nouvelles (focus sur ARBITRUM, ETH, FLOW, OPTI)"""
    ctx.logger.info("🔄 Récupération automatique des news (tokens: ARBITRUM, ETH, FLOW, OPTI)...")
    
    try:
        # Nettoyer le cache de temps en temps
        clear_old_cache()
        
        # Requête spécialisée pour nos tokens autorisés
        # ARBITRUM, ETH, FLOW, OPTI avec leurs synonymes et contexte
        specialized_query = "(ethereum OR ETH OR arbitrum OR ARB OR layer2 OR L2 OR flow OR \"flow blockchain\" OR dapper OR optimism OR OP OR optimistic) AND (price OR regulation OR SEC OR ETF OR adoption OR institutional OR DeFi OR NFT OR gaming OR upgrade OR update OR partnership OR integration OR development OR mainnet OR testnet)"
        raw_news = fetch_top_news(query=specialized_query, filter_displayed=True)
        
        # Si pas de nouvelles actualités, ne rien afficher
        if not raw_news or (len(raw_news) == 1 and raw_news[0].get("title", "").startswith("ERROR")):
            ctx.logger.info("📰 No new information for our target tokens")
            return
        
        # Filtrer davantage pour garder seulement les actualités vraiment pertinentes
        filtered_news = filter_news_by_target_tokens(raw_news)
        
        if not filtered_news:
            ctx.logger.info("📰 No relevant news for ARBITRUM/ETH/FLOW/OPTI")
            return
        
        # Formater les données (seulement les nouvelles)
        news_data = []
        for article in filtered_news:
            news_item = NewsData(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", ""),
                source=article.get("source", ""),
                published_at=article.get("published_at", "")
            )
            news_data.append(news_item)
        
        # Créer la réponse finale
        news_response = NewsResponse(
            news=news_data,
            total_articles=len(news_data),
            timestamp=datetime.now().isoformat()
        )
        
        # Sauvegarder les articles dans le fichier JSON (format complet)
        articles_for_json = [
            {
                "title": n.title,
                "description": n.description,
                "source": n.source,
                "url": n.url,
                "timestamp": n.published_at,
                "detected_tokens": detect_relevant_tokens(n.title + " " + n.description)
            } 
            for n in news_data
        ]
        save_articles_to_json(articles_for_json)
        
        # Afficher en JSON seulement s'il y a de nouvelles actualités
        news_json = json.dumps(news_response.dict(), indent=2, ensure_ascii=False)
        ctx.logger.info(f"📰 {len(news_data)} NOUVELLES ACTUALITÉS FILTRÉES:")
        ctx.logger.info(news_json)
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération automatique: {e}")

# Handler pour répondre aux requêtes de news
@agent.on_message(model=TextMessage)
async def handle_news_request(ctx: Context, sender: str, msg: TextMessage):
    """Répond uniquement avec les dernières actualités sportives"""
    ctx.logger.info(f"Sport news request received from {sender}: {msg.message}")
    sport_query = "sport OR sports OR football OR soccer OR nba OR tennis OR olympics OR athlete OR match OR game OR tournament OR world cup OR euro"
    raw_news = fetch_top_news(query=sport_query)
    news_data = []
    for article in raw_news:
        news_item = NewsData(
            title=article.get("title", ""),
            description=article.get("description", ""),
            url=article.get("url", ""),
            source=article.get("source", ""),
            published_at=article.get("published_at", "")
        )
        news_data.append(news_item)
    news_response = NewsResponse(
        news=news_data,
        total_articles=len(news_data),
        timestamp=datetime.now().isoformat()
    )
    await ctx.send(sender, news_response)

# Endpoint REST pour récupérer les news (pour le frontend)
@agent.on_rest_post("/news", NewsRequest, NewsResponse)
async def get_news_rest(ctx: Context, req: NewsRequest) -> NewsResponse:
    """Endpoint REST pour récupérer uniquement les news sportives"""
    ctx.logger.info(f"🌐 API Call - Sport news only via REST")
    sport_query = "sport OR sports OR football OR soccer OR nba OR tennis OR olympics OR athlete OR match OR game OR tournament OR world cup OR euro"
    try:
        clear_old_cache()
        raw_news = fetch_top_news(query=sport_query, filter_displayed=True)
        news_data = []
        for article in raw_news:
            news_item = NewsData(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", ""),
                source=article.get("source", ""),
                published_at=article.get("published_at", "")
            )
            news_data.append(news_item)
        news_response = NewsResponse(
            news=news_data,
            total_articles=len(news_data),
            timestamp=datetime.now().isoformat()
        )
        ctx.logger.info(f"✅ {len(news_data)} sport news returned via REST API")
        return news_response
    except Exception as e:
        ctx.logger.error(f"❌ Error during REST sport news fetch: {e}")
        fallback_news = get_mock_news()
        news_data = []
        for article in fallback_news:
            news_data.append(NewsData(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", ""),
                source=article.get("source", ""),
                published_at=article.get("published_at", "")
            ))
        return NewsResponse(
            news=news_data,
            total_articles=len(news_data),
            timestamp=datetime.now().isoformat()
        )

# Endpoint REST pour la santé de l'agent
@agent.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Endpoint de santé pour vérifier que l'agent fonctionne"""
    return HealthResponse(
        status="healthy",
        agent="News Agent",
        address=agent.address,
        timestamp=datetime.now().isoformat()
    )

displayed_news_cache.clear()  # Vider le cache complètement


def detect_relevant_tokens(text: str) -> list:
    """Détecte quels tokens sont mentionnés dans le texte"""
    text_lower = text.lower()
    found_tokens = []
    
    # Mapping des tokens avec leurs variantes
    token_patterns = {
        "ARBITRUM": ["arbitrum", "arb", "layer 2", "l2"],
        "ETH": ["ethereum", "eth", "ether"],
        "FLOW": ["flow", "flow blockchain", "dapper"],
        "OPTI": ["optimism", "opti", "op ", " op)", "optimistic"]
    }
    
    for token, patterns in token_patterns.items():
        if any(pattern in text_lower for pattern in patterns):
            found_tokens.append(token)
    
    return found_tokens


def filter_news_by_target_tokens(news_list: list) -> list:
    """Filtre les actualités pour garder seulement celles pertinentes aux tokens cibles"""
    filtered = []
    
    for article in news_list:
        title = article.get("title", "")
        description = article.get("description", "")
        full_text = f"{title} {description}".lower()
        
        # Vérifier si l'article mentionne nos tokens cibles
        relevant_tokens = detect_relevant_tokens(full_text)
        
        if relevant_tokens:
            # Ajouter les tokens détectés à l'article pour traçabilité
            article["relevant_tokens"] = relevant_tokens
            filtered.append(article)
        
        # Garder aussi les actualités générales crypto importantes
        general_crypto_keywords = [
            "sec", "etf", "regulation", "institutional", "adoption",
            "defi", "nft", "layer 2", "scaling", "gas fees"
        ]
        
        if not relevant_tokens and any(keyword in full_text for keyword in general_crypto_keywords):
            article["relevant_tokens"] = ["GENERAL_CRYPTO"]
            filtered.append(article)
    
    return filtered


if __name__ == "__main__":
    agent.run()