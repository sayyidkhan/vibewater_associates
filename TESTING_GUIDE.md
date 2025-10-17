# Testing Guide - WebSocket Integration

## Overview

This guide helps you verify that the frontend is correctly parsing WebSocket responses and updating the strategy builder.

## Data Flow Verification

### 1. Backend → Frontend Flow

```
AWS Bedrock Response
        ↓
<user_message>...</user_message>
<backend>{...}</backend>
        ↓
Backend Parser (bedrock_service.py)
        ↓
WebSocket Message
{
  "type": "message_complete",
  "user_message": "...",
  "strategy_json": {...}
}
        ↓
Frontend WebSocket Hook (useWebSocketChat.ts)
        ↓
State Updates:
- messages[] ← user_message
- strategyJson ← strategy_json
        ↓
StrategyBuilder Component
        ↓
UI Updates:
- Chat displays user_message
- Flowchart renders from strategy_json.flowchart
- Metrics update from strategy_json.strategy_metrics
- Guardrails update from strategy_json.guardrails
```

## Console Logging

The integration now includes comprehensive console logging to track data flow:

### Backend Logs
When the backend receives and parses a response, you'll see:
```python
# In bedrock_service.py parse_response method
# Logs when extracting user_message and backend JSON
```

### Frontend Logs

**WebSocket Hook** (`useWebSocketChat.ts`):
```
📨 Message complete received: { hasUserMessage: true, hasStrategyJson: true, hasError: false }
💬 Adding user message to chat: I've created a high-return crypto strategy...
🎯 Updating strategy JSON: { account: {...}, flowchart: {...}, ... }
```

**Strategy Builder** (`StrategyBuilder.tsx`):
```
🔄 Strategy JSON received, updating UI: { account: {...}, ... }
📊 Updating flowchart with 6 nodes
🎲 Updating degen class to: High
📈 Updating metrics: { impact_monthly_return_delta_pct: 7, estimated_capital_required_usd: 1000 }
🛡️ Updating guardrails: 3 items
```

## Testing Steps

### Step 1: Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Open Browser with DevTools

1. Navigate to `http://localhost:3000/builder`
2. Open Browser DevTools (F12 or Cmd+Option+I)
3. Go to **Console** tab

### Step 3: Send Test Message

Type in the chat input:
```
I have $1000, please choose a high-return strategy that gives at least 7% returns monthly
```

### Step 4: Verify Console Logs

You should see the following sequence in the console:

1. **WebSocket Connection:**
   ```
   WebSocket connected
   ```

2. **Message Start:**
   ```
   📨 Message complete received: { hasUserMessage: true, hasStrategyJson: true, hasError: false }
   ```

3. **User Message Added:**
   ```
   💬 Adding user message to chat: I've created a high-return crypto strategy...
   ```

4. **Strategy JSON Received:**
   ```
   🎯 Updating strategy JSON: { account: {...}, flowchart: {...}, ... }
   ```

5. **UI Updates:**
   ```
   🔄 Strategy JSON received, updating UI: { account: {...}, ... }
   📊 Updating flowchart with 6 nodes
   🎲 Updating degen class to: High
   📈 Updating metrics: { impact_monthly_return_delta_pct: 7, ... }
   🛡️ Updating guardrails: 3 items
   ```

### Step 5: Verify UI Updates

Check that the following UI elements update:

#### ✅ Chat Panel (Left Sidebar)
- [ ] User message appears in blue bubble on right
- [ ] Assistant response appears in gray bubble on left
- [ ] Green notification: "✅ Strategy builder updated with new configuration"

#### ✅ Flowchart (Center Panel)
- [ ] Nodes appear in the flowchart
- [ ] Nodes are connected with edges
- [ ] Node labels match the strategy (e.g., "Start Strategy", "Crypto Category", etc.)

#### ✅ Configuration Panel (Right Sidebar)

**Degen Class:**
- [ ] Correct risk level is selected (High/Medium/Low)
- [ ] Button is highlighted in primary color

