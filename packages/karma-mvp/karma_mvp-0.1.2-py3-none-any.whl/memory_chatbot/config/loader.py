"""Configuration file loader and manager."""

import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .settings import (
    GlobalConfig, WorkspaceConfig, AppConfig, 
    UserProfile, WorkspaceInfo, UserPreferences,
    ProjectProfile, LLMConfig
)


class ConfigurationError(Exception):
    """Configuration related errors."""
    pass


class ConfigLoader:
    """Configuration file loader and manager."""
    
    def __init__(self):
        self.global_dir = Path.home() / ".memory-chatbot"
        self.global_config_path = self.global_dir / "global.yaml"
        self.app_config_path = self.global_dir / "config.yaml"
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """Safely parse datetime string with timezone handling."""
        # Handle various datetime formats
        dt_str = dt_string.strip()
        
        # Handle malformed formats like '+00:00Z' or '+00:00+00:00'
        if dt_str.endswith('Z') and '+00:00' in dt_str:
            # Remove Z suffix if already has timezone
            dt_str = dt_str[:-1]
        
        # Handle double timezone like '+00:00+00:00'
        if dt_str.count('+00:00') > 1:
            # Keep only the first occurrence
            parts = dt_str.split('+00:00')
            dt_str = parts[0] + '+00:00'
        
        # If has Z suffix only, replace with +00:00
        if dt_str.endswith('Z') and '+' not in dt_str:
            dt_str = dt_str.replace('Z', '+00:00')
        
        # If no timezone info, assume UTC
        if '+' not in dt_str and 'Z' not in dt_str and 'T' in dt_str:
            dt_str += '+00:00'
        
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError as e:
            # Last resort: try to parse without timezone and add UTC
            try:
                if '+' in dt_str:
                    dt_str = dt_str.split('+')[0] + '+00:00'
                return datetime.fromisoformat(dt_str)
            except ValueError:
                raise ConfigurationError(f"Invalid datetime format: {dt_string}") from e
        
    def ensure_global_dir(self) -> None:
        """Ensure global configuration directory exists."""
        self.global_dir.mkdir(parents=True, exist_ok=True)
        
    def load_global_config(self) -> GlobalConfig:
        """Load global configuration from file."""
        self.ensure_global_dir()
        
        if not self.global_config_path.exists():
            return self.create_default_global_config()
            
        try:
            with open(self.global_config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return self._dict_to_global_config(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load global config: {e}")
    
    def save_global_config(self, config: GlobalConfig) -> None:
        """Save global configuration to file."""
        self.ensure_global_dir()
        
        try:
            data = self._global_config_to_dict(config)
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save global config: {e}")
    
    def load_workspace_config(self, workspace_path: Optional[Path] = None) -> WorkspaceConfig:
        """Load workspace configuration from file."""
        if workspace_path is None:
            workspace_path = Path.cwd() / "workspace"
        
        config_path = workspace_path / "config.yaml"
        
        if not config_path.exists():
            return self.create_default_workspace_config()
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return self._dict_to_workspace_config(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load workspace config: {e}")
    
    def save_workspace_config(self, config: WorkspaceConfig, workspace_path: Optional[Path] = None) -> None:
        """Save workspace configuration to file."""
        if workspace_path is None:
            workspace_path = Path.cwd() / "workspace"
        
        workspace_path.mkdir(parents=True, exist_ok=True)
        config_path = workspace_path / "config.yaml"
        
        try:
            data = self._workspace_config_to_dict(config)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save workspace config: {e}")
    
    def load_app_config(self) -> AppConfig:
        """Load application configuration."""
        self.ensure_global_dir()
        
        if not self.app_config_path.exists():
            return AppConfig()
            
        try:
            with open(self.app_config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return self._dict_to_app_config(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load app config: {e}")
    
    def save_app_config(self, config: AppConfig) -> None:
        """Save application configuration."""
        self.ensure_global_dir()
        
        try:
            data = self._app_config_to_dict(config)
            with open(self.app_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save app config: {e}")
    
    def create_default_global_config(self) -> GlobalConfig:
        """Create default global configuration."""
        now = datetime.now()
        user_id = f"user_{now.strftime('%Y%m%d_%H%M%S')}"
        
        return GlobalConfig(
            user_profile=UserProfile(
                user_id=user_id,
                created_at=now,
                last_updated=now
            ),
            preferences=UserPreferences()
        )
    
    def create_default_workspace_config(self, name: str = "default-workspace") -> WorkspaceConfig:
        """Create default workspace configuration."""
        now = datetime.now()
        
        return WorkspaceConfig(
            workspace_info=WorkspaceInfo(
                name=name,
                description="Default workspace",
                created_at=now,
                last_updated=now
            ),
            project_profile=ProjectProfile()
        )
    
    def _dict_to_global_config(self, data: Dict[str, Any]) -> GlobalConfig:
        """Convert dictionary to GlobalConfig."""
        config = GlobalConfig()
        config.version = data.get('version', '1.0')
        
        # User profile
        if 'user_profile' in data:
            up = data['user_profile']
            config.user_profile = UserProfile(
                user_id=up['user_id'],
                created_at=self._parse_datetime(up['created_at']),
                last_updated=self._parse_datetime(up['last_updated'])
            )
        
        # Preferences
        if 'preferences' in data:
            prefs = data['preferences']
            config.preferences = UserPreferences(
                communication_style=prefs.get('communication_style', 'detailed'),
                technical_depth=prefs.get('technical_depth', 'expert'),
                code_examples=prefs.get('code_examples', 'always'),
                language_preference=prefs.get('language_preference', 'en'),
                response_length=prefs.get('response_length', 'medium')
            )
        
        # Knowledge base and insights would be loaded here
        config.knowledge_base = data.get('knowledge_base', {})
        config.personal_insights = data.get('personal_insights', [])
        
        return config
    
    def _global_config_to_dict(self, config: GlobalConfig) -> Dict[str, Any]:
        """Convert GlobalConfig to dictionary."""
        data = {
            'version': config.version,
            'preferences': {
                'communication_style': config.preferences.communication_style,
                'technical_depth': config.preferences.technical_depth,
                'code_examples': config.preferences.code_examples,
                'language_preference': config.preferences.language_preference,
                'response_length': config.preferences.response_length
            }
        }
        
        if config.user_profile:
            data['user_profile'] = {
                'user_id': config.user_profile.user_id,
                'created_at': config.user_profile.created_at.isoformat() + 'Z',
                'last_updated': config.user_profile.last_updated.isoformat() + 'Z'
            }
        
        if config.knowledge_base:
            data['knowledge_base'] = config.knowledge_base
            
        if config.personal_insights:
            data['personal_insights'] = config.personal_insights
        
        return data
    
    def _dict_to_workspace_config(self, data: Dict[str, Any]) -> WorkspaceConfig:
        """Convert dictionary to WorkspaceConfig."""
        config = WorkspaceConfig()
        config.version = data.get('version', '1.0')
        
        # Workspace info
        if 'workspace_info' in data:
            wi = data['workspace_info']
            config.workspace_info = WorkspaceInfo(
                name=wi['name'],
                description=wi['description'],
                created_at=self._parse_datetime(wi['created_at']),
                last_updated=self._parse_datetime(wi['last_updated'])
            )
        
        # Project profile
        if 'project_profile' in data:
            pp = data['project_profile']
            config.project_profile = ProjectProfile(
                domain_type=pp.get('domain_type', 'general'),
                tech_stack=pp.get('tech_stack', {}),
                team_size=pp.get('team_size', 1),
                project_stage=pp.get('project_stage', 'development'),
                research_area=pp.get('research_area', ''),
                creative_medium=pp.get('creative_medium', ''),
                business_sector=pp.get('business_sector', ''),
                personal_goal=pp.get('personal_goal', '')
            )
        
        # Project knowledge and development notes would be loaded here
        return config
    
    def _workspace_config_to_dict(self, config: WorkspaceConfig) -> Dict[str, Any]:
        """Convert WorkspaceConfig to dictionary."""
        data = {
            'version': config.version,
            'project_profile': {
                'domain_type': config.project_profile.domain_type,
                'tech_stack': config.project_profile.tech_stack,
                'team_size': config.project_profile.team_size,
                'project_stage': config.project_profile.project_stage,
                'research_area': config.project_profile.research_area,
                'creative_medium': config.project_profile.creative_medium,
                'business_sector': config.project_profile.business_sector,
                'personal_goal': config.project_profile.personal_goal
            }
        }
        
        if config.workspace_info:
            data['workspace_info'] = {
                'name': config.workspace_info.name,
                'description': config.workspace_info.description,
                'created_at': config.workspace_info.created_at.isoformat() + 'Z',
                'last_updated': config.workspace_info.last_updated.isoformat() + 'Z'
            }
        
        return data
    
    def _dict_to_app_config(self, data: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig."""
        config = AppConfig()
        config.current_workspace = data.get('current_workspace')
        config.session_db_path = data.get('session_db_path', '~/.memory-chatbot/sessions.db')
        config.log_level = data.get('log_level', 'INFO')
        
        if 'llm' in data:
            llm = data['llm']
            config.llm = LLMConfig(
                provider=llm.get('provider', 'openai'),
                model=llm.get('model', 'gpt-3.5-turbo'),
                temperature=llm.get('temperature', 0.7),
                max_tokens=llm.get('max_tokens', 2000),
                api_key_encrypted=llm.get('api_key_encrypted'),
                base_url=llm.get('base_url'),
                organization=llm.get('organization'),
                timeout=llm.get('timeout', 60.0)
            )
        
        return config
    
    def _app_config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """Convert AppConfig to dictionary."""
        return {
            'current_workspace': config.current_workspace,
            'session_db_path': config.session_db_path,
            'log_level': config.log_level,
            'llm': {
                'provider': config.llm.provider,
                'model': config.llm.model,
                'temperature': config.llm.temperature,
                'max_tokens': config.llm.max_tokens,
                'api_key_encrypted': config.llm.api_key_encrypted,
                'base_url': config.llm.base_url,
                'organization': config.llm.organization,
                'timeout': config.llm.timeout
            }
        }