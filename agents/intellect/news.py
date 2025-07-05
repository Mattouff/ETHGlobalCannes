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

AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"

def fetch_top_news(query=None, search_in=None):
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
            url = f"https://newsapi.org/v2/everything?{search_params}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
        else:
            # Sinon, récupérer les actualités générales
            url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={api_key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            # Formater les articles pour correspondre à notre modèle
            formatted_news = []
            for article in articles:
                formatted_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "") if article.get("source") else "",
                    "published_at": article.get("publishedAt", datetime.now().isoformat())
                }
                formatted_news.append(formatted_article)
            
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
    return [
        {
            "title": "ERROR - to get data from NewsAPI",
            "description": "NewsApi is not available, using mock data",
            "url": "",
            "source": "Internal Mock",
            "published_at": datetime.now().isoformat()
        }
    ]

# startup handler
@agent.on_event("startup")
async def startup_function(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")

# Handler pour récupérer et afficher les news
@agent.on_interval(period=300.0)  # Toutes les 5 minutes
async def fetch_and_display_news(ctx: Context):
    """Récupère les news toutes les 5 minutes et les affiche en JSON"""
    ctx.logger.info("Récupération des news à la une...")
    
    try:
        # Récupérer les news avec focus crypto par défaut
        crypto_query = "(cryptocurrency OR bitcoin OR ethereum OR blockchain) AND (regulation OR SEC OR ETF OR adoption OR institutional OR ban OR legal OR government OR fed OR inflation OR tether OR binance OR coinbase OR grayscale OR blackrock OR microstrategy OR Trump OR Musk)"
        raw_news = fetch_top_news(query=crypto_query)
        
        # Formater les données
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
        
        # Afficher en JSON
        news_json = json.dumps(news_response.dict(), indent=2, ensure_ascii=False)
        ctx.logger.info("📰 NEWS À LA UNE:")
        ctx.logger.info(news_json)
        
    except Exception as e:
        ctx.logger.error(f"Erreur lors de la récupération des news: {e}")

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

if __name__ == "__main__":
    agent.run()