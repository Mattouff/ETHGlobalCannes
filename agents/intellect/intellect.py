from typing import Any
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import json
import uuid
from datetime import datetime
import os


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


# Configuration de l'agent avec endpoint
agent = Agent(
    name="intellect",
    port=8000,
    seed="intentfi-agent-seed-phrase",
    endpoint=["http://localhost:8000/submit"],
)

print(f"Agent address: {agent.address}")
fund_agent_if_low(agent.wallet.address())

AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"

# Fichier des actualités généré par news.py
NEWS_FILE = "news_logs.json"

# Protocol pour IntentFi
intentfi_protocol = Protocol("IntentFi")


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
        
        ctx.logger.info("⏳ En attente de la réponse de Claude AI (5s max)...")
        ctx.logger.info(f"🔍 Debug - AI_AGENT_ADDRESS: {AI_AGENT_ADDRESS}")
        
        import asyncio
        for attempt in range(5):  # Seulement 5 secondes
            await asyncio.sleep(1)
            
            if request_id in ai_responses:
                ctx.logger.info(f"✅ Réponse reçue de Claude AI!")
                response = ai_responses[request_id]
                
                # Nettoyer les variables
                del ai_responses[request_id]
                if request_id in pending_requests:
                    del pending_requests[request_id]
                
                return response
        
        # Timeout après 5 secondes - Claude ne répond pas
        ctx.logger.warning(f"⏰ Timeout rapide: Claude AI ne répond pas (probablement hors ligne)")
        
        # Nettoyer
        if request_id in pending_requests:
            del pending_requests[request_id]
        
        # Retourner directement une recommandation de fallback intelligente
        ctx.logger.info("🤖 Génération d'une recommandation de fallback intelligente...")
        
        if request.intent_type == "price_based":
            return {
                "type": "conditional_transfer",
                "condition": "ETH > $3200",
                "action": "Transfer 50 USDC to Optimism via LayerZero",
                "confidence": 0.7,
                "reasoning": "Recommandation IntentFi: Basée sur l'analyse technique ETH. Niveau de résistance clé à $3200. Optimism choisi pour les frais réduits via LayerZero.",
                "cross_chain_details": {
                    "source_chain": "Ethereum",
                    "target_chain": "Optimism", 
                    "estimated_gas": "$3-6 USD"
                },
                "fallback": True,
                "chainlink_trigger": True
            }
        elif request.intent_type == "time_based":
            return {
                "type": "scheduled_dca",
                "schedule": "Weekly on Sundays at 12:00 UTC",
                "action": "DCA 20 USDC into ETH, split 70% Ethereum / 30% Arbitrum",
                "confidence": 0.8,
                "reasoning": "Recommandation IntentFi: DCA hebdomadaire optimal pour réduire la volatilité. Split multi-chain via LayerZero pour optimiser les coûts.",
                "chainlink_automation": True,
                "fallback": True
            }
        elif request.intent_type == "risk_management":
            return {
                "type": "stop_loss_protection",
                "condition": "ETH < $2900 OR portfolio_loss > 12%",
                "action": "Convert 25% ETH to USDC, distribute across Polygon and Base",
                "confidence": 0.75,
                "reasoning": "Recommandation IntentFi: Protection contre volatilité excessive. Diversification multi-chain automatique via LayerZero.",
                "chainlink_monitoring": True,
                "fallback": True
            }
        else:
            return {
                "type": "hold_strategy",
                "reasoning": "Recommandation IntentFi: Type d'intent non reconnu. Stratégie conservatrice recommandée en attendant clarification.",
                "suggested_action": "Définir un intent spécifique (price_based, time_based, risk_management)",
                "fallback": True
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


if __name__ == "__main__":
    agent.run()