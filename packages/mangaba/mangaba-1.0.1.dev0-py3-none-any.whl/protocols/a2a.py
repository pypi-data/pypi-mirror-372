"""Protocolo A2A (Agent-to-Agent) para comunicação entre agentes Mangaba"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    """Tipos de mensagens A2A"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class A2AMessage:
    """Mensagem padrão do protocolo A2A"""
    id: str
    sender_id: str
    receiver_id: Optional[str]
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, sender_id: str, message_type: MessageType, content: Dict[str, Any], 
               receiver_id: Optional[str] = None, correlation_id: Optional[str] = None) -> 'A2AMessage':
        """Cria uma nova mensagem A2A"""
        return cls(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            correlation_id=correlation_id,
            metadata={}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte mensagem para dicionário"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Cria mensagem a partir de dicionário"""
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)

class A2AProtocol:
    """Protocolo de comunicação Agent-to-Agent"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self.connected_agents: Dict[str, 'A2AAgent'] = {}
        self.message_history: List[A2AMessage] = []
        
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Registra um handler para um tipo de mensagem"""
        self.message_handlers[message_type].append(handler)
    
    def connect_agent(self, agent: 'A2AAgent'):
        """Conecta outro agente para comunicação"""
        self.connected_agents[agent.agent_id] = agent
        
    def disconnect_agent(self, agent_id: str):
        """Desconecta um agente"""
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]
    
    def send_message(self, message: A2AMessage) -> bool:
        """Envia mensagem para outro agente"""
        try:
            if message.receiver_id and message.receiver_id in self.connected_agents:
                target_agent = self.connected_agents[message.receiver_id]
                target_agent.receive_message(message)
                self.message_history.append(message)
                return True
            elif message.message_type == MessageType.BROADCAST:
                # Broadcast para todos os agentes conectados
                for agent in self.connected_agents.values():
                    agent.receive_message(message)
                self.message_history.append(message)
                return True
            return False
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False
    
    def receive_message(self, message: A2AMessage):
        """Recebe e processa mensagem"""
        self.message_history.append(message)
        
        # Executa handlers registrados
        for handler in self.message_handlers[message.message_type]:
            try:
                handler(message)
            except Exception as e:
                print(f"Erro no handler: {e}")
    
    def create_request(self, receiver_id: str, action: str, params: Dict[str, Any]) -> A2AMessage:
        """Cria uma mensagem de requisição"""
        return A2AMessage.create(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            content={
                "action": action,
                "params": params
            }
        )
    
    def create_response(self, original_message: A2AMessage, result: Any, success: bool = True) -> A2AMessage:
        """Cria uma mensagem de resposta"""
        return A2AMessage.create(
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "result": result,
                "success": success
            },
            correlation_id=original_message.id
        )
    
    def broadcast(self, content: Dict[str, Any]) -> A2AMessage:
        """Cria uma mensagem de broadcast"""
        message = A2AMessage.create(
            sender_id=self.agent_id,
            message_type=MessageType.BROADCAST,
            content=content
        )
        self.send_message(message)
        return message

class A2AAgent:
    """Agente base com capacidades A2A"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.a2a_protocol = A2AProtocol(agent_id)
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """Configura handlers padrão"""
        self.a2a_protocol.register_handler(MessageType.REQUEST, self.handle_request)
        self.a2a_protocol.register_handler(MessageType.RESPONSE, self.handle_response)
        self.a2a_protocol.register_handler(MessageType.NOTIFICATION, self.handle_notification)
    
    def handle_request(self, message: A2AMessage):
        """Handler padrão para requisições"""
        action = message.content.get("action")
        params = message.content.get("params", {})
        
        # Implementar lógica específica do agente aqui
        result = f"Ação '{action}' processada pelo agente {self.agent_id}"
        
        response = self.a2a_protocol.create_response(message, result)
        self.a2a_protocol.send_message(response)
    
    def handle_response(self, message: A2AMessage):
        """Handler padrão para respostas"""
        print(f"Resposta recebida de {message.sender_id}: {message.content}")
    
    def handle_notification(self, message: A2AMessage):
        """Handler padrão para notificações"""
        print(f"Notificação de {message.sender_id}: {message.content}")
    
    def receive_message(self, message: A2AMessage):
        """Recebe mensagem via protocolo A2A"""
        self.a2a_protocol.receive_message(message)
    
    def connect_to(self, other_agent: 'A2AAgent'):
        """Conecta-se a outro agente"""
        self.a2a_protocol.connect_agent(other_agent)
        other_agent.a2a_protocol.connect_agent(self)
    
    def send_request(self, receiver_id: str, action: str, params: Dict[str, Any]):
        """Envia requisição para outro agente"""
        message = self.a2a_protocol.create_request(receiver_id, action, params)
        return self.a2a_protocol.send_message(message)
    
    def notify_all(self, content: Dict[str, Any]):
        """Envia notificação para todos os agentes conectados"""
        return self.a2a_protocol.broadcast(content)