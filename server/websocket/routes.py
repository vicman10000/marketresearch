"""
WebSocket Routes
WebSocket endpoints for real-time updates
"""
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import structlog

from server.websocket.manager import manager
from server.database import get_db
from server.auth.security import decode_token

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["WebSocket"])


async def get_user_from_token(token: Optional[str], db: Session) -> Optional[int]:
    """
    Extract user ID from JWT token
    Returns None if token is invalid or not provided
    """
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            email = payload.get("sub")
            if email:
                from server.models.user import User
                user = db.query(User).filter(User.email == email).first()
                return user.id if user else None
    except Exception as e:
        logger.warning("websocket_token_validation_failed", error=str(e))
    
    return None


@router.websocket("/ws/market-updates")
async def websocket_market_updates(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time market data updates
    
    Query params:
        token: Optional JWT token for authenticated users
    
    Message format:
        Subscribe: {"action": "subscribe", "symbols": ["AAPL", "MSFT"]}
        Unsubscribe: {"action": "unsubscribe", "symbols": ["AAPL"]}
    """
    connection_id = str(uuid.uuid4())
    user_id = await get_user_from_token(token, db)
    
    await manager.connect(websocket, connection_id, user_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "welcome",
            "connection_id": connection_id,
            "authenticated": user_id is not None,
            "message": "Connected to market updates stream"
        }, connection_id)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "subscribe":
                # Subscribe to specific stock symbols
                symbols = data.get("symbols", [])
                for symbol in symbols:
                    topic = f"stock:{symbol}"
                    manager.subscribe(connection_id, topic)
                
                await manager.send_personal_message({
                    "type": "subscribed",
                    "symbols": symbols
                }, connection_id)
                
                logger.info("subscribed_to_stocks",
                           connection_id=connection_id,
                           symbols=symbols)
            
            elif action == "unsubscribe":
                # Unsubscribe from specific stock symbols
                symbols = data.get("symbols", [])
                for symbol in symbols:
                    topic = f"stock:{symbol}"
                    manager.unsubscribe(connection_id, topic)
                
                await manager.send_personal_message({
                    "type": "unsubscribed",
                    "symbols": symbols
                }, connection_id)
                
                logger.info("unsubscribed_from_stocks",
                           connection_id=connection_id,
                           symbols=symbols)
            
            elif action == "ping":
                # Heartbeat
                await manager.send_personal_message({
                    "type": "pong"
                }, connection_id)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
        logger.info("websocket_client_disconnected", connection_id=connection_id)
    
    except Exception as e:
        logger.error("websocket_error",
                    connection_id=connection_id,
                    error=str(e))
        manager.disconnect(connection_id, user_id)


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for user notifications
    Requires authentication
    
    Query params:
        token: JWT access token (required)
    """
    connection_id = str(uuid.uuid4())
    user_id = await get_user_from_token(token, db)
    
    if not user_id:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    await manager.connect(websocket, connection_id, user_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "welcome",
            "connection_id": connection_id,
            "message": "Connected to notifications stream"
        }, connection_id)
        
        # Subscribe to user notifications topic
        manager.subscribe(connection_id, f"user:{user_id}")
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, connection_id)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
        logger.info("notifications_websocket_disconnected",
                   connection_id=connection_id,
                   user_id=user_id)
    
    except Exception as e:
        logger.error("notifications_websocket_error",
                    connection_id=connection_id,
                    user_id=user_id,
                    error=str(e))
        manager.disconnect(connection_id, user_id)


@router.get("/ws/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics
    """
    return {
        "total_connections": manager.get_connection_count(),
        "unique_users": len(manager.user_connections),
        "active_topics": len(manager.topic_subscriptions)
    }

