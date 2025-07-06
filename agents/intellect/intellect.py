from typing import Any, Dict
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import json
import uuid
from datetime import datetime
import os
import aiohttp
import statistics
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextPrompt(Model):
    text: str


class TextResponse(Model):
    text: str


class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: dict[str, Any]


class StructuredOutputResponse(Model):
    output: dict[str, Any]


class IntentRequest(Model):
    user_id: str
    intent_type: str
    parameters: dict[str, Any]


class IntentResponse(Model):
    success: bool
    recommendation: dict[str, Any]
    message: str


class HealthResponse(Model):
    status: str
    agent: str
    address: str
    timestamp: str

class PopularIntentsResponse(Model):
    popular_intents: list[dict[str, Any]]
    total_count: int
    timestamp: str


class NewsJsonResponse(Model):
    articles: list[dict[str, Any]]
    total_articles: int
    timestamp: str
    status: str


# Modèles pour la communication avec Simon (Trading Agent)
class TradingRecommendation(Model):
    token_symbol: str
    recommendation: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    price_target: float = None
    stop_loss: float = None
    news_sentiment: str  # "positive", "negative", "neutral"
    timestamp: str


class TradingAnalysisRequest(Model):
    token_symbol: str
    news_context: list[dict[str, Any]] = []
    request_id: str = ""
    timestamp: str = ""


class TradingAnalysisAPIResponse(Model):
    success: bool
    message: str
    analysis: dict[str, Any] = None
    timestamp: str


# Configuration de l'agent avec endpoint
agent = Agent(
    name="intellect",
    port=8000,
    seed="intentfi-agent-seed-phrase",
    endpoint=["http://localhost:8000/submit"],
    mailbox=True,
)

print(f"Agent address: {agent.address}")
fund_agent_if_low(agent.wallet.address())

AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"
SIMON_AGENT_ADDRESS = "agent1q0q5rqwj7q4upgm7fwf4dmv675nl4nqgy9tgp3qgyn8wlxwz804pxuj7032"  # Simon Agent

# Tokens autorisés pour les recommandations de trading
ALLOWED_TOKENS = ["ARBITRUM", "ETH", "FLOW", "OPTI"]

# Fichier des actualités généré par news.py
NEWS_FILE = "news_logs.json"

# Protocol pour IntentFi
intentfi_protocol = Protocol("IntentFi")

# Protocol pour la communication avec Simon
simon_protocol = Protocol("IntellectCommunication")


@intentfi_protocol.on_message(model=IntentRequest)
async def handle_intent_request(ctx: Context, sender: str, msg: IntentRequest):
    """Traite les demandes d'intent et génère des recommandations"""
    
    ctx.logger.info(f"📥 Nouvelle demande d'intent de {sender}")
    ctx.logger.info(f"User: {msg.user_id}, Type: {msg.intent_type}")
    
    # Générer une recommandation basée sur le type d'intent
    recommendation = await generate_intent_recommendation(ctx, msg)
    
    # Répondre avec la recommandation
    response = IntentResponse(
        success=True,
        recommendation=recommendation,
        message="Recommandation générée avec succès"
    )
    
    await ctx.send(sender, response)
    ctx.logger.info(f"📤 Recommandation envoyée à {sender}")

# Variables globales pour stocker les réponses de l'AI agent
pending_requests = {}
ai_responses = {}

class AIResponse(Model):
    request_id: str
    recommendation: dict[str, Any]

async def generate_intent_recommendation(ctx: Context, request: IntentRequest):
    """Génère une recommandation d'intent en contactant réellement l'AI agent Claude"""
    
    # Créer un ID unique pour cette requête
    request_id = str(uuid.uuid4())
    
    # Créer un prompt financier spécialisé basé sur le type d'intent
    if request.intent_type == "price_based":
        financial_prompt = f"""
        Analysez les conditions de marché actuelles pour ETH et recommandez un intent de trading basé sur le prix.
        
        Contexte utilisateur:
        - User ID: {request.user_id}
        - Type d'intent: {request.intent_type}
        - Paramètres: {request.parameters}
        
        Analysez:
        1. Prix actuel ETH via Chainlink (récupérez le prix en temps réel)
        2. Sentiment du marché (bullish/bearish/neutral)
        3. Volatilité récente et tendances
        4. Niveaux de support/résistance techniques
        
        Recommandez un intent conditionnel avec:
        - Condition de prix précise basée sur l'analyse (ex: "ETH > $3200")
        - Action à exécuter (transfert cross-chain LayerZero, swap, etc.)
        - Niveau de confiance basé sur l'analyse (0-1)
        - Raisonnement détaillé avec données de marché
        
        IMPORTANT: Basez votre analyse sur des données réelles de marché.
        
        Répondez UNIQUEMENT au format JSON strict:
        {{
            "type": "conditional_transfer",
            "condition": "ETH > $XXXX",
            "action": "action détaillée avec LayerZero",
            "confidence": 0.XX,
            "reasoning": "analyse détaillée",
            "request_id": "{request_id}",
            "cross_chain_details": {{
                "source_chain": "Ethereum",
                "target_chain": "Optimism",
                "estimated_gas": "$X-Y USD"
            }}
        }}
        """
        
    elif request.intent_type == "time_based":
        financial_prompt = f"""
        Créez une stratégie d'investissement temporelle (DCA, scheduling) pour l'utilisateur.
        
        Contexte utilisateur:
        - User ID: {request.user_id}
        - Type d'intent: {request.intent_type}
        - Paramètres: {request.parameters}
        
        Analysez les tendances de marché actuelles et recommandez:
        1. Fréquence optimale d'investissement (quotidien/hebdomadaire/mensuel)
        2. Allocation recommandée basée sur la volatilité actuelle
        3. Stratégie cross-chain pour optimiser les coûts
        4. Montants adaptés au profil de risque
        
        Répondez UNIQUEMENT au format JSON strict:
        {{
            "type": "scheduled_dca",
            "schedule": "timing précis",
            "action": "action détaillée avec montants et chaînes",
            "confidence": 0.XX,
            "reasoning": "analyse de marché détaillée",
            "request_id": "{request_id}"
        }}
        """
        
    elif request.intent_type == "risk_management":
        financial_prompt = f"""
        Développez une stratégie de gestion des risques pour le portfolio de l'utilisateur.
        
        Contexte utilisateur:
        - User ID: {request.user_id}
        - Type d'intent: {request.intent_type}
        - Paramètres: {request.parameters}
        
        Analysez et recommandez:
        1. Niveaux de stop-loss basés sur la volatilité actuelle
        2. Diversification cross-chain avec LayerZero
        3. Stratégies de hedging adaptées au marché actuel
        4. Seuils de déclenchement optimaux
        
        Répondez UNIQUEMENT au format JSON strict:
        {{
            "type": "stop_loss_protection",
            "condition": "condition de déclenchement précise",
            "action": "action de protection détaillée",
            "confidence": 0.XX,
            "reasoning": "analyse de risque détaillée",
            "request_id": "{request_id}"
        }}
        """
        
    else:
        financial_prompt = f"""
        Analysez la demande d'intent personnalisée et proposez une stratégie financière adaptée.
        
        Contexte utilisateur:
        - User ID: {request.user_id}
        - Type d'intent: {request.intent_type}
        - Paramètres: {request.parameters}
        
        Fournissez une recommandation basée sur les conditions de marché actuelles.
        
        Répondez UNIQUEMENT au format JSON strict:
        {{
            "type": "custom_strategy",
            "reasoning": "analyse détaillée",
            "suggested_action": "action recommandée",
            "request_id": "{request_id}"
        }}
        """
    
    # Créer le schéma de réponse pour l'intent financier
    intent_schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "condition": {"type": "string"},
            "action": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reasoning": {"type": "string"},
            "request_id": {"type": "string"},
            "cross_chain_details": {
                "type": "object",
                "properties": {
                    "source_chain": {"type": "string"},
                    "target_chain": {"type": "string"},
                    "estimated_gas": {"type": "string"}
                }
            }
        },
        "required": ["type", "reasoning", "request_id"]
    }
    
    # Envoyer le prompt à l'AI agent Claude
    try:
        prompt = StructuredOutputPrompt(
            prompt=financial_prompt,
            output_schema=intent_schema
        )
        
        ctx.logger.info(f"🧠 Envoi du prompt financier à Claude AI pour {request.user_id}")
        ctx.logger.info(f"📤 Request ID: {request_id}")
        
        pending_requests[request_id] = {
            "user_id": request.user_id,
            "intent_type": request.intent_type,
            "timestamp": ctx.timestamp if hasattr(ctx, 'timestamp') else "N/A"
        }
        
        await ctx.send(AI_AGENT_ADDRESS, prompt)
        
        ctx.logger.info("⏳ En attente de la réponse de Claude AI (45s max avec retry)...")
        ctx.logger.info(f"🔍 Debug - AI_AGENT_ADDRESS: {AI_AGENT_ADDRESS}")
        
        import asyncio
        
        # Configuration retry avec backoff exponentiel
        max_retries = 3
        base_timeout = 15  # 15 secondes par tentative
        
        for retry_attempt in range(max_retries):
            current_timeout = base_timeout * (2 ** retry_attempt)  # 15s, 30s, 60s
            ctx.logger.info(f"🔄 Tentative {retry_attempt + 1}/{max_retries} - timeout: {current_timeout}s")
            
            # Attendre la réponse avec timeout étendu
            for attempt in range(current_timeout):
                await asyncio.sleep(1)
                
                if request_id in ai_responses:
                    ctx.logger.info(f"✅ Réponse reçue de Claude AI après {retry_attempt + 1} tentative(s)!")
                    response = ai_responses[request_id]
                    
                    # Nettoyer les variables
                    del ai_responses[request_id]
                    if request_id in pending_requests:
                        del pending_requests[request_id]
                    
                    return response
            
            # Si pas de réponse, retry (sauf dernière tentative)
            if retry_attempt < max_retries - 1:
                ctx.logger.warning(f"⏰ Timeout tentative {retry_attempt + 1} - retry dans 3s...")
                await asyncio.sleep(3)
                
                # Renvoyer la requête pour retry
                try:
                    await ctx.send(AI_AGENT_ADDRESS, prompt)
                    ctx.logger.info(f"🔄 Requête renvoyée (retry {retry_attempt + 2})")
                except Exception as retry_error:
                    ctx.logger.error(f"❌ Erreur lors du retry: {retry_error}")
        
        # Timeout final après tous les retries
        ctx.logger.warning("⏰ Timeout final - Claude AI ne répond pas après 3 tentatives, retour d'une recommandation par défaut")
        
        return {
            "type": "hold_position",
            "condition": "market_analysis_pending",
            "action": "Attendre une analyse de marché plus détaillée",
            "confidence": 0.3,
            "reasoning": "Timeout de l'analyse IA. Recommandation de prudence en attendant plus d'informations.",
            "request_id": request_id
        }
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de l'envoi à Claude AI: {e}")
        return {
            "type": "error",
            "reasoning": f"Erreur lors de la communication avec Claude AI: {str(e)}",
            "suggested_action": "Réessayer la requête"
        }


