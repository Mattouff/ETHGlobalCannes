import json
import uuid
from datetime import datetime
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_analysis_to_file(token: str, analysis: dict):
    """Sauvegarde l'analyse dans un fichier JSON"""
    try:
        filename = f"market_analysis_{token.lower()}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Analyse sauvegardée dans {filename}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde de l'analyse: {e}")

def save_trading_recommendation_to_file(token: str, recommendation: dict):
    """Sauvegarde la recommandation de trading dans un fichier JSON"""
    try:
        filename = f"trading_recommendation_{token.lower()}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recommendation, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Recommandation de trading sauvegardée dans {filename}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde de la recommandation: {e}")

# Créer l'agent Intellect (qui agrège les données)
simon = Agent(
    name="simon",
    seed="intellect_secret_seed_phrase_2024", 
    port=8003,
    endpoint=["http://localhost:8003/submit"]
)

fund_agent_if_low(simon.wallet.address())

# Adresses des agents
SIMON_AGENT_ADDRESS = "agent1q0q5rqwj7q4upgm7fwf4dmv675nl4nqgy9tgp3qgyn8wlxwz804pxuj7032"
NEWS_AGENT_ADDRESS = "agent1qvd8tt75720p60aggzlna7rep89rmadhrt67cllz486w4y6www06vquhcca"  # Votre agent news local

# Créer des protocoles pour la communication
communication_protocol = Protocol("IntellectCommunication")

# Modèles de données pour la communication
class TokenAnalysisRequest(Model):
    token_symbol: str
    analysis_type: str = "market_analysis"
    timestamp: str

class TokenAnalysisResponse(Model):
    token_symbol: str
    price: float = None
    price_change_24h: float = None
    market_cap: float = None
    volume_24h: float = None
    analysis: str
    sentiment: str = "neutral"  # positive, negative, neutral
    recommendation: str = "hold"  # buy, sell, hold
    timestamp: str
    confidence_score: float = 0.0

class TradingRecommendation(Model):
    token_symbol: str
    recommendation: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    price_target: float = None
    stop_loss: float = None
    news_sentiment: str  # "positive", "negative", "neutral"
    timestamp: str

class GeneralMessage(Model):
    message: str
    sender: str = "simon"
    timestamp: str

class MarketDataRequest(Model):
    tokens: list[str]
    request_id: str

class MarketDataResponse(Model):
    request_id: str
    analyses: list[TokenAnalysisResponse]
    timestamp: str
    total_tokens: int

class HealthResponse(Model):
    status: str
    agent: str
    address: str
    timestamp: str

class AnalysisRequestResponse(Model):
    success: bool
    message: str
    token: str
    timestamp: str

class ErrorResponse(Model):
    success: bool
    error: str
    timestamp: str

class TokenDataResponse(Model):
    success: bool
    data: dict = None
    message: str = None
    timestamp: str

class SupportedTokensResponse(Model):
    supported_tokens: list[str]
    count: int
    timestamp: str

# Stockage des analyses reçues
market_analyses = {}
pending_requests = {}

# Tokens supportés
SUPPORTED_TOKENS = ["ETH", "BASE", "FLOW"]

def is_valid_token(token: str) -> bool:
    """Vérifie si le token est supporté"""
    return token.upper() in SUPPORTED_TOKENS

