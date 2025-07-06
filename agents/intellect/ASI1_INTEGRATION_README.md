# 🚀 ASI1.ai Integration - IntentFi Agent

## 📋 Overview

Your IntentFi agent is now **compatible with ASI1.ai**! It can receive and process messages via the official Fetch.ai chat protocol and REST APIs.

## 🌐 Connecting with ASI1.ai

### 1. **Via the ASI1.ai Web Interface**

- Go to https://asi1.ai/
- Use your agent's address: `agent1qf82uz69zk3dlw6k3y5aewlfaavcxed29a8w9rmxqsf20tgnwtx9xxdrf24`
- Start chatting directly!

### 2. **Via the REST API**

Your agent exposes several compatible endpoints:

```bash
# Base URL (via ngrok)
https://91fe-83-144-23-154.ngrok-free.app

# Available endpoints:
POST /chat/send                    # Send a message
GET  /chat/conversations           # List conversations
GET  /chat/history/{conv_id}       # Conversation history
GET  /chat/analytics               # Analytics and statistics
GET  /asi-one/metadata             # Agent metadata
GET  /health                       # Health status
```

## 💬 Usage Examples

### Chat via REST API

```bash
curl -X POST https://91fe-83-144-23-154.ngrok-free.app/chat/send \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Recommend me an intent for ETH",
        "sender_id": "user123"
    }'
```

### Supported Messages

The agent understands several types of requests:

#### 🎯 **Financial Intents**

- "Recommend me an intent for ETH"
- "Create a DCA strategy for Bitcoin"
- "Risk management intent"
- "Conditional price strategy"

#### 📊 **Trading Analysis**

- "Analyze ETH"
- "Buy or sell BTC?"
- "Market sentiment for SOL"
- "Trading MATIC"

#### ❓ **Help and Conversation**

- "help" or "aide"
- General crypto questions
- Requests for explanations

## 🔧 Response Structure

### Chat Message (Official Protocol)

```python
{
    "timestamp": "2025-07-06T12:00:00Z",
    "msg_id": "uuid4",
    "content": [
        {
            "type": "text",
            "text": "Here is my response..."
        }
    ]
}
```

### API REST Response

```json
{
  "success": true,
  "message_id": "uuid4",
  "response": "🎯 Intent recommendation...",
  "conversation_id": "api_conv_123",
  "timestamp": "2025-07-06T12:00:00Z"
}
```

## 🎯 Agent Capabilities

### **Intent Recommendations**

- **Price-based**: Price condition triggers
- **Time-based**: DCA strategies and scheduling
- **Risk management**: Risk management and stop-loss
- **Cross-chain**: Inter-chain transfers with LayerZero

### **Trading Analysis**

- Real-time market data (CoinGecko)
- Technical analysis (support/resistance)
- News sentiment
- Buy/sell/hold recommendations

### **Supported Tokens**

ETH, BTC, USDC, USDT, SOL, ADA, MATIC, AVAX, DOT, LINK, UNI, ARB, OP, FLOW, and more...

## 🔗 Technical Configuration

### Enabled Protocols

- ✅ **Official Fetch.ai chat protocol** (if uagents_core available)
- ✅ **IntentFi Protocol** (custom recommendations)
- ✅ **Simon Communication** (trading analysis)
- ✅ **REST API** (web endpoints)

### Public Endpoints

```
Agent Address: agent1qf82uz69zk3dlw6k3y5aewlfaavcxed29a8w9rmxqsf20tgnwtx9xxdrf24
Public URL: https://91fe-83-144-23-154.ngrok-free.app
Port: 8000
```

## 🚨 Troubleshooting

### If chat is not working:

1. **Check ngrok**: The URL must be accessible
2. **Protocol**: Install `uagents_core` for the official protocol
3. **Agent running**: Make sure the agent is running on port 8000

### Useful logs:

```bash
# Start the agent and check logs
python intellect.py

# Look for these messages:
✅ Official chat protocol initialized successfully!
🔗 ASI1.AI INTEGRATION READY! 🔗
```

## 🎉 Quick Test

### Via curl:

```bash
curl https://91fe-83-144-23-154.ngrok-free.app/health
```

### Via ASI1.ai:

1. Go to https://asi1.ai/
2. Connect with the agent address
3. Type: "Hello, recommend me an ETH intent"
4. 🎯 Wait for the personalized response!

---

**🚀 Your IntentFi agent is now ready to communicate with the world via ASI1.ai!**
