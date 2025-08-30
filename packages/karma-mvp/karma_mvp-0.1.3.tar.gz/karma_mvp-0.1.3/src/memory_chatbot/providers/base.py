"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass


@dataclass
class ModelLimits:
    """Model limitations and capabilities."""
    max_tokens: int
    context_window: int
    supports_streaming: bool = True
    supports_system_message: bool = True


@dataclass
class CompletionResponse:
    """Response from LLM completion."""
    content: str
    tokens_used: int
    model: str
    finish_reason: str = "stop"
    metadata: Optional[Dict[str, Any]] = None


class LLMProviderError(Exception):
    """LLM provider related errors."""
    pass


class LLMProvider(ABC):
    """Abstract base class for LLM service providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7, 
                            max_tokens: Optional[int] = None,
                            **kwargs) -> CompletionResponse:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            CompletionResponse with generated content and metadata
        """
        pass
    
    @abstractmethod
    async def stream_completion(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.7, 
                              max_tokens: Optional[int] = None,
                              **kwargs) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            String chunks of the response as they are generated
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def get_model_limits(self) -> ModelLimits:
        """
        Get the limitations and capabilities of the current model.
        
        Returns:
            ModelLimits object with model constraints
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of models supported by this provider.
        
        Returns:
            List of supported model names/identifiers
        """
        pass
    
    @abstractmethod
    async def list_available_models(self) -> List[str]:
        """
        Get list of models currently available via API.
        
        Returns:
            List of available model names from API
            
        Raises:
            LLMProviderError: If unable to fetch model list
        """
        pass
    
    def validate_model(self, model: str) -> bool:
        """
        Validate if a model is supported by this provider.
        
        Args:
            model: Model name to validate
            
        Returns:
            True if model is supported, False otherwise
        """
        return model in self.get_supported_models()
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """
        Validate message format.
        
        Args:
            messages: List of message dictionaries to validate
            
        Raises:
            LLMProviderError: If messages are invalid
        """
        if not isinstance(messages, list):
            raise LLMProviderError("Messages must be a list")
        
        if not messages:
            raise LLMProviderError("Messages list cannot be empty")
        
        valid_roles = {'system', 'user', 'assistant'}
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise LLMProviderError(f"Message {i} must be a dictionary")
            
            if 'role' not in message:
                raise LLMProviderError(f"Message {i} missing 'role' field")
            
            if 'content' not in message:
                raise LLMProviderError(f"Message {i} missing 'content' field")
            
            if message['role'] not in valid_roles:
                raise LLMProviderError(f"Message {i} has invalid role: {message['role']}")
            
            if not isinstance(message['content'], str):
                raise LLMProviderError(f"Message {i} content must be a string")
    
    def estimate_total_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate total tokens for a conversation.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Estimated total token count
        """
        total = 0
        for message in messages:
            total += self.count_tokens(message['content'])
            # Add overhead for role and formatting
            total += 5
        return total
    
    def trim_context_to_fit(self, messages: List[Dict[str, str]], 
                           max_tokens: int, reserve_tokens: int = 500) -> List[Dict[str, str]]:
        """
        Trim conversation context to fit within token limits.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens allowed
            reserve_tokens: Tokens to reserve for response generation
            
        Returns:
            Trimmed list of messages that fit within limits
        """
        available_tokens = max_tokens - reserve_tokens
        
        # Always keep system message if present
        system_messages = [msg for msg in messages if msg['role'] == 'system']
        conversation_messages = [msg for msg in messages if msg['role'] != 'system']
        
        # Calculate system message tokens
        system_tokens = sum(self.count_tokens(msg['content']) + 5 for msg in system_messages)
        remaining_tokens = available_tokens - system_tokens
        
        if remaining_tokens <= 0:
            # If system messages are too long, truncate them
            return system_messages[:1] if system_messages else []
        
        # Include conversation messages from most recent backwards
        included_messages = []
        current_tokens = 0
        
        for message in reversed(conversation_messages):
            message_tokens = self.count_tokens(message['content']) + 5
            if current_tokens + message_tokens > remaining_tokens:
                break
            included_messages.append(message)
            current_tokens += message_tokens
        
        # Return in original order
        result = system_messages + list(reversed(included_messages))
        return result
    
    def format_system_message(self, context: Dict[str, Any]) -> str:
        """
        Format context information into a system message.
        
        Args:
            context: Context dictionary with memory information
            
        Returns:
            Formatted system message string
        """
        # Base system message with domain adaptation
        current_domain = context.get('current_domain', 'general')
        
        # Domain-specific base messages
        domain_messages = {
            'technology': "You are an expert technical assistant with deep knowledge of software development, programming, and technology. You provide precise, actionable technical guidance with code examples.",
            'academic': "You are a knowledgeable academic assistant skilled in research methodology, analysis, and scholarly communication. You help with rigorous thinking and evidence-based conclusions.",
            'creative': "You are a creative assistant that understands artistic processes, design principles, and creative problem-solving. You encourage experimentation and iterative refinement.",
            'business': "You are a strategic business assistant with expertise in planning, operations, and management. You focus on practical solutions and measurable outcomes.",
            'personal': "You are a supportive personal assistant that helps with life organization, habit formation, and personal development. You provide gentle guidance and encouragement.",
            'general': "You are a helpful AI assistant with access to conversation context and memory."
        }
        
        parts = [domain_messages.get(current_domain, domain_messages['general'])]
        
        # Add domain context
        if current_domain != 'general':
            parts.append(f"\nConversation Context: {current_domain.title()} domain")
        
        # Add user preferences
        if 'preferences' in context:
            prefs = context['preferences']
            parts.append(f"""
