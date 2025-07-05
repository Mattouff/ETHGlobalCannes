from typing import Any
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import json
import uuid


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


# Configuration de l'agent avec endpoint
agent = Agent(
    name="intellect",
    port=8001,
    seed="intentfi-agent-seed-phrase",
    endpoint=["http://localhost:8001/submit"],
)

print(f"Agent address: {agent.address}")
fund_agent_if_low(agent.wallet.address())

AI_AGENT_ADDRESS = "agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx"

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

class AIResponse(Model):
    request_id: str
    recommendation: dict[str, Any]

async def generate_intent_recommendation(ctx: Context, request: IntentRequest):
    """Génère une recommandation d'intent en contactant réellement l'AI agent Claude"""
    
    # Créer un ID unique pour cette requête
    import uuid
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
            "reasoning": "analyse de marché détaillée"
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
            "reasoning": "analyse de risque détaillée"
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
            "suggested_action": "action recommandée"
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
            "cross_chain_details": {
                "type": "object",
                "properties": {
                    "source_chain": {"type": "string"},
                    "target_chain": {"type": "string"},
                    "estimated_gas": {"type": "string"}
                }
            }
        },
        "required": ["type", "reasoning"]
    }
    
    # Envoyer le prompt à l'AI agent Claude
    try:
        prompt = StructuredOutputPrompt(
            prompt=financial_prompt,
            output_schema=intent_schema
        )
        
        ctx.logger.info(f"🧠 Envoi du prompt financier à Claude AI pour {request.user_id}")
        ctx.logger.info(f"📤 Request ID: {request_id}")
        
        # Stocker la requête en attente
        pending_requests[request_id] = {
            "user_id": request.user_id,
            "intent_type": request.intent_type,
            "timestamp": ctx.timestamp if hasattr(ctx, 'timestamp') else "N/A"
        }
        
        # Envoyer à l'AI agent Claude
        await ctx.send(AI_AGENT_ADDRESS, prompt)
        
        # TODO: Implémenter un système d'attente pour la réponse
        # Pour l'instant, on retourne une réponse temporaire
        ctx.logger.info("⏳ En attente de la réponse de Claude AI...")
         
        import asyncio
        await asyncio.sleep(1)  

        return {
            "type": "ai_analysis_pending",
            "reasoning": f"Analyse en cours par Claude AI pour request_id: {request_id}",
            "status": "pending_ai_response",
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
        timestamp=str(ctx.timestamp) if hasattr(ctx, 'timestamp') else "N/A"
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

agent.include(intentfi_protocol)

class Location(Model):
    city: str
    country: str
    temperature: float


@agent.on_event("startup")
async def send_message(ctx: Context):
    ctx.logger.info("🚀 IntentFi Agent démarré!")
    ctx.logger.info(f"📍 Endpoints disponibles:")
    ctx.logger.info(f"   GET  http://localhost:8001/health")
    ctx.logger.info(f"   POST http://localhost:8001/recommend")
    ctx.logger.info(f"   GET  http://localhost:8001/intents/popular")
    
    prompt = StructuredOutputPrompt(
        prompt="Get current ETH price and market sentiment for trading decisions",
        output_schema=Location.schema(),
    )
    await ctx.send(AI_AGENT_ADDRESS, prompt)


@agent.on_message(TextResponse)
async def handle_text_response(ctx: Context, sender: str, msg: TextResponse):
    ctx.logger.info(f"📥 Réponse IA: {msg.text}")


@agent.on_message(StructuredOutputResponse)  
async def handle_structured_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    """Traite les réponses structurées de Claude AI pour les recommandations d'intents"""
    ctx.logger.info(f"📥 Réponse Claude AI reçue de ...{sender[-8:]}:")
    ctx.logger.info(f"🔍 Données: {msg.output}")
    
    try:
        # Vérifier si c'est une réponse d'intent financier
        if isinstance(msg.output, dict) and any(key in msg.output for key in ['type', 'condition', 'action', 'reasoning']):
            ctx.logger.info("💰 Recommandation d'intent financier reçue!")
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
            
        else:
            ctx.logger.info(f"📊 Autre réponse structurée: {msg.output}")
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur lors du traitement de la réponse Claude: {e}")
        ctx.logger.info(f"📋 Données brutes: {msg.output}")


if __name__ == "__main__":
    agent.run()