**Strategy Impact:**
- [ ] Monthly return percentage matches user request
- [ ] Display shows: "+7% expected monthly returns" (or user's value)

**Estimated Capital:**
- [ ] Capital amount matches user request
- [ ] Display shows: "$1,000" (or user's value)

**Guardrails:**
- [ ] Guardrails appear with correct status colors:
  - Green (✅) for "ok" status
  - Yellow (⚠️) for "warning" status
  - Red (⛔) for "error" status
- [ ] Guardrail messages are displayed

## Troubleshooting

### Issue: No Console Logs

**Problem:** No logs appear in console

**Solutions:**
1. Ensure DevTools Console is open
2. Check Console filter settings (should show all levels)
3. Verify frontend is running on `http://localhost:3000`

### Issue: WebSocket Not Connecting

**Problem:** "Connecting to AI assistant..." stays visible

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify WebSocket URL in `useWebSocketChat.ts` (default: `ws://localhost:8000/ws/chat`)
3. Check browser console for WebSocket errors

### Issue: Chat Works But No Strategy JSON

**Problem:** Chat message appears but flowchart doesn't update

**Check Console For:**
```
🎯 Updating strategy JSON: null
```

**Solutions:**
1. Check backend logs for parsing errors
2. Verify LLM response includes both `<user_message>` and `<backend>` tags
3. Check if `strategy_json` is null in WebSocket message
4. Verify AWS Bedrock credentials are correct

### Issue: Strategy JSON Received But UI Not Updating

**Problem:** Console shows strategy JSON but UI doesn't change

**Check Console For:**
```
🔄 Strategy JSON received, updating UI: { ... }
📊 Updating flowchart with 0 nodes  ← Problem: no nodes
```

**Solutions:**
1. Verify `strategyJson.flowchart.nodes` exists and has items
2. Check node types match `nodeTypes` in StrategyBuilder
3. Verify ReactFlow is rendering (check for errors)

### Issue: Partial UI Updates

**Problem:** Some parts update but not others

**Check Which Logs Appear:**
- ✅ `📊 Updating flowchart` → Flowchart should update
- ✅ `🎲 Updating degen class` → Degen class should update
- ✅ `📈 Updating metrics` → Metrics should update
- ✅ `🛡️ Updating guardrails` → Guardrails should update

**Solutions:**
1. Check if specific fields are missing in strategy JSON
2. Verify field names match expected structure
3. Check for TypeScript errors in browser console

## Expected Response Structure

The backend should send this structure to frontend:

```json
{
  "type": "message_complete",
  "user_message": "I've created a high-return crypto strategy...",
  "strategy_json": {
    "account": {
      "workspace": "Vibe Water Associates",
      "section": "My Strategies"
    },
    "flowchart": {
      "nodes": [
        { "id": "start", "type": "start", "label": "Start Strategy" },
        { "id": "category", "type": "category", "label": "Crypto Category: ", "meta": {...} },
        ...
      ],
      "edges": [
        ["start", "category"],
        ["category", "entry"],
        ...
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
        { "key": "no_short_selling", "label": "No short selling", "status": "ok" },
        ...
      ]
    }
  },
  "error": null
}
```

## Debug Checklist

Use this checklist to debug issues:

- [ ] Backend server is running on port 8000
- [ ] Frontend server is running on port 3000
- [ ] Browser DevTools Console is open
- [ ] WebSocket connection is established (check console for "WebSocket connected")
- [ ] AWS Bedrock credentials are configured in `.env`
- [ ] Message sent from chat input
- [ ] Console shows "📨 Message complete received"
- [ ] Console shows "💬 Adding user message to chat"
- [ ] Console shows "🎯 Updating strategy JSON"
- [ ] Console shows "🔄 Strategy JSON received, updating UI"
- [ ] Chat displays user's message
- [ ] Chat displays assistant's response
- [ ] Green notification appears: "✅ Strategy builder updated"
- [ ] Flowchart shows nodes
- [ ] Degen class is selected
- [ ] Metrics are updated
- [ ] Guardrails are displayed

## Success Criteria

✅ **Integration is working correctly when:**

1. User sends a message
2. Chat displays both user and assistant messages
3. Green notification appears
4. Flowchart updates with nodes and edges
5. Degen class selection updates
6. Strategy metrics update (capital and returns)
7. Guardrails update with correct status colors
8. All console logs appear in correct sequence
9. No errors in browser console
10. No errors in backend logs

---

**Note:** All console logs use emojis for easy identification:
- 📨 WebSocket message received
- 💬 Chat message
- 🎯 Strategy JSON
- 🔄 UI update triggered
- 📊 Flowchart update
- 🎲 Degen class update
- 📈 Metrics update
- 🛡️ Guardrails update
- ❌ Error
