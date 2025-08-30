"""Global memory management for user preferences and cross-project knowledge."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..config.settings import (
    GlobalConfig, PersonalInsight, KnowledgeDomain, 
    UserPreferences, UserProfile, DomainPreferences, Mem0Config
)
from ..config.loader import ConfigLoader, ConfigurationError
from ..utils.crypto import CryptoManager, CryptoError


class GlobalMemoryError(Exception):
    """Global memory related errors."""
    pass


class GlobalMemory:
    """Manages global user preferences and cross-project knowledge."""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, mem0_config: Optional[Mem0Config] = None):
        self.config_loader = config_loader or ConfigLoader()
        self._config: Optional[GlobalConfig] = None
        
        # Mem0 integration
        self.mem0_config = mem0_config
        self.mem0_client = None
        self.crypto_manager = CryptoManager()
        
        # Initialize Mem0 client if enabled
        if self.mem0_config and self.mem0_config.enabled and self.mem0_config.enhance_context:
            self._initialize_mem0_client()
    
    def _initialize_mem0_client(self):
        """Initialize Mem0 client for context enhancement."""
        try:
            # Try to import Mem0 (optional dependency)
            try:
                from mem0 import MemoryClient as Mem0
            except ImportError:
                return
            
            if self.mem0_config.use_platform:
                # Platform version with API key
                if self.mem0_config.api_key_encrypted:
                    try:
                        api_key = self.crypto_manager.decrypt(self.mem0_config.api_key_encrypted)
                        self.mem0_client = Mem0(api_key=api_key)
                    except CryptoError:
                        pass
            else:
                # OSS version with local configuration
                self.mem0_client = Mem0(config=self.mem0_config.oss_config)
                
        except Exception:
            # Any initialization failure - gracefully disable Mem0
            self.mem0_client = None
    
    def load(self) -> GlobalConfig:
        """Load global configuration from file."""
        try:
            self._config = self.config_loader.load_global_config()
            return self._config
        except ConfigurationError as e:
            raise GlobalMemoryError(f"Failed to load global memory: {e}")
    
    def save(self) -> None:
        """Save current global configuration to file."""
        if self._config is None:
            raise GlobalMemoryError("No configuration loaded to save")
        
        try:
            self._config.user_profile.last_updated = datetime.now()
            self.config_loader.save_global_config(self._config)
        except ConfigurationError as e:
            raise GlobalMemoryError(f"Failed to save global memory: {e}")
    
    @property
    def config(self) -> GlobalConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self.load()
        return self._config
    
    def get_preferences(self) -> UserPreferences:
        """Get user preferences."""
        return self.config.preferences
    
    def update_preferences(self, **kwargs) -> None:
        """Update user preferences."""
        prefs = self.config.preferences
        for key, value in kwargs.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
            else:
                raise GlobalMemoryError(f"Unknown preference: {key}")
        
        self.save()
    
    def add_personal_insight(self, content: str, confidence: float, source: str) -> None:
        """Add a new personal insight."""
        if not 0.0 <= confidence <= 1.0:
            raise GlobalMemoryError("Confidence must be between 0.0 and 1.0")
        
        insight = PersonalInsight(
            content=content,
            confidence=confidence,
            source=source,
            created_at=datetime.now()
        )
        
        self.config.personal_insights.append(insight)
        self.save()
    
    def get_personal_insights(self, min_confidence: float = 0.0) -> List[PersonalInsight]:
        """Get personal insights above minimum confidence threshold."""
        return [
            insight for insight in self.config.personal_insights
            if insight.confidence >= min_confidence
        ]
    
    def update_knowledge_domain(self, domain_name: str, keywords: List[str], 
                              experience_level: str) -> None:
        """Update or create a knowledge domain."""
        valid_levels = ["beginner", "intermediate", "expert"]
        if experience_level not in valid_levels:
            raise GlobalMemoryError(f"Invalid experience level: {experience_level}")
        
        domain = KnowledgeDomain(
            name=domain_name,
            keywords=keywords,
            experience_level=experience_level,
            last_used=datetime.now()
        )
        
        # Initialize domains list if it doesn't exist
        if "domains" not in self.config.knowledge_base:
            self.config.knowledge_base["domains"] = []
        
        # Update existing domain or add new one
        domains = self.config.knowledge_base["domains"]
        for i, existing_domain in enumerate(domains):
            if existing_domain.get("name") == domain_name:
                domains[i] = {
                    "name": domain.name,
                    "keywords": domain.keywords,
                    "experience_level": domain.experience_level,
                    "last_used": domain.last_used.isoformat()
                }
                break
        else:
            domains.append({
                "name": domain.name,
                "keywords": domain.keywords,
                "experience_level": domain.experience_level,
                "last_used": domain.last_used.isoformat()
            })
        
        self.save()
    
    def get_knowledge_domains(self) -> List[Dict[str, Any]]:
        """Get all knowledge domains."""
        return self.config.knowledge_base.get("domains", [])
    
    def get_relevant_knowledge(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Get knowledge domains relevant to given keywords."""
        domains = self.get_knowledge_domains()
        relevant = []
        
        for domain in domains:
            domain_keywords = domain.get("keywords", [])
            if any(keyword.lower() in [dk.lower() for dk in domain_keywords] for keyword in keywords):
                relevant.append(domain)
        
        return relevant
    
    def get_context_for_prompt(self, keywords: Optional[List[str]] = None, 
                              current_domain: str = "general", workspace_name: str = "global") -> Dict[str, Any]:
        """Get relevant context for prompt injection, enhanced with Mem0 memories."""
        # Get domain-specific preferences or fall back to global defaults
        if current_domain in self.config.preferences.domain_preferences:
            domain_prefs = self.config.preferences.domain_preferences[current_domain]
            preferences = {
                "communication_style": domain_prefs.communication_style,
                "technical_depth": domain_prefs.depth_level,
                "code_examples": domain_prefs.examples_preference,
                "response_length": domain_prefs.response_length
            }
        else:
            # Fallback to global preferences
            preferences = {
                "communication_style": self.config.preferences.communication_style,
                "technical_depth": self.config.preferences.technical_depth,
                "code_examples": self.config.preferences.code_examples,
                "response_length": self.config.preferences.response_length
            }
        
        context = {
            "preferences": preferences,
            "current_domain": current_domain,
            "insights": []
        }
        
        # Phase 1: Add traditional insights (local memory)
        domain_insights = self.get_domain_insights(current_domain, min_confidence=0.7)
        general_insights = self.get_domain_insights("general", min_confidence=0.7)
        
        # Combine domain-specific and general insights (domain-specific first)
        all_insights = domain_insights[-3:] + general_insights[-2:]  # 3 domain + 2 general
        local_insights = [insight.content for insight in all_insights[-5:]]  # Max 5 total
        
        # Phase 2: Add Mem0 enhanced insights (if available)
        if self.mem0_client and self.mem0_config and self.mem0_config.enhance_context:
            try:
                mem0_insights = self._get_mem0_insights(keywords, current_domain, workspace_name)
                # Combine local and Mem0 insights, prioritizing Mem0 for higher relevance
                context["insights"] = mem0_insights + local_insights
                # Add metadata about enhanced context
                context["enhanced_with_mem0"] = True
                context["mem0_insights_count"] = len(mem0_insights)
            except Exception:
                # Fall back to local insights if Mem0 fails
                context["insights"] = local_insights
                context["enhanced_with_mem0"] = False
        else:
            context["insights"] = local_insights
            context["enhanced_with_mem0"] = False
        
        # Add relevant knowledge domains
        if keywords:
            relevant_domains = self.get_relevant_knowledge(keywords)
            context["knowledge_domains"] = relevant_domains
        
        return context
    
    def _get_mem0_insights(self, keywords: Optional[List[str]], current_domain: str, workspace_name: str) -> List[str]:
        """Retrieve relevant insights from Mem0."""
        insights = []
        
        try:
            # Build user identifier
            user_id = f"global_{workspace_name}" if workspace_name != "global" else "global_user"
            
            # Create search query based on keywords and domain
            if keywords:
                query = f"User preferences and insights related to {', '.join(keywords)} in {current_domain} domain"
            else:
                query = f"User preferences and general insights for {current_domain} domain"
            
            # Get relevant memories from Mem0
            memories = self.mem0_client.get_all(
                user_id=user_id,
                limit=self.mem0_config.retrieval_limit // 2,  # Reserve half for global insights
                filters={
                    "domain": current_domain,
                    "type": "global_insight"
                }
            )
            
            for memory in memories:
                if memory.get('text') and len(memory['text'].strip()) > 5:
                    insights.append(f"[Mem0] {memory['text'].strip()}")
            
            # Also get general insights without domain filter
            if len(insights) < self.mem0_config.retrieval_limit // 2:
                general_memories = self.mem0_client.get_all(
                    user_id=user_id,
                    limit=(self.mem0_config.retrieval_limit // 2) - len(insights),
                    filters={"type": "global_insight"}
                )
                
                for memory in general_memories:
                    if memory.get('text') and len(memory['text'].strip()) > 5:
                        insights.append(f"[Mem0] {memory['text'].strip()}")
        
        except Exception:
            # Silent failure - return empty list
            pass
        
        return insights[:5]  # Limit to 5 insights
    
    def store_insight_to_mem0(self, content: str, domain: str, workspace_name: str, 
                             insight_type: str = "global_insight") -> bool:
        """Store an insight to Mem0 for enhanced context retrieval."""
        if not (self.mem0_client and self.mem0_config and self.mem0_config.enhance_context):
            return False
        
        try:
            user_id = f"global_{workspace_name}" if workspace_name != "global" else "global_user"
            
            # Store insight with metadata
            self.mem0_client.add(
                content,
                user_id=user_id,
                metadata={
                    "type": insight_type,
                    "domain": domain,
                    "workspace": workspace_name,
                    "timestamp": datetime.now().isoformat(),
                    "source": "global_memory"
                }
            )
            return True
            
        except Exception:
            return False
    
    def get_domain_insights(self, domain: str, min_confidence: float = 0.5) -> List[PersonalInsight]:
        """Get insights for a specific domain."""
        return [
            insight for insight in self.config.personal_insights
            if insight.domain == domain and insight.confidence >= min_confidence
        ]
    
    def add_domain_insight(self, content: str, confidence: float, source: str, 
                          domain: str, insight_category: str = "knowledge") -> None:
        """Add a domain-specific insight."""
        insight = PersonalInsight(
            content=content,
            confidence=confidence,
            source=source,
            created_at=datetime.now(),
            domain=domain,
            insight_category=insight_category
        )
        self.config.personal_insights.append(insight)
        self.save()
    
    def update_domain_preference(self, domain: str, preference_type: str, value: str) -> None:
        """Update a domain-specific preference."""
        if domain not in self.config.preferences.domain_preferences:
            self.config.preferences.domain_preferences[domain] = DomainPreferences()
        
        domain_pref = self.config.preferences.domain_preferences[domain]
        
        if preference_type == 'communication_style':
            domain_pref.communication_style = value
        elif preference_type == 'depth_level':
            domain_pref.depth_level = value
        elif preference_type == 'examples_preference':
            domain_pref.examples_preference = value
        elif preference_type == 'response_length':
            domain_pref.response_length = value
        
        self.save()
    
    def export_config(self, export_path: Path) -> None:
        """Export global configuration to specified path."""
        try:
            self.config_loader.save_global_config(self.config)
            # Copy the global config file to export path
            import shutil
            shutil.copy2(self.config_loader.global_config_path, export_path)
        except Exception as e:
            raise GlobalMemoryError(f"Failed to export config: {e}")
    
    def import_config(self, import_path: Path) -> None:
        """Import global configuration from specified path."""
        try:
            # Backup current config
            backup_path = Path(str(self.config_loader.global_config_path) + ".backup")
            if self.config_loader.global_config_path.exists():
                import shutil
                shutil.copy2(self.config_loader.global_config_path, backup_path)
            
            # Import new config
            shutil.copy2(import_path, self.config_loader.global_config_path)
            
            # Reload config
            self._config = None
            self.load()
            
        except Exception as e:
            raise GlobalMemoryError(f"Failed to import config: {e}")
    
    def clean_old_insights(self, days_threshold: int = 90, confidence_threshold: float = 0.3) -> int:
        """Clean old low-confidence insights."""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_threshold)
        
        original_count = len(self.config.personal_insights)
        self.config.personal_insights = [
            insight for insight in self.config.personal_insights
            if not (insight.created_at < cutoff_date and insight.confidence < confidence_threshold)
        ]
        
        removed_count = original_count - len(self.config.personal_insights)
        if removed_count > 0:
            self.save()
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get global memory statistics."""
        return {
            "total_insights": len(self.config.personal_insights),
            "high_confidence_insights": len(self.get_personal_insights(min_confidence=0.7)),
            "knowledge_domains": len(self.get_knowledge_domains()),
            "last_updated": self.config.user_profile.last_updated.isoformat() if self.config.user_profile else None
        }