import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from ..services.bedrock_service import bedrock_service

router = APIRouter()

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def send_json(self, data: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(data)

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with Bedrock LLM
    
    Expected message format from client:
    {
        "type": "message",
        "content": "user message text",
        "history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ]
    }
    
    Response format to client:
    {
        "type": "message_start",
        "message_id": "unique_id"
    }
    {
        "type": "content_chunk",
        "chunk": "text chunk"
    }
    {
        "type": "message_complete",
        "user_message": "conversational response",
        "strategy_json": {...},
        "error": null
    }
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                user_content = message_data.get("content", "")
                history = message_data.get("history", [])
                
                # Build messages list for Bedrock
                messages = []
                
                # Add history
                for msg in history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # Add current user message
                messages.append({
                    "role": "user",
                    "content": user_content
                })
                
                # Send message start notification
                await manager.send_json({
                    "type": "message_start",
                    "message_id": f"msg_{len(messages)}"
                }, websocket)
                
                # Get response from Bedrock
                full_response = ""
                async for chunk in bedrock_service.chat_stream(messages):
                    full_response += chunk
                
                # Parse the complete response first
                parsed = bedrock_service.parse_response(full_response)
                
                # Stream only the user_message character by character
                import asyncio
                user_message = parsed.get("user_message", "")
                if user_message:
                    chunk_size = 3  # Stream 3 characters at a time
                    for i in range(0, len(user_message), chunk_size):
                        chunk = user_message[i:i+chunk_size]
                        await manager.send_json({
                            "type": "content_chunk",
                            "chunk": chunk
                        }, websocket)
                        await asyncio.sleep(0.02)  # Small delay for smooth streaming
                
                # Send complete message with parsed data
                await manager.send_json({
                    "type": "message_complete",
                    "user_message": user_message,
                    "strategy_json": parsed.get("strategy_json"),
                    "error": parsed.get("error")
                }, websocket)
            
            elif message_data.get("type") == "ping":
                # Respond to ping to keep connection alive
                await manager.send_json({
                    "type": "pong"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await manager.send_json({
                "type": "error",
                "error": str(e)
            }, websocket)
        except:
            pass
        manager.disconnect(websocket)
