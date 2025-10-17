# Quick Setup Guide - WebSocket Chat with AWS Bedrock

## Prerequisites

- Python 3.10+
- Node.js 18+
- AWS Bedrock access with Claude 3.5 Haiku model
- AWS Bearer Token for Bedrock

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `boto3==1.34.34` - AWS SDK
- `websockets==12.0` - WebSocket support
- All existing dependencies

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your AWS credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
# AWS Bedrock Configuration
AWS_BEARER_TOKEN_BEDROCK=your_actual_bearer_token_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0
```

**Note**: The model ID, AWS region, and bearer token should already be in your `.env` file as mentioned in your request.

### 3. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The WebSocket endpoint will be available at: `ws://localhost:8000/ws/chat`

## Frontend Setup

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies (if needed)

```bash
npm install
```

No additional dependencies needed - WebSocket is native to browsers.

### 3. Start Frontend

```bash
npm run dev
```

Frontend will run at: `http://localhost:3000`

## Testing the Integration

### 1. Open Strategy Builder

Navigate to: `http://localhost:3000/builder`

### 2. Check Connection Status

- Look for connection indicator in the chat panel
- Should show "Connecting to AI assistant..." then connect
- Green status = connected

### 3. Send a Test Message

Try these example prompts:

**Conservative Strategy:**
```
I have $5000 and want a conservative strategy with 3% monthly returns
```

**Aggressive Strategy:**
```
I have $1000, please choose a high-return strategy that gives at least 7% returns monthly
```

**Balanced Strategy:**
```
I have $10000 for a medium risk strategy targeting 5% monthly returns
```

### 4. Observe the Response

You should see:
- ✅ Chat message with conversational response
- ✅ Flowchart updates with strategy nodes
- ✅ Degen Class updates (High/Medium/Low)
- ✅ Strategy metrics update (capital, returns)
- ✅ Guardrails update based on risk level

## Troubleshooting

### WebSocket Connection Fails

**Problem:** "WebSocket connection error" in chat

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify CORS settings in `backend/app/config.py`
3. Check browser console for detailed errors

### AWS Bedrock Errors

**Problem:** "Error: No response from model"

**Solutions:**
1. Verify `AWS_BEARER_TOKEN_BEDROCK` is set correctly
2. Check AWS region matches your Bedrock access
3. Confirm model ID is correct for your region
4. Check AWS credentials have Bedrock permissions

### No Strategy JSON Generated

**Problem:** Chat works but flowchart doesn't update

**Solutions:**
1. Check browser console for parsing errors
2. Verify LLM response format in backend logs
3. The system prompt should guide Claude to generate both USER_MESSAGE and STRATEGY_JSON

### TypeScript Errors

**Problem:** Type errors in frontend

**Solutions:**
1. Ensure `hooks/useWebSocketChat.ts` is properly typed
2. Run `npm run build` to check for compilation errors
3. Clear `.next` cache: `rm -rf .next`

## Architecture Overview

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│                 │◄──────────────────────────►│                  │
│  Frontend       │                             │  Backend         │
│  (Next.js)      │                             │  (FastAPI)       │
│                 │                             │                  │
│  - Chat UI      │                             │  - WS Router     │
│  - Strategy     │                             │  - Bedrock Svc   │
│    Builder      │                             │                  │
└─────────────────┘                             └────────┬─────────┘
                                                         │
                                                         │ boto3
                                                         ▼
                                                ┌──────────────────┐
                                                │                  │
                                                │  AWS Bedrock     │
                                                │  Claude 3.5      │
                                                │                  │
                                                └──────────────────┘
```

## Key Files Modified/Created

### Backend
- ✅ `requirements.txt` - Added boto3, websockets
- ✅ `app/config.py` - Added AWS Bedrock settings
- ✅ `app/services/bedrock_service.py` - **NEW** Bedrock integration
- ✅ `app/routers/websocket_chat.py` - **NEW** WebSocket endpoint
- ✅ `app/models.py` - Added chat message models
- ✅ `app/main.py` - Registered WebSocket router

### Frontend
- ✅ `hooks/useWebSocketChat.ts` - **NEW** WebSocket hook
- ✅ `components/StrategyBuilder.tsx` - Enhanced with real-time chat

### Documentation
- ✅ `WEBSOCKET_INTEGRATION.md` - Complete integration docs
- ✅ `SETUP_WEBSOCKET.md` - This setup guide

## Next Steps

1. **Test with real AWS credentials** - Replace placeholder tokens
2. **Customize system prompt** - Adjust in `bedrock_service.py` for your needs
3. **Add authentication** - Secure WebSocket connections for production
4. **Monitor costs** - Track Bedrock API usage
5. **Implement rate limiting** - Prevent abuse

## Support

For issues or questions:
1. Check `WEBSOCKET_INTEGRATION.md` for detailed documentation
2. Review backend logs: `uvicorn app.main:app --reload --log-level debug`
3. Check browser console for frontend errors
4. Verify AWS Bedrock service status

---

**Status**: ✅ Implementation Complete
**Last Updated**: 2025-01-17