User Preferences for {current_domain.title()} Domain:
- Communication style: {prefs.get('communication_style', 'balanced')}
- Knowledge depth: {prefs.get('technical_depth', 'intermediate')}
- Examples: {prefs.get('code_examples', 'as needed')}
- Response length: {prefs.get('response_length', 'medium')}
""")
        
        # Add workspace context with domain awareness
        if 'workspace' in context:
            ws = context['workspace']
            workspace_context = f"""
Current Workspace: {ws.get('name', 'Unknown')} ({ws.get('domain_type', 'general')} domain)"""
            
            if ws.get('domain_type') == 'technology':
                workspace_context += f"""
- Project stage: {ws.get('project_stage', 'development')}"""
                
                # Handle tech stack safely
                tech_stack = ws.get('tech_stack', {})
                if tech_stack:
                    tech_items = []
                    for k, v in tech_stack.items():
                        if isinstance(v, list):
                            tech_items.append(f"{k}: {', '.join(v)}")
                        else:
                            tech_items.append(f"{k}: {v}")
                    if tech_items:
                        workspace_context += f"\n- Tech stack: {', '.join(tech_items)}"
            elif ws.get('domain_type') == 'academic':
                if ws.get('research_area'):
                    workspace_context += f"\n- Research area: {ws.get('research_area')}"
            elif ws.get('domain_type') == 'creative':
                if ws.get('creative_medium'):
                    workspace_context += f"\n- Creative medium: {ws.get('creative_medium')}"
            elif ws.get('domain_type') == 'business':
                if ws.get('business_sector'):
                    workspace_context += f"\n- Business sector: {ws.get('business_sector')}"
            elif ws.get('domain_type') == 'personal':
                if ws.get('personal_goal'):
                    workspace_context += f"\n- Personal goal: {ws.get('personal_goal')}"
            
            parts.append(workspace_context)
        
        # Add domain-specific decisions/patterns
        if 'recent_decisions' in context:
            decision_label = {
                'technology': "Recent Architecture Decisions",
                'academic': "Recent Research Decisions",
                'creative': "Recent Creative Decisions", 
                'business': "Recent Strategic Decisions",
                'personal': "Recent Personal Decisions"
            }.get(current_domain, "Recent Decisions")
            
            parts.append(f"\n{decision_label}:")
            for decision in context['recent_decisions']:
                parts.append(f"- {decision['title']}: {decision['decision']}")
        
        # Add domain-specific patterns
        if 'common_patterns' in context:
            pattern_label = {
                'technology': "Common Technical Patterns",
                'academic': "Research Methodologies",
                'creative': "Creative Processes",
                'business': "Business Strategies", 
                'personal': "Personal Strategies"
            }.get(current_domain, "Common Patterns")
            
            parts.append(f"\n{pattern_label}:")
            for pattern in context['common_patterns']:
                parts.append(f"- {pattern['pattern']}: {pattern['implementation']}")
        
        # Add domain-specific insights
        if 'insights' in context and context['insights']:
            insight_label = {
                'technology': "Technical Insights & Preferences",
                'academic': "Research Insights & Methods",
                'creative': "Creative Insights & Preferences",
                'business': "Business Insights & Approaches",
                'personal': "Personal Insights & Preferences"
            }.get(current_domain, "Personal Insights")
            
            parts.append(f"\n{insight_label}:")
            for insight in context['insights']:
                parts.append(f"- {insight}")
        
        # Add workspace conversation history for context continuity
        if 'workspace_conversation_history' in context and context['workspace_conversation_history']:
            history = context['workspace_conversation_history']
            
            history_label = {
                'technology': "Recent Development Context",
                'academic': "Recent Research Context", 
                'creative': "Recent Creative Context",
                'business': "Recent Business Context",
                'personal': "Recent Personal Context"
            }.get(current_domain, "Recent Conversation Context")
            
            parts.append(f"\n{history_label}:")
            parts.append("Based on previous conversations, you should be aware of:")
            
            # Group and summarize history intelligently
            user_info = []
            recent_topics = []
            
            for msg in history:
                content = msg['content']
                role = msg['role']
                
                # Extract user personal information
                if role == 'user' and any(keyword in content.lower() for keyword in 
                    ['我喜欢', '我的', '我想', '我需要', 'i like', 'i want', 'i need', 'my']):
                    if len(content) < 100:  # Keep short personal statements
                        user_info.append(f"  • User mentioned: \"{content}\"")
                
                # Extract recent topics (shorter messages for context)
                elif len(content.strip()) > 5 and len(content) < 80:
                    recent_topics.append(f"  • {role.title()}: \"{content}\"")
            
            # Add user information first (most important)
            if user_info:
                parts.append("User's personal information:")
                parts.extend(user_info[-5:])  # Last 5 personal info items
            
            # Add recent conversation topics
            if recent_topics:
                parts.append("Recent conversation topics:")
                parts.extend(recent_topics[-8:])  # Last 8 topics
            
            # Add a note about context continuity
            parts.append("Continue the conversation naturally based on this shared context.")
        
        return '\n'.join(parts)


class ProviderRegistry:
    """Registry for managing LLM providers."""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        """Register a provider class."""
        if not issubclass(provider_class, LLMProvider):
            raise LLMProviderError(f"Provider must inherit from LLMProvider")
        cls._providers[name] = provider_class
    
    @classmethod
    def get_provider(cls, name: str) -> type:
        """Get a provider class by name."""
        if name not in cls._providers:
            raise LLMProviderError(f"Unknown provider: {name}")
        return cls._providers[name]
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """Get list of registered provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def create_provider(cls, name: str, api_key: str, model: str, **kwargs) -> LLMProvider:
        """Create and return a provider instance."""
        provider_class = cls.get_provider(name)
        return provider_class(api_key=api_key, model=model, **kwargs)
    
    @classmethod
    def get_supported_models(cls, provider_name: str) -> List[str]:
        """Get supported models for a specific provider."""
        provider_class = cls.get_provider(provider_name)
        
        # Check if the provider class has a MODEL_LIMITS attribute
        if hasattr(provider_class, 'MODEL_LIMITS'):
            return list(provider_class.MODEL_LIMITS.keys())
        
        # Fallback: try to create instance with a valid model
        try:
            # First, check if provider has default models we can use
            known_defaults = {
                'openai': 'gpt-3.5-turbo',
                'claude': 'claude-3-5-sonnet-20241022'
            }
            
            default_model = known_defaults.get(provider_name, 'default')
            temp_instance = provider_class(api_key="dummy", model=default_model)
            return temp_instance.get_supported_models()
        except Exception:
            return []
    
    @classmethod
    def get_all_supported_models(cls) -> Dict[str, List[str]]:
        """Get supported models for all registered providers."""
        result = {}
        for provider_name in cls.list_providers():
            result[provider_name] = cls.get_supported_models(provider_name)
        return result