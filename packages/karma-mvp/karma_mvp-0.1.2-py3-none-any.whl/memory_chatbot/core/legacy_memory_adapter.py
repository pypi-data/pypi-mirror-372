"""Legacy memory adapter that wraps existing YAML and SQLite functionality."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
import json
import os
from pathlib import Path

from .memory_adapter import MemoryAdapter, MemoryAdapterError, MemoryAdapterStorageError
from .global_memory import GlobalMemory, GlobalMemoryError
from .workspace_memory import WorkspaceMemory
try:
    from .workspace_memory import WorkspaceMemoryError
except ImportError:
    WorkspaceMemoryError = Exception
from .memory_extractor import MemoryExtractor
from ..config.loader import ConfigLoader


class LegacyMemoryAdapter(MemoryAdapter):
    """
    Legacy memory adapter that preserves existing YAML-based storage.
    
    This adapter wraps the existing GlobalMemory and WorkspaceMemory classes
    to provide backward compatibility while implementing the new adapter interface.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the legacy memory adapter."""
        super().__init__(config)
        
        # Initialize existing components
        self.config_loader = ConfigLoader()
        self.global_memory = GlobalMemory(self.config_loader)
        self.memory_extractor = MemoryExtractor()
        
        # Session database path
        self.session_db_path = self.config.get(
            'session_db_path', 
            os.path.expanduser('~/.memory-chatbot/sessions.db')
        )
        
        # Initialize session database
        self._init_session_db()
        
        # Cache for workspace memory instances
        self._workspace_memories: Dict[str, WorkspaceMemory] = {}
    
    def _init_session_db(self) -> None:
        """Initialize session database for conversation memories."""
        try:
            os.makedirs(os.path.dirname(self.session_db_path), exist_ok=True)
            
            with sqlite3.connect(self.session_db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        confidence REAL DEFAULT 0.5,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_memories 
                    ON conversation_memories(session_id, memory_type)
                ''')
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize session database: {e}")
            raise MemoryAdapterStorageError(f"Session database initialization failed: {e}")
    
    def _get_workspace_memory(self, workspace_id: str) -> WorkspaceMemory:
        """Get or create workspace memory instance."""
        if workspace_id not in self._workspace_memories:
            workspace_path = Path.cwd() / workspace_id if '/' not in workspace_id else Path(workspace_id)
            self._workspace_memories[workspace_id] = WorkspaceMemory(workspace_path, self.config_loader)
        
        return self._workspace_memories[workspace_id]
    
    def store_preference(self, user_id: str, preference: Dict[str, Any]) -> str:
        """Store a user preference in global memory."""
        try:
            config = self.global_memory.config
            
            # Extract preference details
            pref_type = preference.get('type', 'general')
            content = preference.get('content', '')
            confidence = preference.get('confidence', 0.7)
            
            # Create preference entry
            pref_entry = {
                'type': pref_type,
                'value': content,
                'confidence': confidence,
                'created_at': datetime.now().isoformat(),
                'metadata': preference.get('metadata', {})
            }
            
            # Add to user preferences based on type
            if pref_type == 'communication':
                if not hasattr(config.user_preferences, 'communication_style'):
                    config.user_preferences.communication_style = {}
                config.user_preferences.communication_style.update(pref_entry)
                
            elif pref_type == 'domain':
                domain = preference.get('domain', 'general')
                if not hasattr(config, 'domain_preferences'):
                    config.domain_preferences = {}
                if domain not in config.domain_preferences:
                    config.domain_preferences[domain] = {}
                config.domain_preferences[domain].update(pref_entry)
                
            else:
                # Store in general preferences
                if not hasattr(config.user_preferences, 'general'):
                    config.user_preferences.general = {}
                pref_id = f"pref_{datetime.now().timestamp()}"
                config.user_preferences.general[pref_id] = pref_entry
            
            # Save configuration
            self.global_memory.save()
            
            self.logger.info(f"Stored preference for user {user_id}: {pref_type}")
            return f"global_{pref_type}_{datetime.now().timestamp()}"
            
        except (GlobalMemoryError, Exception) as e:
            self.logger.error(f"Failed to store preference: {e}")
            raise MemoryAdapterStorageError(f"Failed to store preference: {e}")
    
    def retrieve_preferences(self, user_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve user preferences from global memory."""
        try:
            config = self.global_memory.config
            preferences = []
            
            # Extract communication style preferences
            if hasattr(config.user_preferences, 'communication_style'):
                comm_style = config.user_preferences.communication_style
                if isinstance(comm_style, dict):
                    preferences.append({
                        'id': 'communication_style',
                        'type': 'communication',
                        'content': comm_style,
                        'source': 'global'
                    })
            
            # Extract domain preferences
            if hasattr(config, 'domain_preferences'):
                for domain, prefs in config.domain_preferences.items():
                    preferences.append({
                        'id': f'domain_{domain}',
                        'type': 'domain',
                        'content': prefs,
                        'domain': domain,
                        'source': 'global'
                    })
            
            # Extract general preferences
            if hasattr(config.user_preferences, 'general'):
                for pref_id, pref_data in config.user_preferences.general.items():
                    preferences.append({
                        'id': pref_id,
                        'type': 'general',
                        'content': pref_data,
                        'source': 'global'
                    })
            
            # Filter by query if provided
            if query:
                query_lower = query.lower()
                preferences = [
                    pref for pref in preferences 
                    if query_lower in str(pref.get('content', '')).lower()
                ]
            
            self.logger.info(f"Retrieved {len(preferences)} preferences for user {user_id}")
            return preferences
            
        except (GlobalMemoryError, Exception) as e:
            self.logger.error(f"Failed to retrieve preferences: {e}")
            return []
    
    def store_workspace_knowledge(self, workspace_id: str, knowledge: Dict[str, Any]) -> str:
        """Store workspace-specific knowledge."""
        try:
            workspace_memory = self._get_workspace_memory(workspace_id)
            config = workspace_memory.config
            
            # Extract knowledge details
            knowledge_type = knowledge.get('type', 'general')
            content = knowledge.get('content', '')
            
            # Create knowledge entry
            knowledge_entry = {
                'content': content,
                'confidence': knowledge.get('confidence', 0.7),
                'created_at': datetime.now().isoformat(),
                'metadata': knowledge.get('metadata', {})
            }
            
            # Store based on type
            if knowledge_type == 'architecture':
                if not hasattr(config, 'architecture_decisions'):
                    config.architecture_decisions = []
                config.architecture_decisions.append(knowledge_entry)
                
            elif knowledge_type == 'best_practice':
                if not hasattr(config, 'best_practices'):
                    config.best_practices = []
                config.best_practices.append(knowledge_entry)
                
            else:
                # Store in general knowledge
                if not hasattr(config, 'general_knowledge'):
                    config.general_knowledge = []
                config.general_knowledge.append(knowledge_entry)
            
            # Save workspace configuration
            workspace_memory.save()
            
            knowledge_id = f"workspace_{workspace_id}_{knowledge_type}_{datetime.now().timestamp()}"
            self.logger.info(f"Stored knowledge for workspace {workspace_id}: {knowledge_type}")
            return knowledge_id
            
        except (WorkspaceMemoryError, Exception) as e:
            self.logger.error(f"Failed to store workspace knowledge: {e}")
            raise MemoryAdapterStorageError(f"Failed to store workspace knowledge: {e}")
    
    def retrieve_workspace_knowledge(self, workspace_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve workspace knowledge."""
        try:
            workspace_memory = self._get_workspace_memory(workspace_id)
            config = workspace_memory.config
            knowledge_items = []
            
            # Extract architecture decisions
            if hasattr(config, 'architecture_decisions'):
                for i, decision in enumerate(config.architecture_decisions):
                    knowledge_items.append({
                        'id': f'arch_{i}',
                        'type': 'architecture',
                        'content': decision,
                        'source': 'workspace',
                        'workspace_id': workspace_id
                    })
            
            # Extract best practices
            if hasattr(config, 'best_practices'):
                for i, practice in enumerate(config.best_practices):
                    knowledge_items.append({
                        'id': f'practice_{i}',
                        'type': 'best_practice',
                        'content': practice,
                        'source': 'workspace',
                        'workspace_id': workspace_id
                    })
            
            # Extract general knowledge
            if hasattr(config, 'general_knowledge'):
                for i, knowledge in enumerate(config.general_knowledge):
                    knowledge_items.append({
                        'id': f'general_{i}',
                        'type': 'general',
                        'content': knowledge,
                        'source': 'workspace',
                        'workspace_id': workspace_id
                    })
            
            # Filter by query if provided
            if query:
                query_lower = query.lower()
                knowledge_items = [
                    item for item in knowledge_items
                    if query_lower in str(item.get('content', '')).lower()
                ]
            
            self.logger.info(f"Retrieved {len(knowledge_items)} knowledge items for workspace {workspace_id}")
            return knowledge_items
            
        except (WorkspaceMemoryError, Exception) as e:
            self.logger.error(f"Failed to retrieve workspace knowledge: {e}")
            return []
    
    def store_conversation_memory(self, session_id: str, memory: Dict[str, Any]) -> str:
        """Store conversation-derived memory in SQLite."""
        try:
            memory_type = memory.get('type', 'general')
            content = json.dumps(memory.get('content', {}))
            confidence = memory.get('confidence', 0.5)
            metadata = json.dumps(memory.get('metadata', {}))
            
            with sqlite3.connect(self.session_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversation_memories 
                    (session_id, memory_type, content, confidence, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, memory_type, content, confidence, metadata))
                
                memory_id = cursor.lastrowid
                conn.commit()
            
            self.logger.info(f"Stored conversation memory for session {session_id}")
            return str(memory_id)
            
        except Exception as e:
            self.logger.error(f"Failed to store conversation memory: {e}")
            raise MemoryAdapterStorageError(f"Failed to store conversation memory: {e}")
    
    def retrieve_conversation_memories(self, session_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve conversation memories from SQLite."""
        try:
            with sqlite3.connect(self.session_db_path) as conn:
                cursor = conn.cursor()
                
                if query:
                    cursor.execute('''
                        SELECT id, memory_type, content, confidence, metadata, created_at
                        FROM conversation_memories 
                        WHERE session_id = ? AND content LIKE ?
                        ORDER BY created_at DESC
                    ''', (session_id, f'%{query}%'))
                else:
                    cursor.execute('''
                        SELECT id, memory_type, content, confidence, metadata, created_at
                        FROM conversation_memories 
                        WHERE session_id = ?
                        ORDER BY created_at DESC
                    ''', (session_id,))
                
                memories = []
                for row in cursor.fetchall():
                    memory_id, memory_type, content, confidence, metadata, created_at = row
                    
                    memories.append({
                        'id': str(memory_id),
                        'type': memory_type,
                        'content': json.loads(content),
                        'confidence': confidence,
                        'metadata': json.loads(metadata),
                        'created_at': created_at,
                        'source': 'conversation',
                        'session_id': session_id
                    })
                
                self.logger.info(f"Retrieved {len(memories)} conversation memories for session {session_id}")
                return memories
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation memories: {e}")
            return []
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing memory."""
        # For legacy adapter, this is limited since YAML doesn't have IDs
        # We'll implement basic update for conversation memories only
        try:
            if memory_id.isdigit():
                # This is likely a conversation memory ID
                with sqlite3.connect(self.session_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Update conversation memory
                    content = json.dumps(data.get('content', {}))
                    confidence = data.get('confidence')
                    metadata = json.dumps(data.get('metadata', {}))
                    
                    cursor.execute('''
                        UPDATE conversation_memories 
                        SET content = ?, confidence = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (content, confidence, metadata, int(memory_id)))
                    
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        self.logger.info(f"Updated conversation memory {memory_id}")
                        return {'id': memory_id, 'updated': True, **data}
            
            raise MemoryAdapterError(f"Cannot update memory {memory_id} - not supported in legacy mode")
            
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            raise MemoryAdapterError(f"Failed to update memory: {e}")
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        try:
            if memory_id.isdigit():
                # This is likely a conversation memory ID
                with sqlite3.connect(self.session_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM conversation_memories WHERE id = ?', (int(memory_id),))
                    conn.commit()
                    
                    success = cursor.rowcount > 0
                    if success:
                        self.logger.info(f"Deleted conversation memory {memory_id}")
                    return success
            
            self.logger.warning(f"Cannot delete memory {memory_id} - not supported in legacy mode")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False
    
    def search_memories(self, query: str, scope: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search across all memories."""
        all_memories = []
        
        # Search global preferences if scope allows
        if scope is None or scope == 'global':
            try:
                global_prefs = self.retrieve_preferences('default_user', query)
                all_memories.extend(global_prefs)
            except Exception as e:
                self.logger.warning(f"Failed to search global memories: {e}")
        
        # Search conversation memories if scope allows
        if scope is None or scope == 'session':
            try:
                with sqlite3.connect(self.session_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT DISTINCT session_id FROM conversation_memories 
                        WHERE content LIKE ? LIMIT ?
                    ''', (f'%{query}%', limit))
                    
                    for (session_id,) in cursor.fetchall():
                        session_memories = self.retrieve_conversation_memories(session_id, query)
                        all_memories.extend(session_memories[:2])  # Limit per session
                        
            except Exception as e:
                self.logger.warning(f"Failed to search conversation memories: {e}")
        
        # Sort by relevance (basic implementation)
        all_memories = sorted(all_memories, key=lambda x: x.get('confidence', 0.5), reverse=True)
        
        return all_memories[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            stats = {
                'adapter_type': 'legacy',
                'global_config_loaded': self.global_memory._config is not None,
                'workspace_instances': len(self._workspace_memories),
                'session_db_path': self.session_db_path,
                'timestamp': datetime.now().isoformat()
            }
            
            # Count conversation memories
            try:
                with sqlite3.connect(self.session_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM conversation_memories')
                    stats['conversation_memories_count'] = cursor.fetchone()[0]
            except Exception:
                stats['conversation_memories_count'] = 'unknown'
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {'error': str(e), 'adapter_type': 'legacy'}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health = {
            'status': 'unknown',
            'adapter_type': 'legacy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        try:
            # Check global memory
            try:
                self.global_memory.load()
                health['checks']['global_memory'] = 'ok'
            except Exception as e:
                health['checks']['global_memory'] = f'error: {e}'
            
            # Check session database
            try:
                with sqlite3.connect(self.session_db_path) as conn:
                    conn.execute('SELECT 1').fetchone()
                health['checks']['session_database'] = 'ok'
            except Exception as e:
                health['checks']['session_database'] = f'error: {e}'
            
            # Determine overall status
            all_ok = all(check == 'ok' for check in health['checks'].values())
            health['status'] = 'healthy' if all_ok else 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health