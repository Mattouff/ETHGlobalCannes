from typing import Any
from uagents import Agent, Context, Model, Protocol
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
import logging

# Import du protocole de chat officiel Fetch.ai
try:
    from uagents_core.contrib.protocols.chat import (
        ChatMessage,
        ChatAcknowledgement,
        TextContent,
        chat_protocol_spec
    )
    CHAT_PROTOCOL_AVAILABLE = True
    print("✅ Protocole de chat officiel Fetch.ai chargé")
except ImportError:
    print("⚠️ Protocole de chat officiel non disponible, utilisation du protocole custom")
    CHAT_PROTOCOL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèles de base pour la communication
class TextPrompt(Model):
    text: str

class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: dict[str, Any]

class StructuredOutputResponse(Model):
    output: dict[str, Any]

# Adresse de l'agent Claude AI sur Agentverse (temporairement désactivé pour tests)
AI_AGENT_ADDRESS = None  # Désactivé temporairement pour diagnostiquer

# Variables pour gérer les conversations en attente
pending_chats = {}

# Création de l'agent chat uniquement (pas de REST)
chat_agent = Agent(
    name="intellect_chat",
    port=8010,
    seed="intentfi-chat-agent-seed-phrase",
    mailbox=True,
)

# Protocole de chat uniquement
if CHAT_PROTOCOL_AVAILABLE:
    chat_protocol = Protocol(spec=chat_protocol_spec)
else:
    chat_protocol = Protocol("ASI_ONE_Chat")

