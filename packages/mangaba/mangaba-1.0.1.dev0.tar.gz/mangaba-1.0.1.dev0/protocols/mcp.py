"""Protocolo MCP (Model Context Protocol) para gerenciamento de contexto avançado"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class ContextType(Enum):
    """Tipos de contexto MCP"""
    CONVERSATION = "conversation"
    TASK = "task"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    SYSTEM = "system"
    USER_PROFILE = "user_profile"

class ContextPriority(Enum):
    """Prioridades de contexto"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MCPContext:
    """Contexto individual no protocolo MCP"""
    id: str
    context_type: ContextType
    content: Dict[str, Any]
    priority: ContextPriority
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.children_ids is None:
            self.children_ids = []
    
    @classmethod
    def create(cls, context_type: ContextType, content: Dict[str, Any], 
               priority: ContextPriority = ContextPriority.MEDIUM,
               expires_in_hours: Optional[int] = None,
               tags: List[str] = None,
               parent_id: Optional[str] = None) -> 'MCPContext':
        """Cria um novo contexto MCP"""
        now = datetime.now().isoformat()
        expires_at = None
        if expires_in_hours:
            expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
        
        return cls(
            id=str(uuid.uuid4()),
            context_type=context_type,
            content=content,
            priority=priority,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            tags=tags or [],
            parent_id=parent_id
        )
    
    def update_content(self, new_content: Dict[str, Any]):
        """Atualiza o conteúdo do contexto"""
        self.content.update(new_content)
        self.updated_at = datetime.now().isoformat()
    
    def add_tag(self, tag: str):
        """Adiciona uma tag ao contexto"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """Verifica se o contexto expirou"""
        if not self.expires_at:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)
    
    def get_hash(self) -> str:
        """Gera hash do conteúdo para detecção de mudanças"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte contexto para dicionário"""
        data = asdict(self)
        data['context_type'] = self.context_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPContext':
        """Cria contexto a partir de dicionário"""
        data['context_type'] = ContextType(data['context_type'])
        data['priority'] = ContextPriority(data['priority'])
        return cls(**data)

@dataclass
class MCPSession:
    """Sessão MCP para agrupamento de contextos"""
    id: str
    name: str
    created_at: str
    updated_at: str
    context_ids: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def create(cls, name: str) -> 'MCPSession':
        """Cria uma nova sessão MCP"""
        now = datetime.now().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            created_at=now,
            updated_at=now,
            context_ids=[]
        )