async def request_token_analysis(ctx: Context, token_symbol: str) -> str:
    """Demande une analyse de marché pour un token spécifique à Simon"""
    try:
        token_symbol = token_symbol.upper()
        if not is_valid_token(token_symbol):
            return f"Token {token_symbol} non supporté. Tokens supportés: {', '.join(SUPPORTED_TOKENS)}"

        request_id = str(uuid.uuid4())
        request = TokenAnalysisRequest(
            token_symbol=token_symbol,
            analysis_type="market_analysis",
            timestamp=datetime.now().isoformat()
        )
        
        # Stocker la demande en attente
        pending_requests[request_id] = {
            "token": token_symbol,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        ctx.logger.info(f"📤 Envoi de la demande d'analyse pour {token_symbol} à Simon...")
        
        # Envoyer la demande à Simon en utilisant ctx.send
        await ctx.send(SIMON_AGENT_ADDRESS, request)
        
        return f"Demande d'analyse envoyée pour {token_symbol} (ID: {request_id})"
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de l'envoi de la demande: {e}")
        return f"Erreur lors de la demande d'analyse: {str(e)}"

# Gestionnaire pour recevoir les analyses de Simon
@communication_protocol.on_message(model=TokenAnalysisResponse)
async def handle_analysis_response(ctx: Context, sender: str, msg: TokenAnalysisResponse):
    """Traite les réponses d'analyse reçues de Simon"""
    try:
        ctx.logger.info(f"📥 Analyse reçue de Simon pour {msg.token_symbol}")
        
        # Stocker l'analyse
        market_analyses[msg.token_symbol] = {
            "token_symbol": msg.token_symbol,
            "price": msg.price,
            "price_change_24h": msg.price_change_24h,
            "market_cap": msg.market_cap,
            "volume_24h": msg.volume_24h,
            "analysis": msg.analysis,
            "sentiment": msg.sentiment,
            "recommendation": msg.recommendation,
            "confidence_score": msg.confidence_score,
            "timestamp": msg.timestamp,
            "received_at": datetime.now().isoformat()
        }
        
        # Log de l'analyse reçue
        ctx.logger.info(f"✅ Analyse stockée pour {msg.token_symbol}:")
        ctx.logger.info(f"   Prix: ${msg.price}")
        ctx.logger.info(f"   Changement 24h: {msg.price_change_24h}%")
        ctx.logger.info(f"   Sentiment: {msg.sentiment}")
        ctx.logger.info(f"   Recommandation: {msg.recommendation}")
        
        # Sauvegarder dans un fichier JSON
        save_analysis_to_file(msg.token_symbol, market_analyses[msg.token_symbol])
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors du traitement de l'analyse: {e}")

# Gestionnaire pour recevoir les recommandations de trading d'Intellect
@communication_protocol.on_message(model=TradingRecommendation)
async def handle_trading_recommendation(ctx: Context, sender: str, msg: TradingRecommendation):
    """Traite les recommandations de trading reçues d'Intellect"""
    try:
        ctx.logger.info(f"🎯 Recommandation de trading reçue pour {msg.token_symbol}")
        
        # Analyser la recommandation
        risk_level = "LOW" if msg.confidence >= 0.7 else "MEDIUM" if msg.confidence >= 0.4 else "HIGH"
        confidence_pct = int(msg.confidence * 100)
        
        # Log détaillé de la recommandation
        ctx.logger.info("=" * 60)
        ctx.logger.info(f"🎯 TOKEN: {msg.token_symbol}")
        ctx.logger.info(f"📊 ACTION: {msg.recommendation.upper()}")
        ctx.logger.info(f"💪 CONFIDENCE: {confidence_pct}% ({risk_level} risk)")
        ctx.logger.info(f"💭 REASONING: {msg.reasoning[:100]}{'...' if len(msg.reasoning) > 100 else ''}")
        ctx.logger.info(f"📈 SENTIMENT: {msg.news_sentiment}")
        
        if msg.price_target:
            ctx.logger.info(f"🎯 TARGET PRICE: ${msg.price_target:.2f}")
        if msg.stop_loss:
            ctx.logger.info(f"🛑 STOP LOSS: ${msg.stop_loss:.2f}")
        
        ctx.logger.info("=" * 60)
        
        # Stocker la recommandation de trading
        trading_recommendation = {
            "token_symbol": msg.token_symbol,
            "action": msg.recommendation,
            "confidence": msg.confidence,
            "confidence_level": risk_level,
            "reasoning": msg.reasoning,
            "news_sentiment": msg.news_sentiment,
            "price_target": msg.price_target,
            "stop_loss": msg.stop_loss,
            "timestamp": msg.timestamp,
            "received_at": datetime.now().isoformat()
        }
        
        # Sauvegarder la recommandation
        save_trading_recommendation_to_file(msg.token_symbol, trading_recommendation)
        
        # Si c'est un token suspect (très faible confiance), log d'avertissement
        if msg.confidence <= 0.2:
            ctx.logger.warning(f"⚠️ HIGH RISK TOKEN DETECTED: {msg.token_symbol}")
            ctx.logger.warning(f"   Very low confidence ({confidence_pct}%) suggests suspicious token")
            ctx.logger.warning(f"   Action: {msg.recommendation.upper()} - PROCEED WITH EXTREME CAUTION")
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors du traitement de la recommandation: {e}")

# Gestionnaire pour les messages de type général dans le protocole
@communication_protocol.on_message(model=GeneralMessage)
async def handle_general_message_protocol(ctx: Context, sender: str, msg: GeneralMessage):
    """Gestionnaire pour les messages texte généraux dans le protocole"""
    ctx.logger.info(f"📨 Message protocole reçu de {sender}: {msg.message}")

# Gestionnaire pour les demandes d'analyse en écho (cas de test)
@communication_protocol.on_message(model=TokenAnalysisRequest)
async def handle_analysis_request_echo(ctx: Context, sender: str, msg: TokenAnalysisRequest):
    """Gestionnaire pour les demandes d'analyse en écho (cas de test)"""
    ctx.logger.info(f"🔄 Echo de demande d'analyse reçue de {sender} pour {msg.token_symbol}")

# Inclure le protocole dans l'agent
simon.include(communication_protocol)

# Endpoint REST pour demander une analyse
@simon.on_rest_post("/analyze", TokenAnalysisRequest, AnalysisRequestResponse)
async def request_analysis_endpoint(ctx: Context, req: TokenAnalysisRequest) -> AnalysisRequestResponse:
    """Endpoint REST pour demander une analyse de token"""
    try:
        result = await request_token_analysis(ctx, req.token_symbol)
        return AnalysisRequestResponse(
            success=True,
            message=result,
            token=req.token_symbol.upper(),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        ctx.logger.error(f"❌ Erreur endpoint analyze: {e}")
        return AnalysisRequestResponse(
            success=False,
            message=f"Erreur: {str(e)}",
            token=req.token_symbol.upper(),
            timestamp=datetime.now().isoformat()
        )

# Endpoint REST pour récupérer les analyses stockées
@simon.on_rest_get("/market_data", MarketDataResponse)
async def get_market_data(ctx: Context) -> MarketDataResponse:
    """Retourne toutes les analyses de marché stockées"""
    try:
        analyses_list = []
        for token, analysis in market_analyses.items():
            analyses_list.append(TokenAnalysisResponse(**analysis))
        
        response = MarketDataResponse(
            request_id=str(uuid.uuid4()),
            analyses=analyses_list,
            timestamp=datetime.now().isoformat(),
            total_tokens=len(analyses_list)
        )
        
        ctx.logger.info(f"📊 Retour de {len(analyses_list)} analyses de marché")
        return response
        
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération des données: {e}")
        return MarketDataResponse(
            request_id=str(uuid.uuid4()),
            analyses=[],
            timestamp=datetime.now().isoformat(),
            total_tokens=0
        )

# Endpoint REST pour récupérer l'analyse d'un token spécifique
@simon.on_rest_get("/market_data/{token}", TokenDataResponse)
async def get_token_analysis(ctx: Context, token: str) -> TokenDataResponse:
    """Retourne l'analyse d'un token spécifique"""
    try:
        token = token.upper()
        
        if token in market_analyses:
            analysis = market_analyses[token]
            ctx.logger.info(f"📈 Retour de l'analyse pour {token}")
            return TokenDataResponse(
                success=True,
                data=analysis,
                timestamp=datetime.now().isoformat()
            )
        else:
            # Si pas d'analyse stockée, en demander une nouvelle
            result = await request_token_analysis(ctx, token)
            return TokenDataResponse(
                success=False,
                message=f"Aucune analyse trouvée pour {token}. {result}",
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors de la récupération de l'analyse {token}: {e}")
        return TokenDataResponse(
            success=False,
            message=f"Erreur: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

# Endpoint de santé
@simon.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Endpoint de santé pour vérifier que l'agent fonctionne"""
    return HealthResponse(
        status="healthy",
        agent="Intellect Agent",
        address=simon.address,
        timestamp=datetime.now().isoformat()
    )

# Endpoint pour lister les tokens supportés
@simon.on_rest_get("/supported_tokens", SupportedTokensResponse)
async def get_supported_tokens(ctx: Context) -> SupportedTokensResponse:
    """Retourne la liste des tokens supportés"""
    return SupportedTokensResponse(
        supported_tokens=SUPPORTED_TOKENS,
        count=len(SUPPORTED_TOKENS),
        timestamp=datetime.now().isoformat()
    )

# Gestionnaire de démarrage
@simon.on_event("startup")
async def startup_handler(ctx: Context):
    """Gestionnaire exécuté au démarrage de l'agent"""
    ctx.logger.info("🚀 Agent Intellect démarré")
    ctx.logger.info(f"📍 Adresse de l'agent: {simon.address}")
    ctx.logger.info(f"🎯 Adresse de Simon: {SIMON_AGENT_ADDRESS}")
    ctx.logger.info(f"💱 Tokens supportés: {', '.join(SUPPORTED_TOKENS)}")
    
    # Financer l'agent si nécessaire
    fund_agent_if_low(simon.wallet.address())

if __name__ == "__main__":
    logger.info("🔄 Démarrage de l'agent Intellect...")
    logger.info(f"🌐 Endpoints disponibles:")
    logger.info(f"   POST /analyze - Demander une analyse de token")
    logger.info(f"   GET /market_data - Récupérer toutes les analyses")
    logger.info(f"   GET /market_data/{{token}} - Récupérer l'analyse d'un token")
    logger.info(f"   GET /health - Vérifier la santé de l'agent")
    logger.info(f"   GET /supported_tokens - Liste des tokens supportés")
    
    simon.run()
