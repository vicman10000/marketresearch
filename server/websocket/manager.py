"""
WebSocket Connection Manager
Manages WebSocket connections and broadcasts
"""
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import json
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Active connections: {connection_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # User connections: {user_id: Set[connection_id]}
        self.user_connections: Dict[int, Set[str]] = {}
        
        # Topic subscriptions: {topic: Set[connection_id]}
        self.topic_subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[int] = None):
        """
        Accept and register a WebSocket connection
        """
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info("websocket_connected", 
                   connection_id=connection_id,
                   user_id=user_id,
                   total_connections=len(self.active_connections))
    
    def disconnect(self, connection_id: str, user_id: Optional[int] = None):
        """
        Remove a WebSocket connection
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from all topic subscriptions
        for topic in list(self.topic_subscriptions.keys()):
            self.topic_subscriptions[topic].discard(connection_id)
            if not self.topic_subscriptions[topic]:
                del self.topic_subscriptions[topic]
        
        logger.info("websocket_disconnected",
                   connection_id=connection_id,
                   user_id=user_id,
                   total_connections=len(self.active_connections))
    
    def subscribe(self, connection_id: str, topic: str):
        """
        Subscribe a connection to a topic
        """
        if topic not in self.topic_subscriptions:
            self.topic_subscriptions[topic] = set()
        
        self.topic_subscriptions[topic].add(connection_id)
        logger.debug("subscribed_to_topic",
                    connection_id=connection_id,
                    topic=topic)
    
    def unsubscribe(self, connection_id: str, topic: str):
        """
        Unsubscribe a connection from a topic
        """
        if topic in self.topic_subscriptions:
            self.topic_subscriptions[topic].discard(connection_id)
            if not self.topic_subscriptions[topic]:
                del self.topic_subscriptions[topic]
        
        logger.debug("unsubscribed_from_topic",
                    connection_id=connection_id,
                    topic=topic)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """
        Send a message to a specific connection
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("send_personal_message_failed",
                           connection_id=connection_id,
                           error=str(e))
                self.disconnect(connection_id)
    
    async def send_to_user(self, message: dict, user_id: int):
        """
        Send a message to all connections of a specific user
        """
        if user_id in self.user_connections:
            connection_ids = list(self.user_connections[user_id])
            for connection_id in connection_ids:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict, exclude: Optional[Set[str]] = None):
        """
        Broadcast a message to all active connections
        """
        exclude = exclude or set()
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            if connection_id in exclude:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("broadcast_failed",
                           connection_id=connection_id,
                           error=str(e))
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
        
        logger.debug("broadcast_sent",
                    recipient_count=len(self.active_connections) - len(exclude) - len(disconnected))
    
    async def broadcast_to_topic(self, message: dict, topic: str):
        """
        Broadcast a message to all connections subscribed to a topic
        """
        if topic not in self.topic_subscriptions:
            logger.debug("no_subscribers_for_topic", topic=topic)
            return
        
        connection_ids = list(self.topic_subscriptions[topic])
        disconnected = []
        
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error("topic_broadcast_failed",
                               connection_id=connection_id,
                               topic=topic,
                               error=str(e))
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
        
        logger.debug("topic_broadcast_sent",
                    topic=topic,
                    recipient_count=len(connection_ids) - len(disconnected))
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a specific user"""
        return len(self.user_connections.get(user_id, set()))
    
    def get_topic_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic"""
        return len(self.topic_subscriptions.get(topic, set()))


# Global connection manager instance
manager = ConnectionManager()

