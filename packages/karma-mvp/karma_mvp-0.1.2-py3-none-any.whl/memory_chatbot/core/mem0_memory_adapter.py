"""Mem0-based memory adapter for semantic memory management."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from .memory_adapter import MemoryAdapter, MemoryAdapterError, MemoryAdapterStorageError, MemoryAdapterRetrievalError
from ..providers.mem0_provider import Mem0Provider, Mem0ProviderError


class Mem0MemoryAdapter(MemoryAdapter):
    """
    Mem0-based memory adapter for semantic memory management.
    
    This adapter leverages Mem0's semantic capabilities for intelligent
    memory storage, retrieval, and relationship discovery.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Mem0 memory adapter."""
        super().__init__(config)
        
        # Initialize Mem0 provider
        self.mem0_provider = Mem0Provider(config)
        
        # Memory type prefixes for organization
        self.memory_prefixes = {
            'preference': 'pref',
            'workspace': 'ws',
            'conversation': 'conv',
            'fact': 'fact',
            'insight': 'insight'
        }
        
        # Initialize client if configuration is provided
        if config and 'llm' in config:
            try:
                self.mem0_provider.initialize_client(config)
                self.logger.info("Mem0 client initialized successfully")
            except Mem0ProviderError as e:
                self.logger.warning(f"Mem0 client initialization deferred: {e}")
    
    def _ensure_initialized(self) -> None:
        """Ensure Mem0 client is initialized."""
        if not self.mem0_provider.memory_client:
            raise MemoryAdapterError("Mem0 client not initialized. Call initialize_client() first.")
    
    def initialize_client(self, full_config: Dict[str, Any]) -> None:
        """Initialize the Mem0 client with full configuration."""
        try:
            self.mem0_provider.initialize_client(full_config)
            self.logger.info("Mem0 memory adapter initialized successfully")
        except Mem0ProviderError as e:
            raise MemoryAdapterError(f"Failed to initialize Mem0 adapter: {e}")
    
    def _create_user_id(self, scope: str, identifier: str) -> str:
        """Create a scoped user ID for memory isolation."""
        return f"{scope}:{identifier}"
    
    def _create_memory_metadata(self, memory_type: str, scope: str, **extra_metadata) -> Dict[str, Any]:
        """Create standardized metadata for memory entries."""
        metadata = {
            'memory_type': memory_type,
            'scope': scope,
            'created_at': datetime.now().isoformat(),
            'adapter_version': 'mem0_v1.0',
            **extra_metadata
        }
        return metadata
    
    def store_preference(self, user_id: str, preference: Dict[str, Any]) -> str:
        """Store a user preference using Mem0's semantic understanding."""
        self._ensure_initialized()
        
        try:
            # Create preference messages for semantic understanding
            pref_content = preference.get('content', '')
            pref_type = preference.get('type', 'general')
            confidence = preference.get('confidence', 0.7)
            
            messages = [
                {
                    "role": "user",
                    "content": f"Remember this preference: {pref_content}"
                },
                {
                    "role": "assistant", 
                    "content": f"I've noted your {pref_type} preference. I'll remember this for future interactions."
                }
            ]
            
            # Create metadata
            metadata = self._create_memory_metadata(
                memory_type='preference',
                scope='global',
                preference_type=pref_type,
                confidence=confidence,
                user_preference=True
            )
            
            # Store using Mem0
            scoped_user_id = self._create_user_id('global', user_id)
            result = self.mem0_provider.add_memory(
                messages=messages,
                user_id=scoped_user_id,
                metadata=metadata
            )
            
            self.logger.info(f"Stored preference for user {user_id}: {pref_type}")
            return f"mem0_pref_{result.get('memory_id', 'unknown')}"
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to store preference: {e}")
            raise MemoryAdapterStorageError(f"Failed to store preference: {e}")
    
    def retrieve_preferences(self, user_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve user preferences using semantic search."""
        self._ensure_initialized()
        
        try:
            scoped_user_id = self._create_user_id('global', user_id)
            
            if query:
                # Use semantic search
                memories = self.mem0_provider.search_memory(
                    query=f"preferences about {query}",
                    user_id=scoped_user_id,
                    limit=20
                )
            else:
                # Get all preferences
                all_memories = self.mem0_provider.get_all_memories(scoped_user_id)
                # Filter for preferences
                memories = [
                    mem for mem in all_memories 
                    if mem.get('metadata', {}).get('memory_type') == 'preference'
                ]
            
            # Format for adapter interface
            preferences = []
            for memory in memories:
                preferences.append({
                    'id': memory.get('id'),
                    'type': memory.get('metadata', {}).get('preference_type', 'general'),
                    'content': memory.get('text', ''),
                    'confidence': memory.get('metadata', {}).get('confidence', 0.5),
                    'created_at': memory.get('metadata', {}).get('created_at'),
                    'source': 'mem0_semantic',
                    'metadata': memory.get('metadata', {})
                })
            
            self.logger.info(f"Retrieved {len(preferences)} preferences for user {user_id}")
            return preferences
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to retrieve preferences: {e}")
            raise MemoryAdapterRetrievalError(f"Failed to retrieve preferences: {e}")
    
    def store_workspace_knowledge(self, workspace_id: str, knowledge: Dict[str, Any]) -> str:
        """Store workspace-specific knowledge with semantic understanding."""
        self._ensure_initialized()
        
        try:
            knowledge_content = knowledge.get('content', '')
            knowledge_type = knowledge.get('type', 'general')
            confidence = knowledge.get('confidence', 0.7)
            
            # Create knowledge messages
            messages = [
                {
                    "role": "user",
                    "content": f"In this {workspace_id} project: {knowledge_content}"
                },
                {
                    "role": "assistant",
                    "content": f"I've learned this {knowledge_type} knowledge about the {workspace_id} project. I'll apply this context in future discussions."
                }
            ]
            
            # Create metadata
            metadata = self._create_memory_metadata(
                memory_type='workspace_knowledge',
                scope='workspace',
                workspace_id=workspace_id,
                knowledge_type=knowledge_type,
                confidence=confidence
            )
            
            # Store using Mem0
            scoped_user_id = self._create_user_id('workspace', workspace_id)
            result = self.mem0_provider.add_memory(
                messages=messages,
                user_id=scoped_user_id,
                metadata=metadata
            )
            
            self.logger.info(f"Stored knowledge for workspace {workspace_id}: {knowledge_type}")
            return f"mem0_ws_{result.get('memory_id', 'unknown')}"
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to store workspace knowledge: {e}")
            raise MemoryAdapterStorageError(f"Failed to store workspace knowledge: {e}")
    
    def retrieve_workspace_knowledge(self, workspace_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve workspace knowledge using semantic search."""
        self._ensure_initialized()
        
        try:
            scoped_user_id = self._create_user_id('workspace', workspace_id)
            
            if query:
                # Use semantic search
                memories = self.mem0_provider.search_memory(
                    query=f"knowledge about {query} in {workspace_id}",
                    user_id=scoped_user_id,
                    limit=20
                )
            else:
                # Get all workspace knowledge
                all_memories = self.mem0_provider.get_all_memories(scoped_user_id)
                # Filter for workspace knowledge
                memories = [
                    mem for mem in all_memories 
                    if mem.get('metadata', {}).get('memory_type') == 'workspace_knowledge'
                ]
            
            # Format for adapter interface
            knowledge_items = []
            for memory in memories:
                knowledge_items.append({
                    'id': memory.get('id'),
                    'type': memory.get('metadata', {}).get('knowledge_type', 'general'),
                    'content': memory.get('text', ''),
                    'confidence': memory.get('metadata', {}).get('confidence', 0.5),
                    'created_at': memory.get('metadata', {}).get('created_at'),
                    'workspace_id': workspace_id,
                    'source': 'mem0_semantic',
                    'metadata': memory.get('metadata', {})
                })
            
            self.logger.info(f"Retrieved {len(knowledge_items)} knowledge items for workspace {workspace_id}")
            return knowledge_items
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to retrieve workspace knowledge: {e}")
            raise MemoryAdapterRetrievalError(f"Failed to retrieve workspace knowledge: {e}")
    
    def store_conversation_memory(self, session_id: str, memory: Dict[str, Any]) -> str:
        """Store conversation-derived memory with semantic extraction."""
        self._ensure_initialized()
        
        try:
            # Extract conversation messages if provided
            messages = memory.get('messages', [])
            if not messages and 'content' in memory:
                # Create messages from content
                messages = [
                    {
                        "role": "user",
                        "content": str(memory['content'])
                    }
                ]
            
            if not messages:
                raise MemoryAdapterStorageError("No messages or content provided for conversation memory")
            
            # Create metadata
            metadata = self._create_memory_metadata(
                memory_type='conversation',
                scope='session',
                session_id=session_id,
                extracted_insights=memory.get('extracted_insights', []),
                confidence=memory.get('confidence', 0.5)
            )
            
            # Store using Mem0
            scoped_user_id = self._create_user_id('session', session_id)
            result = self.mem0_provider.add_memory(
                messages=messages,
                user_id=scoped_user_id,
                metadata=metadata
            )
            
            self.logger.info(f"Stored conversation memory for session {session_id}")
            return f"mem0_conv_{result.get('memory_id', 'unknown')}"
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to store conversation memory: {e}")
            raise MemoryAdapterStorageError(f"Failed to store conversation memory: {e}")
    
    def retrieve_conversation_memories(self, session_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve conversation memories using semantic search."""
        self._ensure_initialized()
        
        try:
            scoped_user_id = self._create_user_id('session', session_id)
            
            if query:
                # Use semantic search
                memories = self.mem0_provider.search_memory(
                    query=query,
                    user_id=scoped_user_id,
                    limit=20
                )
            else:
                # Get all session memories
                all_memories = self.mem0_provider.get_all_memories(scoped_user_id)
                # Filter for conversation memories
                memories = [
                    mem for mem in all_memories 
                    if mem.get('metadata', {}).get('memory_type') == 'conversation'
                ]
            
            # Format for adapter interface
            conversation_memories = []
            for memory in memories:
                conversation_memories.append({
                    'id': memory.get('id'),
                    'type': 'conversation',
                    'content': memory.get('text', ''),
                    'confidence': memory.get('metadata', {}).get('confidence', 0.5),
                    'created_at': memory.get('metadata', {}).get('created_at'),
                    'session_id': session_id,
                    'source': 'mem0_semantic',
                    'extracted_insights': memory.get('metadata', {}).get('extracted_insights', []),
                    'metadata': memory.get('metadata', {})
                })
            
            self.logger.info(f"Retrieved {len(conversation_memories)} conversation memories for session {session_id}")
            return conversation_memories
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to retrieve conversation memories: {e}")
            raise MemoryAdapterRetrievalError(f"Failed to retrieve conversation memories: {e}")
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing memory using Mem0."""
        self._ensure_initialized()
        
        try:
            # Update memory using Mem0
            result = self.mem0_provider.update_memory(memory_id, data)
            
            self.logger.info(f"Updated memory {memory_id}")
            return result
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to update memory: {e}")
            raise MemoryAdapterError(f"Failed to update memory: {e}")
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory using Mem0."""
        self._ensure_initialized()
        
        try:
            self.mem0_provider.delete_memory(memory_id)
            self.logger.info(f"Deleted memory {memory_id}")
            return True
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False
    
    def search_memories(self, query: str, scope: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search across all memories using Mem0's semantic search."""
        self._ensure_initialized()
        
        try:
            all_memories = []
            
            if scope is None or scope == 'global':
                # Search global preferences
                try:
                    global_memories = self.mem0_provider.search_memory(
                        query=query,
                        user_id=self._create_user_id('global', 'default_user'),
                        limit=limit // 3
                    )
                    for mem in global_memories:
                        mem['search_scope'] = 'global'
                        all_memories.append(mem)
                except Exception as e:
                    self.logger.warning(f"Failed to search global memories: {e}")
            
            if scope is None or scope == 'workspace':
                # Search workspace knowledge - Note: this is simplified
                # In practice, you'd want to search specific workspaces
                try:
                    # For now, search a default workspace scope
                    workspace_memories = self.mem0_provider.search_memory(
                        query=query,
                        user_id=self._create_user_id('workspace', 'current'),
                        limit=limit // 3
                    )
                    for mem in workspace_memories:
                        mem['search_scope'] = 'workspace'
                        all_memories.append(mem)
                except Exception as e:
                    self.logger.warning(f"Failed to search workspace memories: {e}")
            
            if scope is None or scope == 'session':
                # Search session memories - Note: this is simplified
                try:
                    session_memories = self.mem0_provider.search_memory(
                        query=query,
                        user_id=self._create_user_id('session', 'current'),
                        limit=limit // 3
                    )
                    for mem in session_memories:
                        mem['search_scope'] = 'session'
                        all_memories.append(mem)
                except Exception as e:
                    self.logger.warning(f"Failed to search session memories: {e}")
            
            # Sort by relevance (Mem0 provides relevance scoring)
            all_memories = sorted(
                all_memories, 
                key=lambda x: x.get('score', x.get('relevance', 0)), 
                reverse=True
            )
            
            # Format for adapter interface
            formatted_memories = []
            for memory in all_memories[:limit]:
                formatted_memories.append({
                    'id': memory.get('id'),
                    'content': memory.get('text', ''),
                    'relevance_score': memory.get('score', memory.get('relevance', 0)),
                    'scope': memory.get('search_scope', 'unknown'),
                    'source': 'mem0_semantic',
                    'metadata': memory.get('metadata', {})
                })
            
            self.logger.info(f"Found {len(formatted_memories)} memories for query: {query}")
            return formatted_memories
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to search memories: {e}")
            raise MemoryAdapterRetrievalError(f"Failed to search memories: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics from Mem0."""
        try:
            # Get basic stats from Mem0 provider
            mem0_stats = self.mem0_provider.get_memory_stats('default_user')
            
            stats = {
                'adapter_type': 'mem0_semantic',
                'mem0_client_initialized': self.mem0_provider.memory_client is not None,
                'timestamp': datetime.now().isoformat(),
                **mem0_stats
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {
                'error': str(e),
                'adapter_type': 'mem0_semantic',
                'timestamp': datetime.now().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the Mem0 adapter."""
        health = {
            'status': 'unknown',
            'adapter_type': 'mem0_semantic',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Use Mem0 provider health check
            mem0_health = self.mem0_provider.health_check()
            health.update(mem0_health)
            
            # Additional adapter-specific checks
            health['memory_prefixes'] = list(self.memory_prefixes.keys())
            health['scoping_enabled'] = True
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    def extract_insights_from_conversation(self, messages: List[Dict[str, str]], 
                                         context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Enhanced insight extraction using Mem0's semantic capabilities.
        
        This leverages Mem0's built-in extraction rather than simple pattern matching.
        """
        self._ensure_initialized()
        
        try:
            # Use a temporary session for extraction
            temp_session_id = f"extract_{datetime.now().timestamp()}"
            scoped_user_id = self._create_user_id('extraction', temp_session_id)
            
            # Store conversation temporarily for extraction
            metadata = self._create_memory_metadata(
                memory_type='extraction_temp',
                scope='extraction',
                context=context or {}
            )
            
            result = self.mem0_provider.add_memory(
                messages=messages,
                user_id=scoped_user_id,
                metadata=metadata
            )
            
            # Extract insights from the stored memory
            # Note: This is a simplified approach - Mem0's actual extraction
            # happens during the add_memory call
            insights = []
            
            if result and 'results' in result:
                for memory_entry in result['results']:
                    insights.append({
                        'type': 'semantic_insight',
                        'content': memory_entry.get('text', ''),
                        'confidence': 0.8,  # Mem0's extraction is generally high confidence
                        'extracted_at': datetime.now().isoformat(),
                        'source': 'mem0_semantic',
                        'memory_id': memory_entry.get('id')
                    })
            
            # Clean up temporary memory if needed
            try:
                # Get all extraction memories and clean them up
                extraction_memories = self.mem0_provider.get_all_memories(scoped_user_id)
                for memory in extraction_memories:
                    self.mem0_provider.delete_memory(memory.get('id'))
            except Exception as cleanup_error:
                self.logger.warning(f"Failed to cleanup extraction memories: {cleanup_error}")
            
            self.logger.info(f"Extracted {len(insights)} insights using Mem0 semantic analysis")
            return insights
            
        except Mem0ProviderError as e:
            self.logger.error(f"Failed to extract insights: {e}")
            # Fallback to parent class implementation
            return super().extract_insights_from_conversation(messages, context)