# Handler principal pour le protocole de chat
@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"💬 Message reçu de {sender}")
    ctx.logger.info(f"🔍 Type de message: {type(msg)}")
    ctx.logger.info(f"🔍 Contenu brut: {msg}")
    
    text = ""
    try:
        if hasattr(msg, 'content') and msg.content:
            if isinstance(msg.content, list) and len(msg.content) > 0:
                if hasattr(msg.content[0], 'text'):
                    text = msg.content[0].text
                else:
                    text = str(msg.content[0])
            else:
                text = str(msg.content)
        ctx.logger.info(f"📝 Texte extrait: '{text}'")
    except Exception as e:
        ctx.logger.error(f"❌ Erreur extraction texte: {e}")
        text = "hello"  # Fallback
    
    # Toujours utiliser la réponse directe pour l'instant
    try:
        response_text = generate_direct_response(text)
        ctx.logger.info(f"🎯 Réponse générée: '{response_text[:100]}...'")
        
        if CHAT_PROTOCOL_AVAILABLE:
            chat_msg = ChatMessage(
                msg_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                content=[TextContent(type="text", text=response_text)]
            )
            await ctx.send(sender, chat_msg)
            ctx.logger.info(f"📤 Réponse envoyée avec succès à {sender}")
        else:
            await ctx.send(sender, response_text)
            ctx.logger.info(f"📤 Réponse custom envoyée à {sender}")
            
    except Exception as e:
        ctx.logger.error(f"❌ Erreur envoi réponse: {e}")
        # Réponse d'urgence ultra-simple
        try:
            simple_response = "🤖 IntentFi Agent connecté ! Erreur temporaire, mais je suis là."
            if CHAT_PROTOCOL_AVAILABLE:
                emergency_msg = ChatMessage(
                    msg_id=str(uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    content=[TextContent(type="text", text=simple_response)]
                )
                await ctx.send(sender, emergency_msg)
            else:
                await ctx.send(sender, simple_response)
            ctx.logger.info("🚨 Réponse d'urgence envoyée")
        except Exception as e2:
            ctx.logger.error(f"💥 Échec complet envoi: {e2}")
            
    return  # Supprime le code Claude AI pour l'instant

def generate_direct_response(text: str) -> str:
    """Génère une réponse directe intelligente sans Claude AI"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["hello", "salut", "bonjour", "test"]):
        return "🤖 Bonjour ! Je suis IntentFi Agent, votre assistant crypto et intents financiers. Comment puis-je vous aider aujourd'hui ?"
    
    elif any(word in text_lower for word in ["eth", "ethereum"]):
        return "📊 ETH : Ethereum reste une excellente option d'investissement. Voulez-vous que je vous recommande un intent conditionnel pour acheter ETH si le prix descend sous un certain seuil ?"
    
    elif any(word in text_lower for word in ["btc", "bitcoin"]):
        return "🪙 Bitcoin : L'or numérique ! Pour du long terme, une stratégie DCA (Dollar Cost Averaging) peut être intéressante. Souhaitez-vous un intent de DCA automatique ?"
    
    elif any(word in text_lower for word in ["intent", "recommand", "stratégie"]):
        return "🎯 Intents disponibles :\n• Intent conditionnel (prix)\n• Intent DCA (récurrent)\n• Intent stop-loss (protection)\n• Intent cross-chain (LayerZero)\n\nQuel type vous intéresse ?"
    
    elif any(word in text_lower for word in ["aide", "help", "commandes"]):
        return "🆘 Commandes disponibles :\n• 'ETH' ou 'Bitcoin' pour analyse\n• 'Intent' pour recommandations\n• 'Trading' pour stratégies\n• 'DCA' pour investissement récurrent\n\nPosez vos questions en langage naturel !"
    
    elif any(word in text_lower for word in ["trading", "acheter", "vendre", "buy", "sell"]):
        return "📈 Trading : Le marché crypto est volatil. Je recommande toujours des intents conditionnels avec stop-loss pour limiter les risques. Quel token vous intéresse ?"
    
    elif any(word in text_lower for word in ["dca", "récurrent", "automatique"]):
        return "🔄 DCA (Dollar Cost Averaging) : Excellente stratégie ! Investir la même somme régulièrement réduit l'impact de la volatilité. Fréquence souhaitée : hebdomadaire ou mensuelle ?"
    
    else:
        return f"🤔 Merci pour votre message : '{text}'. Je suis spécialisé en crypto et intents financiers. Posez-moi des questions sur ETH, Bitcoin, stratégies de trading, ou intents conditionnels !"

# Handler pour la réponse structurée de Claude (maintenant sur chat_agent)
@chat_agent.on_message(StructuredOutputResponse)
async def handle_structured_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    ctx.logger.info(f"📥 Réponse Claude AI reçue de ...{sender[-8:]}: {msg.output}")
    
    response_text = msg.output.get("response", "Désolé, je n'ai pas compris la réponse de l'IA.")
    conversation_id = msg.output.get("conversation_id")
    
    # Trouver l'utilisateur original
    original_sender = None
    if conversation_id and conversation_id in pending_chats:
        original_sender = pending_chats[conversation_id]
        del pending_chats[conversation_id]
    
    if original_sender:
        if CHAT_PROTOCOL_AVAILABLE:
            chat_msg = ChatMessage(
                msg_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                content=[TextContent(type="text", text=response_text)]
            )
            await ctx.send(original_sender, chat_msg)
            ctx.logger.info(f"📤 Réponse envoyée à {original_sender}")
        else:
            await ctx.send(original_sender, response_text)
    else:
        ctx.logger.warning("⚠️ Impossible de trouver l'utilisateur original pour la réponse")

# Handler pour accusé de réception (obligatoire pour le protocole officiel)
if CHAT_PROTOCOL_AVAILABLE:
    @chat_protocol.on_message(model=ChatAcknowledgement)
    async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
        ctx.logger.info(f"✅ Accusé de réception reçu de {sender} pour le message {msg.acknowledged_msg_id}")

# Inclusion du protocole de chat uniquement (sans publish_manifest)
chat_agent.include(chat_protocol)

@chat_agent.on_event("startup")
async def startup_event(ctx: Context):
    ctx.logger.info("🚀 Agent de chat IntentFi démarré!")
    ctx.logger.info(f"🎯 Adresse de l'agent: {ctx.agent.address}")
    ctx.logger.info(f"🌐 Port: 8010")  # Port fixe
    ctx.logger.info(f"🔗 Mailbox activée: True")
    
    if AI_AGENT_ADDRESS:
        ctx.logger.info(f"🧠 Communication avec Claude AI: {AI_AGENT_ADDRESS}")
    else:
        ctx.logger.info("🧠 Mode réponse directe activé (pas de Claude AI)")
        
    ctx.logger.info("💬 Prêt à recevoir des messages via le protocole de chat!")
    ctx.logger.info("✅ Testez en envoyant 'Hello' ou 'ETH' via Agentverse/ASI One")
    ctx.logger.info("=" * 80)
    ctx.logger.info("🔍 ADRESSE POUR AGENTVERSE:")
    ctx.logger.info(f"   {ctx.agent.address}")
    ctx.logger.info("=" * 80)

if __name__ == "__main__":
    chat_agent.run()
