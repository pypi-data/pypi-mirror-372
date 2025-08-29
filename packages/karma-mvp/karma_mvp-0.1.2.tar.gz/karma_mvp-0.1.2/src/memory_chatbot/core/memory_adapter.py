"""Memory adapter abstractions for unified memory management."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging


class MemoryAdapter(ABC):
    """
    Abstract base class for memory adapters.
    
    Defines a unified interface for different memory storage backends,
    allowing seamless switching between legacy YAML-based storage
    and modern semantic memory systems like Mem0.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the memory adapter with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def store_preference(self, user_id: str, preference: Dict[str, Any]) -> str:
        """
        Store a user preference.
        
        Args:
            user_id: Unique user identifier
            preference: Preference data to store
            
        Returns:
            Memory ID or reference for the stored preference
        """
        pass
    
    @abstractmethod
    def retrieve_preferences(self, user_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve user preferences.
        
        Args:
            user_id: Unique user identifier
            query: Optional query to filter preferences
            
        Returns:
            List of relevant preferences
        """
        pass
    
    @abstractmethod
    def store_workspace_knowledge(self, workspace_id: str, knowledge: Dict[str, Any]) -> str:
        """
        Store workspace-specific knowledge.
        
        Args:
            workspace_id: Unique workspace identifier
            knowledge: Knowledge data to store
            
        Returns:
            Memory ID or reference for the stored knowledge
        """
        pass
    
    @abstractmethod
    def retrieve_workspace_knowledge(self, workspace_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve workspace knowledge.
        
        Args:
            workspace_id: Unique workspace identifier
            query: Optional query to filter knowledge
            
        Returns:
            List of relevant knowledge items
        """
        pass
    
    @abstractmethod
    def store_conversation_memory(self, session_id: str, memory: Dict[str, Any]) -> str:
        """
        Store conversation-derived memory.
        
        Args:
            session_id: Unique session identifier
            memory: Memory data extracted from conversation
            
        Returns:
            Memory ID or reference for the stored memory
        """
        pass
    
    @abstractmethod
    def retrieve_conversation_memories(self, session_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation memories.
        
        Args:
            session_id: Unique session identifier
            query: Optional query to filter memories
            
        Returns:
            List of relevant conversation memories
        """
        pass
    
    @abstractmethod
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing memory.
        
        Args:
            memory_id: Unique memory identifier
            data: Updated memory data
            
        Returns:
            Updated memory data
        """
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Unique memory identifier
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def search_memories(self, query: str, scope: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search across all memories.
        
        Args:
            query: Search query
            scope: Optional scope filter (global, workspace, session)
            limit: Maximum number of results
            
        Returns:
            List of relevant memories
        """
        pass
    
    @abstractmethod
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the memory adapter.
        
        Returns:
            Health check results
        """
        pass
    
    def extract_insights_from_conversation(self, messages: List[Dict[str, str]], 
                                         context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extract insights from conversation messages.
        
        This is a common method that can be overridden by implementations
        but provides a basic framework.
        
        Args:
            messages: List of conversation messages
            context: Optional context information
            
        Returns:
            List of extracted insights
        """
        insights = []
        
        # Default implementation - extract basic patterns
        for i, message in enumerate(messages):
            if message.get('role') == 'user':
                # Look for preference indicators
                content = message.get('content', '').lower()
                
                # Simple pattern matching for preferences
                if any(keyword in content for keyword in ['i prefer', 'i like', 'i don\'t like', 'i hate']):
                    insights.append({
                        'type': 'preference',
                        'content': message.get('content'),
                        'confidence': 0.7,
                        'extracted_at': datetime.now().isoformat(),
                        'message_index': i
                    })
                
                # Look for factual information
                if any(keyword in content for keyword in ['my name is', 'i am', 'i work at', 'i use']):
                    insights.append({
                        'type': 'fact',
                        'content': message.get('content'),
                        'confidence': 0.8,
                        'extracted_at': datetime.now().isoformat(),
                        'message_index': i
                    })
        
        return insights


class MemoryAdapterError(Exception):
    """Base exception for memory adapter errors."""
    pass


class MemoryAdapterConfigError(MemoryAdapterError):
    """Configuration-related memory adapter errors."""
    pass


class MemoryAdapterStorageError(MemoryAdapterError):
    """Storage-related memory adapter errors."""
    pass


class MemoryAdapterRetrievalError(MemoryAdapterError):
    """Retrieval-related memory adapter errors."""
    pass