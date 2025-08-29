"""Configuration data models for the memory chatbot."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class MemoryAdapterConfig:
    """Configuration for memory adapters."""
    type: str = "legacy"  # "legacy" or "mem0"
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Legacy adapter specific settings
    session_db_path: str = field(
        default_factory=lambda: os.path.expanduser('~/.memory-chatbot/sessions.db')
    )
    
    # Mem0 adapter specific settings
    mem0_config: Dict[str, Any] = field(default_factory=dict)
    enable_semantic_extraction: bool = True
    confidence_threshold: float = 0.5
    max_memories_per_session: int = 100


@dataclass
class UserProfile:
    """User profile information."""
    user_id: str
    created_at: datetime
    last_updated: datetime


@dataclass
class DomainPreferences:
    """Preferences for a specific domain."""
    communication_style: str = "balanced"  # simple, detailed, balanced
    depth_level: str = "intermediate"  # beginner, intermediate, expert
    examples_preference: str = "on_demand"  # always, on_demand, rarely
    response_length: str = "medium"  # short, medium, long


@dataclass
class UserPreferences:
    """User interaction preferences across domains."""
    # Global defaults
    communication_style: str = "balanced"  # simple, detailed, balanced
    technical_depth: str = "intermediate"  # beginner, intermediate, expert
    code_examples: str = "on_demand"  # always, on_demand, rarely
    language_preference: str = "en"  # en, zh-CN, ja, etc.
    response_length: str = "medium"  # short, medium, long
    
    # Domain-specific preferences
    domain_preferences: Dict[str, DomainPreferences] = field(default_factory=lambda: {
        'technology': DomainPreferences(
            communication_style='detailed',
            depth_level='expert', 
            examples_preference='always',
            response_length='medium'
        ),
        'academic': DomainPreferences(
            communication_style='detailed',
            depth_level='expert',
            examples_preference='on_demand',
            response_length='long'
        ),
        'creative': DomainPreferences(
            communication_style='balanced',
            depth_level='intermediate',
            examples_preference='always',
            response_length='medium'
        ),
        'business': DomainPreferences(
            communication_style='simple',
            depth_level='intermediate',
            examples_preference='rarely',
            response_length='short'
        ),
        'personal': DomainPreferences(
            communication_style='simple',
            depth_level='beginner',
            examples_preference='rarely',
            response_length='short'
        )
    })


@dataclass
class KnowledgeDomain:
    """Knowledge domain information."""
    name: str
    keywords: List[str]
    experience_level: str
    last_used: datetime


@dataclass
class PersonalInsight:
    """Personal insight learned from interactions."""
    content: str
    confidence: float
    source: str
    created_at: datetime
    domain: str = "general"  # technology, academic, creative, business, personal, general
    insight_category: str = "knowledge"  # knowledge, preference, pattern, habit, interest


@dataclass
class GlobalConfig:
    """Global configuration structure."""
    version: str = "1.0"
    user_profile: Optional[UserProfile] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    knowledge_base: Dict[str, List[KnowledgeDomain]] = field(default_factory=dict)
    personal_insights: List[PersonalInsight] = field(default_factory=list)
    memory_adapter: MemoryAdapterConfig = field(default_factory=MemoryAdapterConfig)


@dataclass  
class ProjectProfile:
    """Project profile information."""
    domain_type: str = "technology"  # technology, academic, creative, business, personal
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    team_size: int = 1
    project_stage: str = "development"  # planning, development, production
    
    # Domain-specific fields
    research_area: str = ""  # For academic domain
    creative_medium: str = ""  # For creative domain (writing, design, music, etc.)
    business_sector: str = ""  # For business domain
    personal_goal: str = ""  # For personal domain


@dataclass
class ArchitectureDecision:
    """Architecture decision record."""
    title: str
    decision: str
    rationale: str
    date: datetime


@dataclass
class BestPractice:
    """Best practice record."""
    category: str
    practice: str
    reason: str
    examples: List[str] = field(default_factory=list)


@dataclass
class CommonPattern:
    """Common pattern usage record."""
    pattern: str
    implementation: str
    usage_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class DevelopmentNote:
    """Development note record."""
    title: str
    content: str
    created_at: datetime
    tags: List[str] = field(default_factory=list)


@dataclass
class ProjectKnowledge:
    """Project-specific knowledge."""
    architecture_decisions: List[ArchitectureDecision] = field(default_factory=list)
    best_practices: List[BestPractice] = field(default_factory=list)
    common_patterns: List[CommonPattern] = field(default_factory=list)


@dataclass
class WorkspaceInfo:
    """Workspace metadata."""
    name: str
    description: str
    created_at: datetime
    last_updated: datetime


@dataclass
class WorkspaceConfig:
    """Workspace configuration structure."""
    version: str = "1.0"
    workspace_info: Optional[WorkspaceInfo] = None
    project_profile: ProjectProfile = field(default_factory=ProjectProfile)
    project_knowledge: ProjectKnowledge = field(default_factory=ProjectKnowledge)
    development_notes: List[DevelopmentNote] = field(default_factory=list)


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"  # openai, claude, local
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key_encrypted: Optional[str] = None
    base_url: Optional[str] = None  # Custom base URL for API calls
    organization: Optional[str] = None  # OpenAI organization ID
    timeout: float = 60.0  # API request timeout in seconds


@dataclass
class MemoryConfig:
    """Memory system configuration."""
    provider: str = "legacy"  # legacy, mem0
    confidence_threshold: float = 0.3
    extraction_enabled: bool = True
    
    # Mem0 specific configuration
    openai_api_key: Optional[str] = None
    neo4j_url: str = "neo4j://localhost:7687"
    neo4j_username: str = "neo4j" 
    neo4j_password: Optional[str] = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    @classmethod
    def from_env(cls) -> "MemoryConfig":
        """Create MemoryConfig from environment variables."""
        return cls(
            provider=os.getenv("MEMORY_PROVIDER", "legacy"),
            confidence_threshold=float(os.getenv("MEMORY_CONFIDENCE_THRESHOLD", "0.3")),
            extraction_enabled=os.getenv("MEMORY_EXTRACTION_ENABLED", "true").lower() == "true",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            neo4j_url=os.getenv("NEO4J_URL", "neo4j://localhost:7687"),
            neo4j_username=os.getenv("NEO4J_USERNAME", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD"),
            qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333"))
        )


@dataclass
class AppConfig:
    """Application configuration."""
    current_workspace: Optional[str] = None
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    session_db_path: str = "~/.memory-chatbot/sessions.db"
    log_level: str = "INFO"
    debug_mode: bool = False
    performance_monitoring: bool = False
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create AppConfig from environment variables."""
        return cls(
            llm=LLMConfig(),  # Will be initialized with defaults
            memory=MemoryConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            performance_monitoring=os.getenv("ENABLE_PERFORMANCE_MONITORING", "false").lower() == "true"
        )