@agent.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Endpoint de santé"""
    return HealthResponse(
        status="healthy",
        agent="IntentFi Recommender",
        address=agent.address,
        timestamp=datetime.now().isoformat()
    )


@agent.on_rest_post("/recommend", IntentRequest, IntentResponse)
async def recommend_intent(ctx: Context, req: IntentRequest) -> IntentResponse:
    """Endpoint pour demander une recommandation d'intent"""
    
    ctx.logger.info(f"🌐 API Call - Recommend Intent pour user: {req.user_id}")
    
    try:
        recommendation = await generate_intent_recommendation(ctx, req)
        
        return IntentResponse(
            success=True,
            recommendation=recommendation,
            message="Recommandation générée via API REST"
        )
    except Exception as e:
        ctx.logger.error(f"Erreur lors de la génération: {e}")
        return IntentResponse(
            success=False,
            recommendation={},
            message=f"Erreur: {str(e)}"
        )


@agent.on_rest_get("/intents/popular", PopularIntentsResponse)
async def get_popular_intents(ctx: Context) -> PopularIntentsResponse:
    """Endpoint pour récupérer les intents populaires"""
    
    popular_intents = [
        {
            "name": "ETH Profit Taking",
            "condition": "ETH > $3000",
            "action": "Sell 25% ETH",
            "popularity": 0.78
        },
        {
            "name": "DCA Strategy", 
            "condition": "Weekly",
            "action": "Buy 20 USDC of ETH",
            "popularity": 0.85
        },
        {
            "name": "Cross-chain Arbitrage",
            "condition": "Price difference > 2%",
            "action": "Transfer to cheaper chain",
            "popularity": 0.65
        }
    ]
    
    return PopularIntentsResponse(
        popular_intents=popular_intents,
        total_count=len(popular_intents),
        timestamp=str(ctx.timestamp) if hasattr(ctx, 'timestamp') else "N/A"
    )


@agent.on_rest_get("/getJson", NewsJsonResponse)
async def get_news_json(ctx: Context) -> NewsJsonResponse:
    """Endpoint pour récupérer le contenu du fichier news_logs.json"""
    
    ctx.logger.info("🌐 API Call - Récupération du JSON des actualités")
    
    try:
        # Lire le fichier news_logs.json
        if not os.path.exists(NEWS_FILE):
            ctx.logger.warning(f"⚠️ Fichier {NEWS_FILE} non trouvé")
            return NewsJsonResponse(
                articles=[],
                total_articles=0,
                timestamp=datetime.now().isoformat(),
                status="no_data"
            )
        
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get("articles", [])
        total_count = len(articles)
        
        ctx.logger.info(f"📰 JSON récupéré : {total_count} articles")
        
        return NewsJsonResponse(
            articles=articles,
            total_articles=total_count,
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            status="success"
        )
        
    except json.JSONDecodeError as e:
        ctx.logger.error(f"❌ Erreur JSON : {e}")
        return NewsJsonResponse(
            articles=[],
            total_articles=0,
            timestamp=datetime.now().isoformat(),
            status="json_error"
        )
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la lecture : {e}")
        return NewsJsonResponse(
            articles=[],
            total_articles=0,
            timestamp=datetime.now().isoformat(),
            status="error"
        )


agent.include(intentfi_protocol)
agent.include(simon_protocol)

class Location(Model):
    city: str
    country: str
    temperature: float


@agent.on_event("startup")
async def send_message(ctx: Context):
    ctx.logger.info("🚀 IntentFi Agent démarré!")
    ctx.logger.info(f"📍 Endpoints disponibles:")
    ctx.logger.info(f"   GET  http://localhost:8000/health")
    ctx.logger.info(f"   POST http://localhost:8000/recommend")
    ctx.logger.info(f"   GET  http://localhost:8000/intents/popular")
    ctx.logger.info(f"   GET  http://localhost:8000/getJson  🆕")
    ctx.logger.info(f"   POST http://localhost:8000/trading/recommend  🆕")
    ctx.logger.info(f"🤖 Communication avec Simon Agent: {SIMON_AGENT_ADDRESS}")
    
    # Test de connectivité avec l'AI agent
    ctx.logger.info(f"🔍 Test de connectivité avec AI Agent: {AI_AGENT_ADDRESS}")
    
    test_prompt = TextPrompt(text="Hello, this is a connectivity test from IntentFi agent. Please respond with 'Connected' if you receive this message.")
    
    try:
        await ctx.send(AI_AGENT_ADDRESS, test_prompt)
        ctx.logger.info("📤 Message de test envoyé à l'AI Agent")
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de l'envoi du test: {e}")
    
    # Test avec prompt structuré
    prompt = StructuredOutputPrompt(
        prompt="Simple test - return current timestamp and status 'online'",
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "timestamp": {"type": "string"},
                "test": {"type": "boolean"}
            }
        },
    )
    
    try:
        await ctx.send(AI_AGENT_ADDRESS, prompt)
        ctx.logger.info("📤 Test structuré envoyé à l'AI Agent")
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de l'envoi du test structuré: {e}")


@agent.on_message(TextResponse)
async def handle_text_response(ctx: Context, sender: str, msg: TextResponse):
    ctx.logger.info(f"📥 Réponse texte IA de ...{sender[-8:]}: {msg.text}")
    
    # Vérifier si c'est une réponse au test de connectivité
    if "Connected" in msg.text or "connectivity test" in msg.text.lower():
        ctx.logger.info("✅ Test de connectivité réussi avec l'AI Agent!")
    elif "Hello" in msg.text or "test" in msg.text.lower():
        ctx.logger.info("✅ Communication établie avec l'AI Agent!")