class MCPProtocol:
    """Protocolo de gerenciamento de contexto MCP"""
    
    def __init__(self, max_contexts: int = 1000):
        self.contexts: Dict[str, MCPContext] = {}
        self.sessions: Dict[str, MCPSession] = {}
        self.max_contexts = max_contexts
        self.context_index: Dict[str, List[str]] = {}  # tag -> context_ids
        
    def add_context(self, context: MCPContext, session_id: Optional[str] = None) -> str:
        """Adiciona um contexto ao protocolo MCP"""
        # Remove contextos expirados se necessário
        self._cleanup_expired_contexts()
        
        # Remove contextos antigos se exceder o limite
        if len(self.contexts) >= self.max_contexts:
            self._remove_oldest_contexts()
        
        self.contexts[context.id] = context
        
        # Adiciona à sessão se especificada
        if session_id and session_id in self.sessions:
            self.sessions[session_id].context_ids.append(context.id)
            self.sessions[session_id].updated_at = datetime.now().isoformat()
        
        # Atualiza índice de tags
        for tag in context.tags:
            if tag not in self.context_index:
                self.context_index[tag] = []
            self.context_index[tag].append(context.id)
        
        return context.id
    
    def get_context(self, context_id: str) -> Optional[MCPContext]:
        """Recupera um contexto pelo ID"""
        context = self.contexts.get(context_id)
        if context and context.is_expired():
            self.remove_context(context_id)
            return None
        return context
    
    def update_context(self, context_id: str, new_content: Dict[str, Any]) -> bool:
        """Atualiza o conteúdo de um contexto"""
        context = self.get_context(context_id)
        if context:
            context.update_content(new_content)
            return True
        return False
    
    def remove_context(self, context_id: str) -> bool:
        """Remove um contexto"""
        if context_id in self.contexts:
            context = self.contexts[context_id]
            
            # Remove das tags
            for tag in context.tags:
                if tag in self.context_index:
                    self.context_index[tag] = [cid for cid in self.context_index[tag] if cid != context_id]
                    if not self.context_index[tag]:
                        del self.context_index[tag]
            
            # Remove das sessões
            for session in self.sessions.values():
                if context_id in session.context_ids:
                    session.context_ids.remove(context_id)
                    session.updated_at = datetime.now().isoformat()
            
            del self.contexts[context_id]
            return True
        return False
    
    def find_contexts_by_tag(self, tag: str) -> List[MCPContext]:
        """Encontra contextos por tag"""
        context_ids = self.context_index.get(tag, [])
        return [self.get_context(cid) for cid in context_ids if self.get_context(cid)]
    
    def find_contexts_by_type(self, context_type: ContextType) -> List[MCPContext]:
        """Encontra contextos por tipo"""
        return [ctx for ctx in self.contexts.values() if ctx.context_type == context_type and not ctx.is_expired()]
    
    def find_contexts_by_priority(self, min_priority: ContextPriority) -> List[MCPContext]:
        """Encontra contextos por prioridade mínima"""
        return [ctx for ctx in self.contexts.values() 
                if ctx.priority.value >= min_priority.value and not ctx.is_expired()]
    
    def create_session(self, name: str) -> str:
        """Cria uma nova sessão"""
        session = MCPSession.create(name)
        self.sessions[session.id] = session
        return session.id
    
    def get_session_contexts(self, session_id: str) -> List[MCPContext]:
        """Recupera todos os contextos de uma sessão"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [self.get_context(cid) for cid in session.context_ids if self.get_context(cid)]
    
    def get_relevant_contexts(self, query: str, max_results: int = 10) -> List[MCPContext]:
        """Encontra contextos relevantes para uma query (busca simples por palavras-chave)"""
        query_words = query.lower().split()
        scored_contexts = []
        
        for context in self.contexts.values():
            if context.is_expired():
                continue
                
            score = 0
            content_str = json.dumps(context.content).lower()
            
            # Pontuação por palavras-chave no conteúdo
            for word in query_words:
                score += content_str.count(word)
            
            # Pontuação por tags
            for tag in context.tags:
                if any(word in tag.lower() for word in query_words):
                    score += 2
            
            # Pontuação por prioridade
            score += context.priority.value
            
            if score > 0:
                scored_contexts.append((score, context))
        
        # Ordena por pontuação e retorna os melhores
        scored_contexts.sort(key=lambda x: x[0], reverse=True)
        return [ctx for _, ctx in scored_contexts[:max_results]]
    
    def _cleanup_expired_contexts(self):
        """Remove contextos expirados"""
        expired_ids = [cid for cid, ctx in self.contexts.items() if ctx.is_expired()]
        for cid in expired_ids:
            self.remove_context(cid)
    
    def _remove_oldest_contexts(self, count: int = 100):
        """Remove os contextos mais antigos"""
        # Ordena por data de criação e remove os mais antigos
        sorted_contexts = sorted(self.contexts.items(), key=lambda x: x[1].created_at)
        for i in range(min(count, len(sorted_contexts))):
            context_id = sorted_contexts[i][0]
            self.remove_context(context_id)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Retorna resumo do estado atual dos contextos"""
        type_counts = {}
        priority_counts = {}
        
        for context in self.contexts.values():
            if not context.is_expired():
                type_counts[context.context_type.value] = type_counts.get(context.context_type.value, 0) + 1
                priority_counts[context.priority.value] = priority_counts.get(context.priority.value, 0) + 1
        
        return {
            "total_contexts": len([ctx for ctx in self.contexts.values() if not ctx.is_expired()]),
            "total_sessions": len(self.sessions),
            "contexts_by_type": type_counts,
            "contexts_by_priority": priority_counts,
            "total_tags": len(self.context_index)
        }