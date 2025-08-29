"""Mem0 provider for semantic memory management."""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    from mem0 import Memory
except ImportError:
    Memory = None

from .base import LLMProvider


class Mem0ProviderError(Exception):
    """Mem0 provider related errors."""
    pass


class Mem0Provider:
    """
    Provider for Mem0 semantic memory management.
    
    Handles initialization, configuration, and basic operations
    for Mem0 memory storage and retrieval.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Mem0 provider with configuration."""
        if Memory is None:
            raise Mem0ProviderError(
                "mem0ai package not installed. Install with: pip install mem0ai"
            )
        
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Default configuration - use minimal config to avoid initialization issues
        self.default_config = {
            "version": "v1.1"
        }
        
        # Merge with provided config
        self.mem0_config = {**self.default_config, **self.config}
        
        # Initialize memory client
        self.memory_client = None
        # Don't auto-initialize to avoid configuration errors in testing
    
    def initialize_client(self, full_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the Mem0 memory client with full configuration."""
        if full_config:
            self.mem0_config.update(full_config)
            
        try:
            self.memory_client = Memory(config=self.mem0_config)
            self.logger.info("Mem0 client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Mem0 client: {e}")
            raise Mem0ProviderError(f"Failed to initialize Mem0: {e}")
    
    def _initialize_client(self) -> None:
        """Legacy initialization method - calls initialize_client."""
        self.initialize_client()
    
    def add_memory(self, messages: List[Dict[str, str]], 
                   user_id: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add memory from conversation messages.
        
        Args:
            messages: List of conversation messages
            user_id: Unique user identifier
            metadata: Additional metadata for the memory
            
        Returns:
            Memory ID of the stored memory
        """
        if not self.memory_client:
            raise Mem0ProviderError("Mem0 client not initialized")
        
        try:
            # Add timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata["timestamp"] = datetime.now().isoformat()
            
            result = self.memory_client.add(
                messages=messages,
                user_id=user_id,
                metadata=metadata
            )
            
            self.logger.info(f"Added memory for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            raise Mem0ProviderError(f"Failed to add memory: {e}")
    
    def search_memory(self, query: str, 
                      user_id: str,
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum number of results
            
        Returns:
            List of relevant memories
        """
        if not self.memory_client:
            raise Mem0ProviderError("Mem0 client not initialized")
        
        try:
            results = self.memory_client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            self.logger.info(f"Found {len(results)} memories for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memory: {e}")
            raise Mem0ProviderError(f"Failed to search memory: {e}")
    
    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of all user memories
        """
        if not self.memory_client:
            raise Mem0ProviderError("Mem0 client not initialized")
        
        try:
            memories = self.memory_client.get_all(user_id=user_id)
            self.logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to get memories: {e}")
            raise Mem0ProviderError(f"Failed to get memories: {e}")
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of memory to update
            data: New data for the memory
            
        Returns:
            Updated memory data
        """
        if not self.memory_client:
            raise Mem0ProviderError("Mem0 client not initialized")
        
        try:
            result = self.memory_client.update(memory_id=memory_id, data=data)
            self.logger.info(f"Updated memory {memory_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            raise Mem0ProviderError(f"Failed to update memory: {e}")
    
    def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of memory to delete
        """
        if not self.memory_client:
            raise Mem0ProviderError("Mem0 client not initialized")
        
        try:
            self.memory_client.delete(memory_id=memory_id)
            self.logger.info(f"Deleted memory {memory_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            raise Mem0ProviderError(f"Failed to delete memory: {e}")
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with memory statistics
        """
        try:
            memories = self.get_all_memories(user_id)
            return {
                "total_memories": len(memories),
                "user_id": user_id,
                "last_updated": datetime.now().isoformat(),
                "config_version": self.mem0_config.get("version", "unknown")
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the Mem0 provider.
        
        Returns:
            Health check results
        """
        health_status = {
            "status": "unknown",
            "client_initialized": self.memory_client is not None,
            "config_version": self.mem0_config.get("version", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Try a simple operation
            if self.memory_client:
                # Test with a dummy user - this should not fail if service is healthy
                test_result = self.get_memory_stats("health_check_test_user")
                health_status["status"] = "healthy"
                health_status["test_result"] = "passed"
            else:
                health_status["status"] = "unhealthy"
                health_status["error"] = "Client not initialized"
                
        except Exception as e:
            health_status["status"] = "unhealthy" 
            health_status["error"] = str(e)
            self.logger.warning(f"Mem0 health check failed: {e}")
        
        return health_status


def create_mem0_provider(config: Optional[Dict[str, Any]] = None) -> Mem0Provider:
    """
    Factory function to create a Mem0Provider instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Mem0Provider instance
    """
    return Mem0Provider(config=config)


# Environment variable validation
def validate_environment() -> Dict[str, bool]:
    """
    Validate required environment variables for Mem0.
    
    Returns:
        Dictionary with validation results
    """
    required_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY") is not None,
        "NEO4J_URL": os.getenv("NEO4J_URL") is not None,
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME") is not None, 
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD") is not None,
        "QDRANT_HOST": os.getenv("QDRANT_HOST") is not None,
        "QDRANT_PORT": os.getenv("QDRANT_PORT") is not None,
    }
    
    return required_vars