@agent.on_message(StructuredOutputResponse)  
async def handle_structured_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    """Traite les réponses structurées de Claude AI pour les recommandations d'intents"""
    ctx.logger.info(f"📥 Réponse Claude AI reçue de ...{sender[-8:]}:")
    ctx.logger.info(f"🔍 Données: {msg.output}")
    
    try:
        # Vérifier si c'est une réponse d'intent financier avec request_id
        if isinstance(msg.output, dict) and 'request_id' in msg.output:
            request_id = msg.output['request_id']
            ctx.logger.info(f"🎯 Réponse pour request_id: {request_id}")
            
            # Stocker la réponse pour qu'elle soit récupérée par generate_intent_recommendation
            ai_responses[request_id] = msg.output
            
            ctx.logger.info("💰 Recommandation d'intent financier stockée!")
            ctx.logger.info("=" * 60)
            
            recommendation = msg.output
            
            # Affichage détaillé de la recommandation
            ctx.logger.info(f"🎯 TYPE: {recommendation.get('type', 'N/A')}")
            
            if 'condition' in recommendation:
                ctx.logger.info(f"⚡ CONDITION: {recommendation['condition']}")
            
            if 'action' in recommendation:
                ctx.logger.info(f"🚀 ACTION: {recommendation['action']}")
            
            if 'confidence' in recommendation:
                confidence = recommendation['confidence']
                confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                ctx.logger.info(f"{confidence_emoji} CONFIANCE: {confidence:.1%}")
            
            if 'reasoning' in recommendation:
                ctx.logger.info(f"🧠 ANALYSE: {recommendation['reasoning']}")
            
            if 'cross_chain_details' in recommendation:
                details = recommendation['cross_chain_details']
                ctx.logger.info("🌐 DÉTAILS CROSS-CHAIN:")
                ctx.logger.info(f"   📤 Source: {details.get('source_chain', 'N/A')}")
                ctx.logger.info(f"   📥 Destination: {details.get('target_chain', 'N/A')}")
                ctx.logger.info(f"   ⛽ Gas estimé: {details.get('estimated_gas', 'N/A')}")
            
            ctx.logger.info("=" * 60)
            
        # Vérifier si c'est une réponse d'intent financier sans request_id (format général)
        elif isinstance(msg.output, dict) and any(key in msg.output for key in ['type', 'condition', 'action', 'reasoning']):
            ctx.logger.info("💰 Recommandation d'intent financier reçue (sans request_id)!")
            ctx.logger.info("=" * 60)
            
            recommendation = msg.output
            
            # Affichage détaillé
            ctx.logger.info(f"🎯 TYPE: {recommendation.get('type', 'N/A')}")
            
            if 'condition' in recommendation:
                ctx.logger.info(f"⚡ CONDITION: {recommendation['condition']}")
            
            if 'action' in recommendation:
                ctx.logger.info(f"🚀 ACTION: {recommendation['action']}")
            
            if 'confidence' in recommendation:
                confidence = recommendation['confidence']
                confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                ctx.logger.info(f"{confidence_emoji} CONFIANCE: {confidence:.1%}")
            
            if 'reasoning' in recommendation:
                ctx.logger.info(f"🧠 ANALYSE: {recommendation['reasoning']}")
            
            ctx.logger.info("=" * 60)
            
        else:
            # Autres types de réponses (comme température, etc.)
            ctx.logger.info(f"📊 Autre réponse structurée: {msg.output}")
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors du traitement de la réponse Claude: {e}")
        ctx.logger.info(f"📋 Données brutes: {msg.output}")


async def get_token_market_data(ctx: Context, token_symbol: str):
    """Récupère les données de marché réelles pour un token via API publique"""
    try:
        # Utiliser CoinGecko API (gratuite, pas besoin de clé)
        import aiohttp
        
        # Mapping des tokens vers leurs IDs CoinGecko
        token_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'USDC': 'usd-coin',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ARB': 'arbitrum',
            'OP': 'optimism',
            'FLOW': 'flow'
        }
        
        token_id = token_mapping.get(token_symbol.upper())
        
        if not token_id:
            ctx.logger.warning(f"⚠️ Token {token_symbol} non trouvé dans le mapping CoinGecko")
            return None
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if token_id in data:
                        token_data = data[token_id]
                        return {
                            'symbol': token_symbol.upper(),
                            'price_usd': token_data.get('usd'),
                            'price_change_24h': token_data.get('usd_24h_change'),
                            'market_cap': token_data.get('usd_market_cap'),
                            'volume_24h': token_data.get('usd_24h_vol')
                        }
                else:
                    ctx.logger.warning(f"⚠️ Erreur API CoinGecko: {response.status}")
                    return None
                    
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération des données de marché: {e}")
        return None

