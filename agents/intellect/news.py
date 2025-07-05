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
    port=8001,
    endpoint=["http://localhost:8001/submit"]
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
    ctx.logger.info(f"🌐 API REST disponible sur http://localhost:8001")
    ctx.logger.info(f"📋 Endpoints: POST /news, GET /health")
    ctx.logger.info(f"⏰ Récupération automatique toutes les 3 secondes")

# Handler pour récupérer et afficher les news
@agent.on_interval(period=3.0)  # Toutes les 5 minutes
async def fetch_and_display_news(ctx: Context):
    """Récupère les news toutes les 5 minutes et affiche seulement les nouvelles"""
    ctx.logger.info("🔄 Récupération automatique des news...")
    
    try:
        # Nettoyer le cache de temps en temps
        clear_old_cache()
        
        # Récupérer les news avec focus crypto par défaut et filtrage des doublons
        crypto_query = "(cryptocurrency OR ethereum OR blockchain) AND (regulation OR SEC OR ETF OR adoption OR institutional OR ban OR legal OR government OR fed OR inflation OR tether OR binance OR coinbase OR grayscale OR blackrock OR microstrategy OR Trump OR Musk)"
        raw_news = fetch_top_news(query=crypto_query, filter_displayed=True)
        
        # Si pas de nouvelles actualités, ne rien afficher
        if not raw_news or (len(raw_news) == 1 and raw_news[0].get("title", "").startswith("ERROR")):
            ctx.logger.info("📰 No new information")
            # Ne pas logger dans JSON pour éviter le spam - juste afficher dans la console
            return
        
        # Formater les données (seulement les nouvelles)
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
                "timestamp": n.published_at
            } 
            for n in news_data
        ]
        save_articles_to_json(articles_for_json)
        
        # Afficher en JSON seulement s'il y a de nouvelles actualités
        news_json = json.dumps(news_response.dict(), indent=2, ensure_ascii=False)
        ctx.logger.info(f"📰 {len(news_data)} NOUVELLES ACTUALITÉS:")
        ctx.logger.info(news_json)
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération automatique: {e}")

# Handler pour répondre aux requêtes de news
@agent.on_message(model=TextMessage)
async def handle_news_request(ctx: Context, sender: str, msg: TextMessage):
    """Répond aux requêtes de news avec les dernières actualités"""
    message_content = msg.message.lower()
    
    if "news" in message_content or "actualités" in message_content:
        ctx.logger.info(f"Requête de news reçue de {sender}: {msg.message}")
        
        # Extraire une requête de recherche si elle est spécifiée
        query = None
        if "search:" in message_content:
            # Format: "news search: bitcoin" ou "actualités search: technology"
            query = msg.message.split("search:")[-1].strip()
            ctx.logger.info(f"Recherche spécifique demandée: {query}")
        elif any(keyword in message_content for keyword in ["bitcoin", "crypto", "ethereum", "blockchain"]):
            # Détection automatique de mots-clés crypto avec impact sur les cours
            query = "(cryptocurrency OR bitcoin OR ethereum OR blockchain) AND (regulation OR SEC OR ETF OR adoption OR institutional OR ban OR legal OR government OR fed OR inflation OR tether OR binance OR coinbase OR grayscale OR blackrock OR microstrategy OR Trump OR Musk)"
        elif any(keyword in message_content for keyword in ["ai", "intelligence", "technology"]):
            # Détection automatique de mots-clés tech
            query = "AI OR artificial intelligence OR technology"
        
        raw_news = fetch_top_news(query=query)
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
        
        # Envoyer la réponse
        await ctx.send(sender, news_response)

# Endpoint REST pour récupérer les news (pour le frontend)
@agent.on_rest_post("/news", NewsRequest, NewsResponse)
async def get_news_rest(ctx: Context, req: NewsRequest) -> NewsResponse:
    """Endpoint REST pour récupérer les news depuis le frontend"""
    ctx.logger.info(f"🌐 API Call - Requête news via REST")
    ctx.logger.info(f"🔍 Query: {req.query}, Type: {req.search_type}")
    
    try:
        # Nettoyer le cache de temps en temps
        clear_old_cache()
        
        # Déterminer la requête basée sur les paramètres
        query = None
        
        if req.query:
            # Requête spécifique fournie
            query = req.query
        elif req.search_type == "crypto":
            # Requête crypto par défaut
            query = "(cryptocurrency OR bitcoin OR ethereum OR blockchain) AND (regulation OR SEC OR ETF OR adoption OR institutional OR ban OR legal OR government OR fed OR inflation OR tether OR binance OR coinbase OR grayscale OR blackrock OR microstrategy OR Trump OR Musk)"
        elif req.search_type == "tech":
            # Requête tech
            query = "AI OR artificial intelligence OR technology"
        # Si search_type == "general", query reste None pour les actualités générales
        
        # Récupérer les news avec filtrage pour éviter les doublons
        raw_news = fetch_top_news(query=query, filter_displayed=True)
        
        # Si pas de nouvelles actualités, retourner "No new information"
        if not raw_news or (len(raw_news) == 1 and raw_news[0].get("title", "").startswith("ERROR")):
            # Retourner "No new information" sans logger (évite le spam dans les logs JSON)
            return NewsResponse(
                news=[NewsData(
                    title="No new information",
                    description="No new articles found since last request",
                    url="",
                    source="System",
                    published_at=datetime.now().isoformat()
                )],
                total_articles=0,
                timestamp=datetime.now().isoformat()
            )
        
        # Formater les données (seulement les nouvelles)
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
        
        # Créer la réponse finale
        news_response = NewsResponse(
            news=news_data,
            total_articles=len(news_data),
            timestamp=datetime.now().isoformat()
        )
        
        ctx.logger.info(f"✅ {len(news_data)} nouvelles actualités retournées via REST API")
        return news_response
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération REST: {e}")
        # Retourner des données fallback
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

if __name__ == "__main__":
    agent.run()