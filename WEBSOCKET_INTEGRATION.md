# WebSocket Integration with AWS Bedrock

This document describes the WebSocket-based chat integration with AWS Bedrock for the Vibe Water Associates trading platform.

## Overview

The application now features real-time chat functionality that:
- Connects to AWS Bedrock using Claude 3.5 Haiku model
- Streams responses via WebSocket for real-time interaction
- Parses LLM responses into two components:
  1. **User-facing messages** for the chat interface
  2. **Strategy JSON** for populating the visual strategy builder

## Architecture

### Backend Components

#### 1. Bedrock Service (`app/services/bedrock_service.py`)
- Manages AWS Bedrock client initialization
- Contains system prompt for strategy generation
- Streams chat responses from Claude
- Parses responses into user messages and strategy JSON

#### 2. WebSocket Router (`app/routers/websocket_chat.py`)
- WebSocket endpoint at `/ws/chat`
- Manages real-time bidirectional communication
- Handles message streaming and error handling
- Connection management with automatic reconnection

#### 3. Configuration (`app/config.py`)
Environment variables:
```env
AWS_BEARER_TOKEN_BEDROCK=your_token_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0
```

### Frontend Components

#### 1. WebSocket Hook (`hooks/useWebSocketChat.ts`)
Custom React hook providing:
- WebSocket connection management
- Message state management
- Automatic reconnection on disconnect
- Strategy JSON state updates

#### 2. Strategy Builder (`components/StrategyBuilder.tsx`)
Enhanced with:
- Real-time chat interface
- Dynamic strategy visualization from JSON
- Live updates to metrics, guardrails, and flowchart
- Connection status indicators

## Message Flow

### Client → Server
```json
{
  "type": "message",
  "content": "I have $1000, please choose a high-return strategy",
  "history": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous response"}
  ]
}
```

### LLM Response Format

The LLM generates responses using XML-style tags to separate the two components:

```xml
<user_message>
I've created a high-return crypto strategy tailored to your $1000 capital with a target of 7% monthly returns. This is classified as a high-risk strategy with appropriate stop-loss protection at 5% to manage downside risk.
</user_message>

<backend>
{
  "account": {...},
  "flowchart": {...},
  "guardrails": {...},
  ...
}
</backend>
```

### Server → Client

**1. Message Start**
```json
{
  "type": "message_start",
  "message_id": "msg_1"
}
```

**2. Content Chunks (streaming)**
```json
{
  "type": "content_chunk",
  "chunk": "text chunk"
}
```

**3. Message Complete**
```json
{
  "type": "message_complete",
  "user_message": "Conversational response for chat (extracted from <user_message> tag)",
  "strategy_json": {
    "account": {...},
    "flowchart": {...},
    "guardrails": {...},
    ...
  },
  "error": null
}
```

The backend parser extracts:
- **user_message**: Content between `<user_message>` tags → sent to chat interface
- **strategy_json**: JSON content between `<backend>` tags → sent to update strategy builder global state

## Strategy JSON Format

The LLM generates a comprehensive JSON structure that populates the strategy builder:

```json
{
  "account": {
    "workspace": "Vibe Water Associates",
    "section": "My Strategies"
  },
  "assistant_panel": {
    "greeting": "Hello",
    "user_request": "User's original request",
    "assistant_reply": "Brief summary of recommendation"
  },
  "flowchart": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "label": "Start Strategy"
      },
      {
        "id": "category",
        "type": "category",
        "label": "Crypto Category: ",
        "meta": {
          "category": "DeFi"
        }
      },
      {
        "id": "entry",
        "type": "entry_condition",
        "label": "Set Entry Condition: ",
        "meta": {
          "mode": "ai_optimized",
          "rules": ["Enter on a 5% price drop"]
        }
      },
      {
        "id": "profit_target",
        "type": "take_profit",
        "label": "Profit Target: ",
        "meta": {
          "target_pct": 7.0
        }
      },
      {
        "id": "stop_loss",
        "type": "stop_loss",
        "label": "Stop Loss: ",
        "meta": {
          "stop_pct": 5.0,
          "added": true
        }
      },
      {
        "id": "end",
        "type": "end",
        "label": "End Strategy"
      }
    ],
    "edges": [
      ["start", "category"],
      ["category", "entry"],
      ["entry", "profit_target"],
      ["profit_target", "stop_loss"],
      ["stop_loss", "end"]
    ]
  },
  "degen_class": {
    "options": ["High", "Medium", "Low"],
    "selected": "High"
  },
  "strategy_metrics": {
    "impact_monthly_return_delta_pct": 7.0,
    "estimated_capital_required_usd": 1000
  },
  "guardrails": {
    "enabled": [
      {
        "key": "no_short_selling",
        "label": "No short selling",
        "status": "ok"
      },
      {
        "key": "high_risk_class",
        "label": "High risk asset class selected",
        "status": "warning"
      }
    ],
    "violations": []
  },
  "actions": {
    "explain_button": {
      "label": "Explain",
      "enabled": true
    },
    "run_backtest_button": {
      "label": "Run Backtest",
      "enabled": true
    }
  }
}
```

## System Prompt

The Bedrock service uses a carefully crafted system prompt that instructs Claude to:
1. Generate both conversational responses (in `<user_message>` tags) and structured JSON (in `<backend>` tags)
2. Adapt strategy parameters based on user requirements
3. Set appropriate risk levels and guardrails
4. Include all necessary flowchart nodes and connections
5. Calculate realistic metrics based on user capital and goals

### Response Flow:
1. **User message component** (`<user_message>`) → Displayed in chat interface
2. **Backend JSON component** (`<backend>`) → Updates global state for strategy builder page
   - Flowchart nodes and edges
   - Degen class selection
   - Strategy metrics (capital, returns)
   - Guardrails and safety nets
   - Action buttons state

## Usage

### Starting the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testing the Integration

1. Navigate to `/builder` page
2. Wait for WebSocket connection (green status)
3. Type a message like: "I have $5000 and want a conservative strategy with 3% monthly returns"
4. Watch as:
   - Chat displays the conversational response
   - Flowchart updates with strategy nodes
   - Metrics update with capital and return estimates
   - Guardrails adjust based on risk level

## Error Handling

- **Connection errors**: Automatic reconnection after 3 seconds
- **Parse errors**: Displayed in chat with error message
- **Bedrock errors**: Caught and returned to client
- **Invalid JSON**: Gracefully handled with error notification

## Dependencies

### Backend
- `boto3==1.34.34` - AWS SDK for Bedrock
- `websockets==12.0` - WebSocket support
- `fastapi==0.109.0` - Web framework with WebSocket support

### Frontend
- Native WebSocket API (built into browsers)
- React hooks for state management
- ReactFlow for visual flowchart rendering

## Security Considerations

1. **API Keys**: Store AWS credentials in `.env` file (never commit)
2. **CORS**: Configure allowed origins in settings
3. **WebSocket**: Consider adding authentication for production
4. **Rate Limiting**: Implement rate limiting for Bedrock calls

## Future Enhancements

- [ ] Add authentication to WebSocket connections
- [ ] Implement message persistence
- [ ] Add typing indicators during streaming
- [ ] Support for multiple concurrent strategies
- [ ] Export/import strategy JSON
- [ ] Version control for strategy iterations