async def analyze_technical_levels(ctx: Context, token_symbol: str, current_price: float, price_change_24h: float):
    """Analyse technique simplifiée pour calculer les niveaux de support et résistance"""
    try:
        # Calculs basiques d'analyse technique
        volatility = abs(price_change_24h) / 100
        
        # Support et résistance basés sur le prix actuel et la volatilité
        if price_change_24h > 0:
            # Prix en hausse - support plus proche, résistance plus haute
            support_level = current_price * (1 - max(0.05, volatility * 1.5))
            resistance_level = current_price * (1 + max(0.08, volatility * 2))
        elif price_change_24h < 0:
            # Prix en baisse - support plus bas, résistance plus proche  
            support_level = current_price * (1 - max(0.08, volatility * 2))
            resistance_level = current_price * (1 + max(0.05, volatility * 1.5))
        else:
            # Prix stable - niveaux équilibrés
            support_level = current_price * 0.92
            resistance_level = current_price * 1.08
        
        return {
            'support': round(support_level, 6),
            'resistance': round(resistance_level, 6),
            'volatility': volatility
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur analyse technique: {e}")
        return None

async def generate_smart_recommendation(ctx: Context, token_symbol: str, market_data: dict, news_data: list, technical_levels: dict):
    """Génère une recommandation intelligente basée sur les données de marché et les news"""
    try:
        current_price = market_data.get('price_usd', 100)
        price_change_24h = market_data.get('price_change_24h', 0)
        market_cap = market_data.get('market_cap', 0)
        volume_24h = market_data.get('volume_24h', 0)
        
        # Analyse du sentiment des news
        sentiment_score = 0
        if news_data:
            all_text = " ".join([str(article.get("title", "")) + " " + str(article.get("content", "")) for article in news_data[:5]])
            positive_words = ["bullish", "rise", "growth", "gain", "increase", "positive", "up", "rally", "breakout", "adoption", "partnership"]
            negative_words = ["bearish", "fall", "decline", "loss", "decrease", "negative", "down", "crash", "dump", "risk", "regulation"]
            
            positive_count = sum(1 for word in positive_words if word in all_text.lower())
            negative_count = sum(1 for word in negative_words if word in all_text.lower())
            sentiment_score = positive_count - negative_count
        
        # Catégorisation du token
        token_lower = token_symbol.lower()
        major_tokens = ['eth', 'ethereum', 'btc', 'bitcoin', 'usdc', 'usdt', 'bnb', 'ada', 'sol', 'matic', 'avax', 'dot', 'link', 'uni']
        l2_tokens = ['arb', 'arbitrum', 'op', 'optimism', 'matic', 'polygon', 'flow']
        defi_tokens = ['uni', 'uniswap', 'sushi', 'sushiswap', 'aave', 'comp', 'compound', 'mkr', 'maker', 'crv', 'curve', 'bal', 'balancer', 'snx', 'synthetix', 'ren', 'republic', 'yfi', 'yearn']
        
        is_major = any(token in token_lower for token in major_tokens)
        is_l2 = any(token in token_lower for token in l2_tokens)
        is_defi = any(token in token_lower for token in defi_tokens)
        
        # Calcul des niveaux de prix techniques
        support = technical_levels.get('support', current_price * 0.9)
        resistance = technical_levels.get('resistance', current_price * 1.1)
        volatility = technical_levels.get('volatility', 0.05)
        
        # Logique de recommandation avancée
        if market_cap and market_cap > 1_000_000_000:  # Market cap > 1B
            # Token établi avec grosse capitalisation
            if price_change_24h > 5 and sentiment_score >= 2:
                action = "buy"
                confidence = min(0.85, 0.70 + (sentiment_score * 0.05))
                price_target = resistance * 1.1
                stop_loss = support * 0.95
                reasoning = f"Strong bullish momentum for {token_symbol} with {price_change_24h:.2f}% gain and positive news sentiment. " \
                           f"Large cap token ({market_cap/1e9:.1f}B) showing technical breakout above ${current_price:.4f}. " \
                           f"Target: ${price_target:.4f} (resistance + 10%), Stop: ${stop_loss:.4f}."
                           
            elif price_change_24h < -8 and sentiment_score <= -2:
                action = "sell"
                confidence = min(0.80, 0.65 + abs(sentiment_score * 0.05))
                price_target = support * 0.9
                stop_loss = resistance * 1.02
                reasoning = f"Significant bearish pressure on {token_symbol} with {price_change_24h:.2f}% decline and negative sentiment. " \
                           f"Large cap token showing technical breakdown below ${current_price:.4f}. " \
                           f"Target: ${price_target:.4f} (support -10%), Stop: ${stop_loss:.4f}."
                           
            else:
                action = "hold"
                confidence = 0.70 + (volatility * 5)  # Plus de volatilité = moins de confiance
                price_target = None
                stop_loss = support
                reasoning = f"Neutral momentum for established token {token_symbol}. Current price ${current_price:.4f} " \
                           f"trading within technical range (Support: ${support:.4f}, Resistance: ${resistance:.4f}). " \
                           f"Await clearer directional signals. Volatility: {volatility:.1%}"
                           
        elif is_major or is_l2:
            # Token connu mais plus petite cap
            if sentiment_score >= 1 and price_change_24h > 0:
                action = "buy"
                confidence = 0.72
                price_target = current_price * 1.15
                stop_loss = current_price * 0.85
                reasoning = f"Positive sentiment for {token_symbol} with {price_change_24h:.2f}% change. " \
                           f"Established project with growth potential. Target: ${price_target:.4f} (+15%), " \
                           f"Stop: ${stop_loss:.4f} (-15%)."
                           
            elif sentiment_score <= -1 and price_change_24h < -5:
                action = "sell"
                confidence = 0.68
                price_target = current_price * 0.88
                stop_loss = current_price * 1.08
                reasoning = f"Negative sentiment and price decline for {token_symbol}. " \
                           f"Consider reducing exposure. Target: ${price_target:.4f} (-12%), " \
                           f"Stop: ${stop_loss:.4f} (+8%)."
                           
            else:
                action = "hold"
                confidence = 0.60
                price_target = None
                stop_loss = current_price * 0.90
                reasoning = f"Mixed signals for {token_symbol}. Established project but unclear short-term direction. " \
                           f"Monitor at ${current_price:.4f} with stop at ${stop_loss:.4f}."
        elif is_defi:
            # Token DeFi établi -> analyse orientée DeFi
            if sentiment == "positive" or sentiment_score >= 1:
                action = "buy"
                confidence = 0.72 + min(0.12, sentiment_score * 0.03)
                reasoning = f"{token_symbol} is an established DeFi protocol token. " \
                           f"Positive sentiment suggests growing protocol adoption and TVL. " \
                           f"DeFi tokens benefit from ecosystem growth and yield opportunities. Sentiment: +{sentiment_score}."
                price_target = 100 * (1.12 + sentiment_score * 0.02)
                stop_loss = 100 * 0.85
            elif sentiment == "negative":
                action = "hold"
                confidence = 0.58
                reasoning = f"{token_symbol} is a DeFi protocol token facing negative sentiment. " \
                           f"DeFi tokens can be volatile. Consider protocol health, TVL trends, " \
                           f"and broader DeFi market conditions before major decisions."
                price_target = None
                stop_loss = 100 * 0.80
            else:
                action = "buy"
                confidence = 0.65
                reasoning = f"{token_symbol} represents established DeFi infrastructure. " \
                           f"Neutral sentiment with long-term potential from DeFi sector growth. " \
                           f"Monitor protocol metrics and total value locked (TVL) trends."
                price_target = 100 * 1.08
                stop_loss = 100 * 0.87
                
        elif any(token in token_lower for token in major_tokens):
            # Token majeur -> recommandation basée sur le sentiment et l'analyse technique
            if sentiment == "positive" or sentiment_score >= 1:
                action = "buy"
                confidence = 0.75 + min(0.15, sentiment_score * 0.03)  # Plus de sentiment = plus de confiance
                reasoning = f"{token_symbol} is a well-established cryptocurrency showing positive market sentiment. " \
                           f"Recent news analysis suggests favorable conditions. Sentiment score: +{sentiment_score}. " \
                           f"Consider accumulating with proper risk management."
                price_target = 100 * (1.08 + sentiment_score * 0.02)  # Prix plus élevé si sentiment très positif
                stop_loss = 100 * 0.88
            elif sentiment == "negative" or sentiment_score <= -2:
                action = "sell"
                confidence = 0.72 + min(0.15, abs(sentiment_score) * 0.03)
                reasoning = f"{token_symbol} showing negative sentiment in recent market analysis. " \
                           f"Sentiment score: {sentiment_score}. Consider reducing exposure or taking profits " \
                           f"until market conditions improve. Monitor support levels closely."
                price_target = 100 * (0.92 - abs(sentiment_score) * 0.01)
                stop_loss = 100 * 1.05
            else:
                # Sentiment neutre mais token majeur -> analyser d'autres facteurs
                # Favoriser légèrement le buy pour les tokens établis en l'absence de signaux négatifs
                action = "buy"
                confidence = 0.60  # Confiance modérée
                reasoning = f"{token_symbol} is a solid, established cryptocurrency with neutral market sentiment. " \
                           f"In the absence of negative signals, established tokens often present accumulation opportunities. " \
                           f"Consider dollar-cost averaging strategy with risk management."
                price_target = 100 * 1.05  # Objectif conservateur
                stop_loss = 100 * 0.90
                
        elif any(token in token_lower for token in l2_tokens):
            # Token Layer 2 -> recommandation basée sur l'écosystème de scaling
            if sentiment == "positive" or sentiment_score >= 1:
                action = "buy"
                confidence = 0.70 + min(0.15, sentiment_score * 0.03)
                reasoning = f"{token_symbol} is part of the growing Layer 2/scaling ecosystem. " \
                           f"Positive sentiment suggests strong adoption potential. L2 tokens benefit " \
                           f"from Ethereum scaling narrative and increasing DeFi activity. Sentiment: +{sentiment_score}."
                price_target = 100 * (1.10 + sentiment_score * 0.02)
                stop_loss = 100 * 0.90
            elif sentiment == "negative":
                action = "hold"  # Plus conservateur pour L2 que pour majors
                confidence = 0.55
                reasoning = f"{token_symbol} represents Layer 2 infrastructure with current negative sentiment. " \
                           f"However, scaling solutions remain essential. Consider waiting for better entry " \
                           f"points rather than selling. Monitor ecosystem developments."
                price_target = None
                stop_loss = 100 * 0.85
            else:
                # Sentiment neutre pour L2 -> légèrement bullish à long terme
                action = "buy"
                confidence = 0.65
                reasoning = f"{token_symbol} represents Layer 2 scaling infrastructure. " \
                           f"Neutral sentiment with long-term bullish outlook as Ethereum scaling gains adoption. " \
                           f"L2 tokens are positioned to benefit from increasing network activity."
                price_target = 100 * 1.08
                stop_loss = 100 * 0.88
            
        else:
            # Token inconnu mais pas nécessairement suspect -> analyse plus nuancée
            if sentiment == "positive" and sentiment_score >= 2:
                action = "buy"
                confidence = 0.45  # Confiance modérée pour tokens inconnus même avec bon sentiment
                reasoning = f"{token_symbol} is not widely recognized in major rankings but shows strong positive sentiment. " \
                           f"Sentiment score: +{sentiment_score}. Could be an emerging opportunity, but requires caution. " \
                           f"Recommend small position size and thorough research on project fundamentals."
                price_target = 100 * 1.15  # Potentiel plus élevé pour tokens émergents
                stop_loss = 100 * 0.85  # Stop plus serré
            elif sentiment == "negative":
                action = "hold"  # Éviter de sell des tokens inconnus sans plus d'infos
                confidence = 0.35
                reasoning = f"{token_symbol} is not widely recognized and shows negative sentiment. " \
                           f"Insufficient data for confident sell recommendation. If holding, consider " \
                           f"exit strategy. If not holding, avoid entry until clearer information available."
                price_target = None
                stop_loss = 100 * 0.80
            else:
                # Sentiment neutre, token inconnu -> légère préférence hold avec recherche
                action = "hold"
                confidence = 0.40  # Confiance plus élevée qu'avant
                reasoning = f"{token_symbol} is not widely recognized in major cryptocurrency rankings. " \
                           f"Neutral sentiment suggests no immediate catalysts. Recommend thorough research " \
                           f"on project team, use case, tokenomics, and community before trading decisions. " \
                           f"Consider market cap, volume, and development activity."
                price_target = None
                stop_loss = 100 * 0.85
        
        # Détermination du sentiment final
        if sentiment_score >= 3:
            news_sentiment = "very_positive"
        elif sentiment_score >= 1:
            news_sentiment = "positive"
        elif sentiment_score <= -3:
            news_sentiment = "very_negative"
        elif sentiment_score <= -1:
            news_sentiment = "negative"
        else:
            news_sentiment = "neutral"
        
        return {
            "recommendation": action,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "price_target": round(price_target, 6) if price_target else None,
            "stop_loss": round(stop_loss, 6) if stop_loss else None,
            "news_sentiment": news_sentiment,
            "technical_levels": {
                "support": support,
                "resistance": resistance,
                "current_price": current_price,
                "volume_24h": volume_24h,
                "market_cap": market_cap
            },
            "market_analysis": {
                "price_change_24h": price_change_24h,
                "volatility": volatility,
                "sentiment_score": sentiment_score
            }
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur génération recommandation: {e}")
        return None

async def send_trading_recommendation_to_simon(ctx: Context, token_symbol: str, news_data: list = None):
    """Envoie une recommandation de trading avancée à Simon basée sur l'analyse de marché et les actualités"""
    
    try:
        ctx.logger.info(f"📊 Génération d'une recommandation de trading avancée pour {token_symbol}...")
        
        # Si pas de news fournie, récupérer les actualités récentes
        if news_data is None:
            news_data = await get_recent_news_context(ctx)
        
        # Récupérer les données de marché réelles
        market_data = await get_token_market_data(ctx, token_symbol)
        
        if market_data:
            ctx.logger.info(f"💰 Données de marché pour {token_symbol}: ${market_data['price_usd']:.4f} "
                           f"({market_data['price_change_24h']:+.2f}%)")
            
            # Analyser les niveaux techniques
            technical_levels = await analyze_technical_levels(
                ctx, token_symbol, 
                market_data['price_usd'], 
                market_data['price_change_24h']
            )
            
            # Générer une recommandation intelligente
            recommendation = await generate_smart_recommendation(
                ctx, token_symbol, market_data, news_data, technical_levels
            )
            
            if recommendation:
                # Créer la recommandation pour Simon
                trading_rec = TradingRecommendation(
                    token_symbol=token_symbol,
                    recommendation=recommendation["recommendation"],
                    confidence=recommendation["confidence"],
                    reasoning=recommendation["reasoning"],
                    price_target=recommendation["price_target"],
                    stop_loss=recommendation["stop_loss"],
                    news_sentiment=recommendation["news_sentiment"],
                    timestamp=datetime.now().isoformat()
                )
                
                # Envoyer à Simon
                await ctx.send(SIMON_AGENT_ADDRESS, trading_rec)
                ctx.logger.info(f"📤 Recommandation avancée envoyée à Simon pour {token_symbol}")
                
                return recommendation
        
        # Fallback vers l'ancien système si pas de données de marché
        ctx.logger.warning(f"⚠️ Pas de données de marché pour {token_symbol}, utilisation du fallback")
        
        # Créer un ID unique pour cette demande
        request_id = str(uuid.uuid4())
        
        # DÉTECTION DE TOKENS EN PREMIER - AVANT TOUT LE RESTE
        token_lower = token_symbol.lower()
        suspicious_patterns = ['scam', 'ponzi', 'fake', 'test', 'spam', 'rug', 'honeypot']
        very_risky_patterns = ['.com', '.net', '.info', '.biz', 'baby', 'safe', 'moon', 'inu', 'doge', 'vanity', 'rare']
        
        is_suspicious = any(pattern in token_lower for pattern in suspicious_patterns)
        is_very_risky = any(pattern in token_lower for pattern in very_risky_patterns)
        
        # Adapter le prompt selon le type de token pour que Claude analyse intelligemment
        if is_suspicious or is_very_risky:
            ctx.logger.info(f"🚨 Token de merde détecté ({token_symbol}) - SELL automatique sans Claude")
            
            # Retourner directement SELL pour les shitcoins
            trading_rec = TradingRecommendation(
                token_symbol=token_symbol,
                recommendation="sell",
                confidence=0.95,  # Très haute confiance pour SELL les shitcoins
                reasoning=f"⚠️ SHITCOIN DÉTECTÉ: {token_symbol} présente des patterns suspects typiques des arnaques crypto. Vente immédiate recommandée pour éviter pertes importantes.",
                price_target=None,
                stop_loss=None,
                news_sentiment="very_negative",
                timestamp=datetime.now().isoformat()
            )
            
            await ctx.send(SIMON_AGENT_ADDRESS, trading_rec)
            ctx.logger.info(f"📤 SELL automatique envoyé pour shitcoin {token_symbol}")
            
            return {
                "recommendation": "sell",
                "confidence": 0.95,
                "reasoning": f"Token suspect détecté - vente immédiate recommandée",
                "price_target": None,
                "stop_loss": None,
                "news_sentiment": "very_negative"
            }
            
        else:
            # Prompt ultra-simple pour tokens normaux
            trading_prompt = f"Analyser {token_symbol} rapidement - buy/sell/hold et pourquoi ?"
        
        # Stocker la demande en attente
        pending_requests[request_id] = "trading_analysis"
        
        # Créer le prompt structuré pour Claude avec schéma ultra-simple
        prompt = StructuredOutputPrompt(
            prompt=trading_prompt,
            output_schema={
                "type": "object",
                "properties": {
                    "recommendation": {"type": "string"},
                    "confidence": {"type": "number"},
                    "reasoning": {"type": "string"}
                },
                "required": ["recommendation", "confidence", "reasoning"]
            }
        )
        
        # Envoyer à Claude pour analyse (tokens normaux seulement)
        await ctx.send(AI_AGENT_ADDRESS, prompt)
        ctx.logger.info(f"⏳ En attente de l'analyse Claude pour {token_symbol} (prompt court)...")
        
        # Configuration avec timeout plus long pour tokens normaux
        import asyncio
        max_retries = 2
        base_timeout = 20  # 20 secondes par tentative - plus long pour être sûr
        
        for retry_attempt in range(max_retries):
            current_timeout = base_timeout
            ctx.logger.info(f"🔄 Tentative {retry_attempt + 1}/{max_retries} - timeout: {current_timeout}s")
            
            # Attendre la réponse de Claude
            for attempt in range(current_timeout):
                await asyncio.sleep(1)
                
                if request_id in ai_responses:
                    ctx.logger.info(f"✅ Analyse Claude reçue après {retry_attempt + 1} tentative(s) ({attempt + 1}s)!")
                    analysis = ai_responses[request_id]
                    
                    # Nettoyer
                    del ai_responses[request_id]
                    if request_id in pending_requests:
                        del pending_requests[request_id]
                    
                    # Créer la recommandation pour Simon avec valeurs par défaut pour schéma simplifié
                    trading_rec = TradingRecommendation(
                        token_symbol=token_symbol,
                        recommendation=analysis.get("recommendation", "hold"),
                        confidence=analysis.get("confidence", 0.5),
                        reasoning=analysis.get("reasoning", "Analyse basée sur les actualités récentes"),
                        price_target=None,  # Pas de price_target dans le schéma simplifié
                        stop_loss=None,     # Pas de stop_loss dans le schéma simplifié
                        news_sentiment="neutral",  # Pas de sentiment dans le schéma simplifié
                        timestamp=datetime.now().isoformat()
                    )
                    
                    # Envoyer à Simon
                    await ctx.send(SIMON_AGENT_ADDRESS, trading_rec)
                    ctx.logger.info(f"📤 Recommandation Claude envoyée à Simon pour {token_symbol}: {analysis.get('recommendation')} ({analysis.get('confidence', 0)*100:.0f}%)")
                    
                    return analysis
            
            # Si pas de réponse, retry (sauf dernière tentative)
            if retry_attempt < max_retries - 1:
                ctx.logger.warning(f"⏰ Timeout tentative {retry_attempt + 1} - retry dans 3s...")
                await asyncio.sleep(3)
                
                # Renvoyer la requête pour retry
                try:
                    await ctx.send(AI_AGENT_ADDRESS, prompt)
                    ctx.logger.info(f"🔄 Requête renvoyée à Claude (retry {retry_attempt + 2})")
                except Exception as retry_error:
                    ctx.logger.error(f"❌ Erreur lors du retry: {retry_error}")

        # Timeout final - Claude ne répond pas
        ctx.logger.warning(f"⏰ Claude ne répond pas pour {token_symbol} après {max_retries} tentatives - Fallback intelligent")
        
        # Analyser le token pour générer une recommandation intelligente
        major_tokens = ['eth', 'ethereum', 'btc', 'bitcoin', 'usdc', 'usdt', 'bnb', 'ada', 'cardano', 
                       'sol', 'solana', 'matic', 'polygon', 'avax', 'avalanche', 'dot', 'polkadot', 
                       'link', 'chainlink', 'uni', 'uniswap', 'atom', 'cosmos', 'algo', 'algorand',
                       'xrp', 'ripple', 'ltc', 'litecoin', 'bch', 'bitcoin cash', 'xlm', 'stellar']
        
        l2_tokens = ['arb', 'arbitrum', 'op', 'optimism', 'flow', 'immx', 'immutable',
                    'zksync', 'zk', 'metis', 'boba', 'loopring', 'lrc', 'base', 'mantle', 'mnt']
        
        defi_tokens = ['uni', 'uniswap', 'sushi', 'sushiswap', 'aave', 'comp', 'compound', 'mkr', 'maker', 
                      'crv', 'curve', 'bal', 'balancer', 'snx', 'synthetix', 'ren', 'republic', 'yfi', 'yearn']
        
        # Analyser le sentiment des news
        sentiment = "neutral"
        sentiment_score = 0
        
        if news_data:
            positive_words = ['bullish', 'gain', 'positive', 'up', 'growth', 'partnership', 'adoption', 'upgrade']
            negative_words = ['bearish', 'loss', 'negative', 'down', 'crash', 'hack', 'regulation', 'ban']
            
            total_score = 0
            for article in news_data[:10]:
                title_content = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                pos_count = sum(1 for word in positive_words if word in title_content)
                neg_count = sum(1 for word in negative_words if word in title_content)
                total_score += pos_count - neg_count
            
            sentiment_score = total_score
            if total_score >= 3:
                sentiment = "positive"
            elif total_score <= -3:
                sentiment = "negative"
        
        # Logique de fallback selon le type de token
        if any(token_lower == t or token_lower in t for t in major_tokens):
            # Token majeur - recommandation optimiste avec Claude timeout
            action = "buy" if sentiment_score >= 0 else "hold"
            confidence = 0.60
            reasoning = f"{token_symbol} is a well-established cryptocurrency. Claude analysis timeout, " \
                       f"but fundamental strength suggests opportunity. Conservative approach recommended. " \
                       f"Sentiment: {sentiment} (score: {sentiment_score})"
            price_target = 100 * 1.05 if action == "buy" else None
            stop_loss = 100 * 0.90
            
        elif any(token_lower == t or token_lower in t for t in l2_tokens + defi_tokens):
            # Token DeFi/L2 établi
            action = "hold"
            confidence = 0.55
            reasoning = f"{token_symbol} is part of established DeFi/L2 ecosystem. " \
                       f"Claude timeout prevented detailed analysis. Conservative hold recommended " \
                       f"until system recovery. Sentiment: {sentiment}"
            price_target = None
            stop_loss = 100 * 0.87
            
        else:
            # Token inconnu - très conservateur
            action = "hold"
            confidence = 0.35
            reasoning = f"{token_symbol} is not widely recognized. Claude timeout prevented " \
                       f"comprehensive analysis. Recommend thorough research before trading decisions. " \
                       f"Avoid major positions until verified analysis available."
            price_target = None
            stop_loss = 100 * 0.85
        
        # Créer recommandation de fallback intelligente
        fallback_rec = TradingRecommendation(
            token_symbol=token_symbol,
            recommendation=action,
            confidence=confidence,
            reasoning=reasoning,
            price_target=price_target,
            stop_loss=stop_loss,
            news_sentiment=sentiment,
            timestamp=datetime.now().isoformat()
        )
        
        await ctx.send(SIMON_AGENT_ADDRESS, fallback_rec)
        ctx.logger.info(f"📤 Recommandation intelligente pour {token_symbol}: {action} ({confidence:.0%}) - {'⚠️ SUSPECT' if is_suspicious else '✅ Analysé'}")
        
        return {
            "recommendation": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "price_target": price_target,
            "stop_loss": stop_loss,
            "news_sentiment": sentiment
        }
        
    except Exception as e:
        # Gestion d'erreur améliorée avec fallback de sécurité
        ctx.logger.error(f"❌ Erreur critique lors de l'analyse de {token_symbol}: {e}")
        
        # Créer une recommandation de sécurité ultra-conservative
        emergency_rec = TradingRecommendation(
            token_symbol=token_symbol,
            recommendation="hold",
            confidence=0.05,
            reasoning=f"⚠️ ERREUR SYSTÈME: Analyse impossible due à une erreur technique: {str(e)}. " \
                     f"Recommandation de sécurité ultra-conservative. Ne pas trader jusqu'à résolution " \
                     f"du problème technique. Vérifier la connectivité et l'état du système.",
            price_target=None,
            stop_loss=100 * 0.75,  # Stop loss de sécurité
            news_sentiment="neutral",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Essayer d'envoyer la recommandation d'urgence
            await ctx.send(SIMON_AGENT_ADDRESS, emergency_rec)
            ctx.logger.info(f"🚨 Recommandation d'urgence envoyée pour {token_symbol}")
        except Exception as send_error:
            ctx.logger.error(f"❌ Impossible d'envoyer la recommandation d'urgence: {send_error}")
        
        return {
            "recommendation": "hold",
            "confidence": 0.05,
            "reasoning": f"Erreur système: {str(e)}. Analyse impossible.",
            "price_target": None,
            "stop_loss": 100 * 0.75,
            "news_sentiment": "neutral",
            "error": str(e)
        }


async def get_recent_news_context(ctx: Context):
    """Récupère le contexte des actualités récentes depuis le fichier news"""
    try:
        if os.path.exists(NEWS_FILE):
            with open(NEWS_FILE, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
                return news_data.get('articles', [])
        else:
            ctx.logger.warning(f"⚠️ Fichier d'actualités {NEWS_FILE} non trouvé")
            return []
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la lecture des actualités: {e}")
        return []


@agent.on_rest_post("/trading/recommend", TradingAnalysisRequest, TradingAnalysisAPIResponse)
async def request_trading_recommendation(ctx: Context, req: TradingAnalysisRequest) -> TradingAnalysisAPIResponse:
    """Endpoint pour demander une recommandation de trading"""
    
    ctx.logger.info(f"🌐 API Call - Recommandation de trading pour {req.token_symbol}")
    
    try:
        # Validation du token - accepter tous les tokens maintenant
        # Les tokens valides sont ceux que l'utilisateur possède dans son wallet
        if not req.token_symbol or len(req.token_symbol.strip()) == 0:
            return TradingAnalysisAPIResponse(
                success=False,
                message="Le symbole du token est requis",
                timestamp=datetime.now().isoformat()
            )
        
        ctx.logger.info(f"🎯 Génération de recommandation pour {req.token_symbol} (token du wallet)")
        
        # Générer la recommandation
        result = await send_trading_recommendation_to_simon(ctx, req.token_symbol)
        
        if result:
            # Convertir l'analyse en recommandation pour le front-end
            action_mapping = {
                "buy": "ACHETER",
                "sell": "VENDRE", 
                "hold": "CONSERVER"
            }
            
            recommendation = TradingRecommendation(
                token_symbol=req.token_symbol,
                recommendation=action_mapping.get(result.get("recommendation", "hold"), "CONSERVER"),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "Analyse basée sur les actualités récentes"),
                price_target=result.get("price_target"),
                stop_loss=result.get("stop_loss"),
                news_sentiment=result.get("news_sentiment", "neutral"),
                timestamp=datetime.now().isoformat()
            )
            
            return TradingAnalysisAPIResponse(
                success=True,
                message=f"Recommandation générée pour {req.token_symbol}",
                analysis={
                    "action": recommendation.recommendation,
                    "confidence": recommendation.confidence,
                    "reasoning": recommendation.reasoning,
                    "token": recommendation.token_symbol,
                    "timestamp": recommendation.timestamp,
                    "news_sentiment": recommendation.news_sentiment,
                    "price_target": recommendation.price_target,
                    "stop_loss": recommendation.stop_loss,
                    "market_context": result.get("market_context", {
                        "current_price": result.get("market_data", {}).get("current_price", 0),
                        "trend": result.get("market_data", {}).get("technical_analysis", {}).get("trend", "unknown"),
                        "support": result.get("market_data", {}).get("technical_analysis", {}).get("support_level", 0),
                        "resistance": result.get("market_data", {}).get("technical_analysis", {}).get("resistance_level", 0)
                    }) if result.get("market_data") else None
                },
                timestamp=datetime.now().isoformat()
            )
        else:
            return TradingAnalysisAPIResponse(
                success=False,
                message="Erreur lors de la génération de la recommandation",
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur API trading: {e}")
        return TradingAnalysisAPIResponse(
            success=False,
            message=f"Erreur: {str(e)}",
            timestamp=datetime.now().isoformat()
        )


# Gestionnaire pour les demandes d'analyse de trading venant de Simon
@agent.on_message(TradingAnalysisRequest)
async def handle_trading_analysis_request(ctx: Context, sender: str, msg: TradingAnalysisRequest):
    """Traite les demandes d'analyse de trading venant de Simon"""
    
    ctx.logger.info(f"📥 Demande d'analyse de trading reçue de Simon pour {msg.token_symbol}")
    
    try:
        # Envoyer une recommandation basée sur les actualités actuelles
        result = await send_trading_recommendation_to_simon(ctx, msg.token_symbol, None)
        
        if result:
            ctx.logger.info(f"✅ Recommandation générée et envoyée pour {msg.token_symbol}")
        else:
            ctx.logger.error(f"❌ Échec de la génération de recommandation pour {msg.token_symbol}")
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors du traitement de la demande de Simon: {e}")


# Gestionnaire pour confirmer la réception des TradingRecommendation par Simon
@simon_protocol.on_message(model=TradingRecommendation)
async def handle_trading_recommendation_confirmation(ctx: Context, sender: str, msg: TradingRecommendation):
    """Gestionnaire pour confirmer la réception des recommandations de trading par Simon"""
    ctx.logger.info(f"✅ Confirmation: Recommandation de trading bien reçue par Simon pour {msg.token_symbol}")
    ctx.logger.info(f"   Action: {msg.recommendation}, Confidence: {msg.confidence:.0%}")


# Fonction d'analyse de marché avancée
async def get_advanced_market_analysis(token_symbol: str) -> dict:
    """
    Récupère des données de marché réelles et effectue une analyse technique avancée
    """
    try:
        # Mapping des symboles vers les IDs CoinGecko
        token_mapping = {
            'ETH': 'ethereum',
            'BTC': 'bitcoin',
            'MATIC': 'matic-network',
            'USDC': 'usd-coin',
            'USDT': 'tether',
            'ARB': 'arbitrum',
            'OP': 'optimism',
            'AVAX': 'avalanche-2',
            'DOT': 'polkadot',
            'ADA': 'cardano',
            'SOL': 'solana',
            'LINK': 'chainlink',
            'UNI': 'uniswap'
        }
        
        coingecko_id = token_mapping.get(token_symbol.upper(), token_symbol.lower())
        
        async with aiohttp.ClientSession() as session:
            # 1. Prix actuel et données de base
            base_url = f"https://api.coingecko.com/api/v3/simple/price"
            base_params = {
                'ids': coingecko_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            async with session.get(base_url, params=base_params) as response:
                if response.status != 200:
                    raise Exception(f"CoinGecko API error: {response.status}")
                basic_data = await response.json()
            
            # 2. Données historiques pour l'analyse technique
            history_url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
            history_params = {
                'vs_currency': 'usd',
                'days': '30'  # 30 jours de données
            }
            
            async with session.get(history_url, params=history_params) as response:
                if response.status != 200:
                    # Si échec, continuer avec données de base uniquement
                    history_data = None
                else:
                    history_data = await response.json()
        
        # Analyser les données de base
        if coingecko_id not in basic_data:
            raise Exception(f"Token {token_symbol} not found on CoinGecko")
        
        token_data = basic_data[coingecko_id]
        current_price = token_data['usd']
        price_change_24h = token_data.get('usd_24h_change', 0)
        volume_24h = token_data.get('usd_24h_vol', 0)
        market_cap = token_data.get('usd_market_cap', 0)
        
        # Analyse technique si données historiques disponibles
        technical_analysis = {}
        if history_data and 'prices' in history_data:
            prices = [price[1] for price in history_data['prices']]
            
            # Support et résistance (niveaux significatifs)
            support_level = min(prices[-7:])  # Support des 7 derniers jours
            resistance_level = max(prices[-7:])  # Résistance des 7 derniers jours
            
            # Moyennes mobiles
            ma_7 = statistics.mean(prices[-7:]) if len(prices) >= 7 else current_price
            ma_14 = statistics.mean(prices[-14:]) if len(prices) >= 14 else current_price
            ma_30 = statistics.mean(prices) if len(prices) >= 30 else current_price
            
            # Volatilité (écart-type des prix)
            volatility = statistics.stdev(prices[-14:]) if len(prices) >= 14 else 0
            
            # Tendance (comparaison des moyennes mobiles)
            if ma_7 > ma_14 > ma_30:
                trend = "bullish"
            elif ma_7 < ma_14 < ma_30:
                trend = "bearish"
            else:
                trend = "sideways"
            
            # Position actuelle par rapport aux niveaux
            position_vs_support = (current_price - support_level) / support_level * 100
            position_vs_resistance = (resistance_level - current_price) / current_price * 100
            
            technical_analysis = {
                'support_level': round(support_level, 4),
                'resistance_level': round(resistance_level, 4),
                'ma_7': round(ma_7, 4),
                'ma_14': round(ma_14, 4),
                'ma_30': round(ma_30, 4),
                'volatility': round(volatility, 4),
                'trend': trend,
                'position_vs_support': round(position_vs_support, 2),
                'position_vs_resistance': round(position_vs_resistance, 2)
            }
        
        # Calculer des prix cibles basés sur l'analyse technique
        price_targets = calculate_price_targets(current_price, technical_analysis, price_change_24h)
        
        return {
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'volume_24h': volume_24h,
            'market_cap': market_cap,
            'technical_analysis': technical_analysis,
            'price_targets': price_targets,
            'data_quality': 'high' if history_data else 'basic'
        }
        
    except Exception as e:
        # Fallback avec des données simulées réalistes
        return generate_fallback_market_data(token_symbol, str(e))

def calculate_price_targets(current_price: float, technical_analysis: dict, price_change_24h: float) -> dict:
    """
    Calcule des prix cibles basés sur l'analyse technique
    """
    targets = {}
    
    if technical_analysis:
        support = technical_analysis.get('support_level', current_price * 0.95)
        resistance = technical_analysis.get('resistance_level', current_price * 1.05)
        trend = technical_analysis.get('trend', 'sideways')
        volatility = technical_analysis.get('volatility', current_price * 0.02)
        
        # Prix cibles basés sur la tendance et les niveaux techniques
        if trend == "bullish":
            # En tendance haussière, viser la résistance + extension
            targets['buy_target'] = round(current_price * 0.98, 4)  # Légèrement en dessous du prix actuel
            targets['sell_target'] = round(resistance * 1.02, 4)    # Au-dessus de la résistance
            targets['stop_loss_buy'] = round(support * 0.98, 4)     # En dessous du support
            targets['stop_loss_sell'] = round(current_price * 1.05, 4)  # Stop serré pour les ventes
            
        elif trend == "bearish":
            # En tendance baissière, viser le support
            targets['sell_target'] = round(current_price * 1.02, 4)  # Légèrement au-dessus du prix actuel
            targets['buy_target'] = round(support * 0.98, 4)         # Près du support
            targets['stop_loss_sell'] = round(current_price * 0.95, 4)  # Stop serré pour les achats
            targets['stop_loss_buy'] = round(support * 0.95, 4)      # En dessous du support
            
        else:  # sideways
            # En range, jouer les bornes
            targets['buy_target'] = round(support * 1.01, 4)         # Près du support
            targets['sell_target'] = round(resistance * 0.99, 4)     # Près de la résistance
            targets['stop_loss_buy'] = round(support * 0.97, 4)      # En dessous du support
            targets['stop_loss_sell'] = round(resistance * 1.03, 4)  # Au-dessus de la résistance
    
    else:
        # Fallback basé sur le prix actuel et le momentum
        momentum_factor = 1 + (price_change_24h / 100) * 0.5  # Facteur basé sur le mouvement 24h
        
        targets['buy_target'] = round(current_price * 0.97, 4)
        targets['sell_target'] = round(current_price * momentum_factor * 1.05, 4)
        targets['stop_loss_buy'] = round(current_price * 0.92, 4)
        targets['stop_loss_sell'] = round(current_price * 1.08, 4)
    
    return targets

def generate_fallback_market_data(token_symbol: str, error_msg: str) -> dict:
    """
    Génère des données de marché de fallback réalistes
    """
    # Prix de base réalistes pour les tokens majeurs
    base_prices = {
        'ETH': 3200,
        'BTC': 65000,
        'MATIC': 0.85,
        'USDC': 1.0,
        'USDT': 1.0,
        'ARB': 1.2,
        'OP': 2.5,
        'AVAX': 35,
        'DOT': 6.5,
        'ADA': 0.45,
        'SOL': 140,
        'LINK': 15,
        'UNI': 8
    }
    
    base_price = base_prices.get(token_symbol.upper(), 1.0)
    
    return {
        'current_price': base_price,
        'price_change_24h': 0,
        'volume_24h': 0,
        'market_cap': 0,
        'technical_analysis': {},
        'price_targets': {
            'buy_target': round(base_price * 0.97, 4),
            'sell_target': round(base_price * 1.05, 4),
            'stop_loss_buy': round(base_price * 0.92, 4),
            'stop_loss_sell': round(base_price * 1.08, 4)
        },
        'data_quality': 'fallback',
        'error': error_msg
    }

async def generate_technical_fallback_recommendation(ctx: Context, token_symbol: str, market_analysis: Dict, news_data: list = None):
    """
    Génère une recommandation de fallback basée sur l'analyse technique et le sentiment news
    """
    try:
        ctx.logger.info(f"🔧 Génération de recommandation technique pour {token_symbol}")
        
        current_price = market_analysis.get('current_price', 1.0)
        price_change_24h = market_analysis.get('price_change_24h', 0)
        technical_analysis = market_analysis.get('technical_analysis', {})
        price_targets = market_analysis.get('price_targets', {})
        
        # Analyser le sentiment des news localement
        news_sentiment = analyze_news_sentiment(news_data)
        sentiment_score = get_sentiment_score(news_sentiment)
        
        # Déterminer la catégorie du token
        token_category = categorize_token(token_symbol)
        
        # Logique de recommandation basée sur l'analyse technique + sentiment
        if token_category == "suspicious":
            # Token suspect -> recommandation très prudente
            recommendation = {
                "recommendation": "hold",
                "confidence": 0.15,
                "reasoning": f"WARNING: {token_symbol} appears to be a high-risk or unknown token. Current price ${current_price:.4f}. "
                           f"Extremely low confidence due to limited data and potential risks. "
                           f"Recommend thorough research and extreme caution before any trading activity.",
                "price_target": None,
                "stop_loss": current_price * 0.9,
                "news_sentiment": "neutral"
            }
            
        elif token_category == "major":
            # Token majeur -> analyse technique poussée
            trend = technical_analysis.get('trend', 'sideways')
            support = technical_analysis.get('support_level', current_price * 0.95)
            resistance = technical_analysis.get('resistance_level', current_price * 1.05)
            
            if sentiment_score > 1 and price_change_24h > 3 and trend == "bullish":
                # Conditions très bullish
                recommendation = {
                    "recommendation": "buy",
                    "confidence": 0.82,
                    "reasoning": f"Strong bullish signals for {token_symbol}. Price ${current_price:.4f} with {price_change_24h:.2f}% gain "
                               f"in uptrend above support ${support:.4f}. Positive news sentiment reinforces technical breakout. "
                               f"Target resistance level ${resistance:.4f} with strong momentum.",
                    "price_target": resistance * 1.03,
                    "stop_loss": support * 0.98,
                    "news_sentiment": news_sentiment
                }
                
            elif sentiment_score < -1 and price_change_24h < -5 and trend == "bearish":
                # Conditions très bearish
                recommendation = {
                    "recommendation": "sell",
                    "confidence": 0.78,
                    "reasoning": f"Strong bearish signals for {token_symbol}. Price ${current_price:.4f} down {abs(price_change_24h):.2f}% "
                               f"in downtrend below resistance ${resistance:.4f}. Negative news compounds technical weakness. "
                               f"Target support level ${support:.4f} with selling pressure.",
                    "price_target": support * 0.97,
                    "stop_loss": resistance * 1.02,
                    "news_sentiment": news_sentiment
                }
                
            else:
                # Conditions neutres ou mixtes
                action = "buy" if sentiment_score > 0 and price_change_24h > 0 else "hold"
                conf_base = 0.65 if action == "buy" else 0.58
                
                recommendation = {
                    "recommendation": action,
                    "confidence": conf_base + (abs(sentiment_score) * 0.05),
                    "reasoning": f"Mixed signals for established token {token_symbol}. Price ${current_price:.4f} "
                               f"({'up' if price_change_24h > 0 else 'down'} {abs(price_change_24h):.2f}%) "
                               f"in {trend} trend between support ${support:.4f} and resistance ${resistance:.4f}. "
                               f"{'Positive' if sentiment_score > 0 else 'Neutral'} news sentiment suggests "
                               f"{'cautious accumulation' if action == 'buy' else 'holding current positions'}.",
                    "price_target": resistance * 0.99 if action == "buy" else None,
                    "stop_loss": support * 0.98,
                    "news_sentiment": news_sentiment
                }
                
        elif token_category == "l2":
            # Token Layer 2 -> analyse modérée
            recommendation = {
                "recommendation": "buy" if sentiment_score > 0 and price_change_24h > -2 else "hold",
                "confidence": 0.68 if sentiment_score > 0 else 0.52,
                "reasoning": f"Layer 2 ecosystem token {token_symbol} at ${current_price:.4f}. "
                           f"{'Growing adoption' if sentiment_score > 0 else 'Stable development'} "
                           f"with {'positive' if sentiment_score > 0 else 'neutral'} market sentiment. "
                           f"L2 tokens benefit from Ethereum scaling narrative.",
                "price_target": current_price * 1.08 if sentiment_score > 0 else None,
                "stop_loss": current_price * 0.92,
                "news_sentiment": news_sentiment
            }
            
        else:
            # Token inconnu -> prudence
            recommendation = {
                "recommendation": "hold",
                "confidence": 0.35,
                "reasoning": f"Unknown token {token_symbol} at ${current_price:.4f}. "
                           f"Limited market data and news coverage. "
                           f"Recommend thorough research before trading. "
                           f"Current sentiment: {news_sentiment}.",
                "price_target": None,
                "stop_loss": current_price * 0.88,
                "news_sentiment": news_sentiment
            }
        
        # Créer et envoyer la recommandation à Simon
        trading_rec = TradingRecommendation(
            token_symbol=token_symbol,
            recommendation=recommendation["recommendation"],
            confidence=recommendation["confidence"],
            reasoning=recommendation["reasoning"],
            price_target=recommendation["price_target"],
            stop_loss=recommendation["stop_loss"],
            news_sentiment=recommendation["news_sentiment"],
            timestamp=datetime.now().isoformat()
        )
        
        await ctx.send(SIMON_AGENT_ADDRESS, trading_rec)
        ctx.logger.info(f"📤 Recommandation technique envoyée pour {token_symbol}: {recommendation['recommendation'].upper()} ({recommendation['confidence']:.0%})")
        
        return recommendation
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la génération de recommandation technique: {e}")
        return {
            "recommendation": "hold",
            "confidence": 0.3,
            "reasoning": f"Error in analysis for {token_symbol}: {str(e)}",
            "price_target": None,
            "stop_loss": current_price * 0.9 if 'current_price' in locals() else None,
            "news_sentiment": "neutral"
        }

def analyze_news_sentiment(news_data: list) -> str:
    """Analyse le sentiment des actualités"""
    if not news_data:
        return "neutral"
    
    # Mots-clés positifs et négatifs
    positive_words = [
        "bull", "bullish", "rise", "gain", "pump", "moon", "growth", "surge", "rally", 
        "breakthrough", "adoption", "partnership", "upgrade", "innovation", "positive",
        "up", "high", "strong", "optimistic", "buy", "invest", "accumulate"
    ]
    
    negative_words = [
        "bear", "bearish", "fall", "loss", "dump", "crash", "decline", "drop", "sell",
        "weakness", "concern", "risk", "fear", "panic", "negative", "down", "low",
        "uncertain", "volatile", "correction", "pullback", "resistance"
    ]
    
    neutral_words = [
        "stable", "sideways", "range", "consolidation", "wait", "watch", "monitor",
        "unchanged", "flat", "pause", "consolidate"
    ]
    
    # Analyser le texte combiné
    all_text = " ".join([
        str(article.get("title", "")) + " " + str(article.get("content", ""))
        for article in news_data[:5]
    ]).lower()
    
    positive_count = sum(1 for word in positive_words if word in all_text)
    negative_count = sum(1 for word in negative_words if word in all_text)
    neutral_count = sum(1 for word in neutral_words if word in all_text)
    
    # Déterminer le sentiment dominant
    if positive_count > negative_count + neutral_count:
        return "very_positive" if positive_count > negative_count * 2 else "positive"
    elif negative_count > positive_count + neutral_count:
        return "very_negative" if negative_count > positive_count * 2 else "negative"
    else:
        return "neutral"

def get_sentiment_score(sentiment: str) -> int:
    """Convertit le sentiment en score numérique"""
    sentiment_scores = {
        "very_positive": 3,
        "positive": 1,
        "neutral": 0,
        "negative": -1,
        "very_negative": -3
    }
    return sentiment_scores.get(sentiment, 0)

def categorize_token(token_symbol: str) -> str:
    """Catégorise le token selon sa réputation et son écosystème"""
    token_lower = token_symbol.lower()
    
    # Tokens majeurs bien établis
    major_tokens = ['eth', 'ethereum', 'btc', 'bitcoin', 'usdc', 'usdt', 'bnb', 'ada', 'sol', 'matic', 'avax', 'dot', 'link', 'uni']
    
    # Tokens Layer 2 et écosystème
    l2_tokens = ['arb', 'arbitrum', 'op', 'optimism', 'polygon', 'base']
    
    # Patterns suspects
    suspicious_patterns = ['.io', '.org', '.com', 'tron', 'trx', 'rare', 'vanity', 'scam', 'moon', 'safe', 'baby', 'doge', 'shib']
    
    if any(pattern in token_lower for pattern in suspicious_patterns):
        return "suspicious"
    elif any(token in token_lower for token in major_tokens):
        return "major"
    elif any(token in token_lower for token in l2_tokens):
        return "l2"
    else:
        return "unknown"

if __name__ == "__main__":
    logger.info("🔄 Démarrage de l'agent Intellect...")
    logger.info(f"🌐 Endpoints disponibles:")
    logger.info(f"   POST http://localhost:8000/trading/recommend  🆕")
    logger.info(f"   GET http://localhost:8000/health - Santé de l'agent")
    logger.info(f"🤖 Communication avec Simon Agent: {SIMON_AGENT_ADDRESS}")
    
    agent.run()