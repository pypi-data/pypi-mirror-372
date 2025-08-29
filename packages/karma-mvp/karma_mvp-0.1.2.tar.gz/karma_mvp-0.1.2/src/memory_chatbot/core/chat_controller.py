"""Core chat controller that orchestrates the conversation flow."""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import time

from ..config.loader import ConfigLoader, ConfigurationError
from ..core.global_memory import GlobalMemory, GlobalMemoryError
from ..core.workspace_memory import WorkspaceMemory, WorkspaceMemoryError
from ..core.session_manager import SessionManager, SessionManagerError
from ..core.memory_extractor import MemoryExtractor
from ..core.domain_detector import DomainDetector
from ..providers import ProviderRegistry, LLMProviderError
from ..utils.crypto import CryptoManager, CryptoError


class ChatControllerError(Exception):
    """Chat controller related errors."""
    pass


class ChatController:
    """Main controller for chat conversations."""
    
    def __init__(self, debug_mode: bool = False):
        self.console = Console()
        self.debug_mode = debug_mode
        self.config_loader = ConfigLoader()
        self.global_memory = GlobalMemory()
        self.workspace_memory: Optional[WorkspaceMemory] = None
        self.session_manager = SessionManager()
        self.memory_extractor = MemoryExtractor()
        self.crypto_manager = CryptoManager()
        self.domain_detector = DomainDetector()
        
        # Load configurations
        self.app_config = None
        self.llm_provider = None
        
        # Debug info storage
        self._debug_info = {
            'context_build_time': 0,
            'api_call_time': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0
        }
        
    async def initialize(self) -> None:
        """Initialize the chat controller."""
        try:
            # Load app configuration
            self.app_config = self.config_loader.load_app_config()
            
            # Load global memory
            self.global_memory.load()
            
            # Load workspace memory if available
            if self.app_config.current_workspace:
                ws_path = Path.cwd() / self.app_config.current_workspace / "workspace"
                if ws_path.exists():
                    self.workspace_memory = WorkspaceMemory(ws_path)
                    self.workspace_memory.load_workspace()
            
            # Initialize LLM provider
            await self._initialize_llm_provider()
            
            # Print debug initialization info
            self._debug_print_initialization()
            
        except Exception as e:
            raise ChatControllerError(f"Failed to initialize chat controller: {e}")
    
    async def _initialize_llm_provider(self) -> None:
        """Initialize the LLM provider."""
        llm_config = self.app_config.llm
        
        # Check if API key is configured
        if not llm_config.api_key_encrypted:
            self.console.print("⚠️  No API key configured for LLM provider", style="yellow")
            await self._setup_api_key()
        
        # Decrypt API key
        try:
            api_key = self.crypto_manager.decrypt(llm_config.api_key_encrypted)
        except CryptoError as e:
            self.console.print("🔑 API key decryption failed. Please update your API key.", style="yellow")
            self.console.print("Run: chatbot config api-key", style="blue")
            raise ChatControllerError(f"Failed to decrypt API key: {e}")
        
        # Create provider instance with custom configuration
        try:
            provider_kwargs = {
                'temperature': llm_config.temperature,
                'timeout': llm_config.timeout
            }
            
            # Add provider-specific configurations
            if llm_config.provider == 'openai':
                if llm_config.base_url:
                    provider_kwargs['base_url'] = llm_config.base_url
                if llm_config.organization:
                    provider_kwargs['organization'] = llm_config.organization
            elif llm_config.provider == 'claude':
                if llm_config.base_url:
                    provider_kwargs['base_url'] = llm_config.base_url
            
            self.llm_provider = ProviderRegistry.create_provider(
                llm_config.provider,
                api_key=api_key,
                model=llm_config.model,
                **provider_kwargs
            )
        except LLMProviderError as e:
            raise ChatControllerError(f"Failed to create LLM provider: {e}")
    
    async def _setup_api_key(self) -> None:
        """Setup API key for the LLM provider."""
        provider = self.app_config.llm.provider
        
        self.console.print(f"\n🔑 Setting up {provider} API key", style="cyan")
        self.console.print("You can get your API key from:")
        
        if provider == 'openai':
            self.console.print("  https://platform.openai.com/api-keys", style="blue")
        elif provider == 'claude':
            self.console.print("  https://console.anthropic.com/", style="blue")
        
        api_key = Prompt.ask("\nEnter your API key", password=True)
        
        if not api_key or not api_key.strip():
            raise ChatControllerError("API key is required")
        
        # Encrypt and save
        encrypted_key = self.crypto_manager.encrypt(api_key.strip())
        self.app_config.llm.api_key_encrypted = encrypted_key
        self.config_loader.save_app_config(self.app_config)
        
        self.console.print("✅ API key saved securely!", style="green")
    
    async def single_chat(self, prompt: str, model: Optional[str] = None, 
                         temperature: float = 0.7, max_tokens: Optional[int] = None) -> None:
        """Handle a single chat interaction."""
        await self.initialize()
        
        # Start a session
        workspace_name = self.app_config.current_workspace
        session = self.session_manager.start_session(workspace_name)
        
        try:
            # Add user message
            self.session_manager.add_message('user', prompt)
            
            # Generate response
            response = await self._generate_response(prompt, model, temperature, max_tokens)
            
            # Display response
            self.console.print("\n" + "=" * 50)
            self.console.print(Markdown(response.content))
            self.console.print("=" * 50 + "\n")
            
            # Add assistant message
            self.session_manager.add_message('assistant', response.content, response.tokens_used)
            
            # Extract and process insights
            await self._process_insights(session.session_id)
            
        finally:
            # Debug: Print session summary
            self._debug_print_session_summary()
            
            # End session
            self.session_manager.end_session()
    
    async def interactive_chat(self, model: Optional[str] = None, 
                             temperature: float = 0.7, max_tokens: Optional[int] = None) -> None:
        """Handle interactive chat conversation."""
        await self.initialize()
        
        # Display welcome message
        self._display_welcome()
        
        # Start a session
        workspace_name = self.app_config.current_workspace
        session = self.session_manager.start_session(workspace_name)
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]", console=self.console)
                    
                    if not user_input.strip():
                        continue
                    
                    # Check for special commands
                    if user_input.lower() in ['/quit', '/exit', '/q']:
                        break
                    elif user_input.lower() == '/help':
                        self._display_help()
                        continue
                    elif user_input.lower() == '/status':
                        await self._display_status()
                        continue
                    
                    # Add user message
                    self.session_manager.add_message('user', user_input)
                    
                    # Generate response with typing indicator
                    self.console.print("\n[dim]🤖 Thinking...[/dim]")
                    response = await self._generate_response(user_input, model, temperature, max_tokens)
                    
                    # Clear typing indicator and display response
                    self.console.print("\r" + " " * 20 + "\r", end="")
                    self.console.print("\n[bold green]Assistant[/bold green]:")
                    self.console.print(Markdown(response.content))
                    
                    # Add assistant message
                    self.session_manager.add_message('assistant', response.content, response.tokens_used)
                    
                    # Extract insights in background
                    asyncio.create_task(self._process_insights(session.session_id))
                    
                except KeyboardInterrupt:
                    self.console.print("\n\n👋 Goodbye!", style="yellow")
                    break
                except Exception as e:
                    self.console.print(f"\n❌ Error: {e}", style="red")
                    continue
        
        finally:
            # Debug: Print session summary
            self._debug_print_session_summary()
            
            # End session
            self.session_manager.end_session()
    
    async def _generate_response(self, user_input: str, model: Optional[str] = None,
                               temperature: float = 0.7, max_tokens: Optional[int] = None) -> Any:
        """Generate LLM response with context injection."""
        # Override model if specified
        if model and model != self.llm_provider.model:
            # Create new provider instance with different model
            llm_config = self.app_config.llm
            api_key = self.crypto_manager.decrypt(llm_config.api_key_encrypted)
            self.llm_provider = ProviderRegistry.create_provider(
                llm_config.provider,
                api_key=api_key,
                model=model
            )
        
        # Get recent messages for domain detection
        recent_messages = self.session_manager.get_recent_context(max_messages=10)
        
        # Get conversation context with domain detection
        start_context_time = time.time()
        context = await self._build_context(recent_messages)
        self._debug_info['context_build_time'] += time.time() - start_context_time
        
        # Debug: Print context info
        self._debug_print_context(context)
        
        # Debug: Print recent messages/conversation history (current session)
        self._debug_print_conversation_history(recent_messages)
        
        # Debug: Print complete workspace history
        workspace_name = self.app_config.current_workspace
        if workspace_name:
            workspace_history = self.session_manager.get_workspace_history(workspace_name, max_messages=20)
            self._debug_print_workspace_history(workspace_history, workspace_name)
        
        # Build messages list
        messages = []
        
        # Add system message with context
        system_message = ""
        if context:
            system_message = self.llm_provider.format_system_message(context)
            messages.append({"role": "system", "content": system_message})
            
            # Debug: Print system prompt
            self._debug_print_system_prompt(system_message)
        
        # Add recent conversation history
        messages.extend(recent_messages)
        
        # Ensure we don't exceed token limits
        model_limits = self.llm_provider.get_model_limits()
        messages = self.llm_provider.trim_context_to_fit(
            messages, 
            model_limits.context_window,
            reserve_tokens=max_tokens or 1000
        )
        
        # Debug: Print final messages
        self._debug_print_messages(messages)
        
        # Generate response
        try:
            start_api_time = time.time()
            response = await self.llm_provider.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or self.app_config.llm.max_tokens
            )
            
            # Debug: Print API call info
            self._debug_print_api_call_info(messages, temperature, max_tokens, start_api_time, response)
            
            return response
        
        except LLMProviderError as e:
            # Debug: Print failed API call info
            self._debug_print_api_call_info(messages, temperature, max_tokens, start_api_time, None)
            raise ChatControllerError(f"Failed to generate response: {e}")
    
    async def _build_context(self, recent_messages: Optional[List] = None) -> Dict[str, Any]:
        """Build context from memory layers with workspace domain."""
        context = {}
        
        # Use workspace domain as the definitive domain
        current_domain = 'general'  # default
        if self.workspace_memory:
            workspace_domain = getattr(self.workspace_memory.config.project_profile, 'domain_type', 'general')
            current_domain = workspace_domain
        
        # Add global context with domain awareness
        try:
            global_context = self.global_memory.get_context_for_prompt(current_domain=current_domain)
            context.update(global_context)
        except GlobalMemoryError:
            pass  # Continue without global context
        
        # Add workspace context
        if self.workspace_memory:
            try:
                ws_context = self.workspace_memory.get_context_for_prompt()
                context.update(ws_context)
            except WorkspaceMemoryError:
                pass  # Continue without workspace context
        
        # Add workspace conversation history for better context
        workspace_name = self.app_config.current_workspace
        if workspace_name:
            workspace_history = self.session_manager.get_workspace_history(workspace_name, max_messages=30)
            context['workspace_conversation_history'] = self._process_history_for_context(workspace_history)
        
        # Store detected domain for debugging and system prompt
        context['detected_domain'] = current_domain
        context['current_domain'] = current_domain  # For system prompt formatting
        
        return context
    
    def _process_history_for_context(self, workspace_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Process workspace history for inclusion in system prompt context."""
        if not workspace_history:
            return []
        
        # Filter and prioritize messages for context
        processed_history = []
        total_tokens = 0
        max_tokens = 2000  # Limit for history context
        
        # Priority scoring: user preferences, personal info, recent interactions
        def score_message(msg):
            content = msg.get('content', '').lower()
            score = 1.0  # base score
            
            # Higher priority for messages containing personal information
            personal_keywords = ['我喜欢', '我的', '我想', '我需要', '我觉得', '我希望', 'i like', 'i want', 'i need', 'my']
            if any(keyword in content for keyword in personal_keywords):
                score += 2.0
            
            # Higher priority for user messages
            if msg.get('role') == 'user':
                score += 1.0
            
            # Recent messages get higher priority (already sorted by timestamp DESC)
            return score
        
        # Sort by priority score
        scored_messages = [(msg, score_message(msg)) for msg in workspace_history]
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        
        # Select messages within token limit
        for msg, score in scored_messages:
            content = msg.get('content', '')
            msg_tokens = self.llm_provider.count_tokens(content)
            
            if total_tokens + msg_tokens > max_tokens:
                break
                
            processed_history.append({
                'role': msg.get('role', 'unknown'),
                'content': content,
                'timestamp': msg.get('timestamp', ''),
                'priority_score': score
            })
            total_tokens += msg_tokens
            
            # Limit to most important 15 messages
            if len(processed_history) >= 15:
                break
        
        # Sort by timestamp for chronological context
        processed_history.sort(key=lambda x: x.get('timestamp', ''))
        
        return processed_history
    
    async def _process_insights(self, session_id: str) -> None:
        """Extract and apply insights from conversation."""
        try:
            # Get messages from session
            messages = self.session_manager.get_session_messages(session_id)
            
            # Extract insights
            context = await self._build_context()
            insights = self.memory_extractor.extract_from_conversation(messages, context)
            
            # Debug: Print insights info
            self._debug_print_insights(insights, session_id)
            
            # Store insights in session
            for insight in insights:
                self.session_manager.add_extracted_insight(
                    insight.insight_type,
                    insight.target_layer,
                    insight.content,
                    insight.confidence,
                    session_id
                )
            
            # Apply high-confidence insights
            for insight in insights:
                if insight.confidence > 0.7:
                    await self._apply_insight(insight)
            
        except Exception as e:
            # Log error but don't interrupt conversation
            self.console.print(f"[dim red]Warning: Failed to process insights: {e}[/dim red]")
    
    async def _apply_insight(self, insight) -> None:
        """Apply an insight to the appropriate memory layer."""
        try:
            if insight.target_layer == 'global':
                if insight.insight_type == 'preference':
                    # Parse and apply preference
                    if 'prefer' in insight.content.lower():
                        # This is a simplified approach - in production, you'd have more sophisticated parsing
                        pass
                elif insight.insight_type == 'knowledge':
                    self.global_memory.add_personal_insight(
                        insight.content, insight.confidence, "conversation"
                    )
            
            elif insight.target_layer == 'workspace' and self.workspace_memory:
                if insight.insight_type == 'pattern':
                    # Extract pattern info
                    self.workspace_memory.add_development_note(
                        "Pattern Insight",
                        insight.content,
                        ["pattern", "auto-extracted"]
                    )
                elif insight.insight_type == 'knowledge':
                    self.workspace_memory.add_development_note(
                        "Knowledge Insight",
                        insight.content,
                        ["knowledge", "auto-extracted"]
                    )
        
        except Exception as e:
            # Log error but don't interrupt
            self.console.print(f"[dim red]Warning: Failed to apply insight: {e}[/dim red]")
    
    def _display_welcome(self) -> None:
        """Display welcome message."""
        workspace = self.app_config.current_workspace or "No workspace"
        
        self.console.print("\n" + "=" * 60, style="cyan")
        self.console.print("🧠 Memory Chatbot - Three-Layer Memory Architecture", style="bold cyan")
        self.console.print("=" * 60, style="cyan")
        
        self.console.print(f"\n📁 Current workspace: {workspace}", style="blue")
        self.console.print(f"🤖 LLM Provider: {self.app_config.llm.provider}", style="blue")
        self.console.print(f"🎯 Model: {self.app_config.llm.model}", style="blue")
        
        self.console.print("\nType /help for commands, /quit to exit", style="dim")
    
    def _display_help(self) -> None:
        """Display help information."""
        help_text = """
**Available Commands:**
- `/help` - Show this help message
- `/status` - Show current session status
- `/quit`, `/exit`, `/q` - Exit the chat

**Tips:**
- All your preferences and insights are automatically learned and stored
- Switch workspaces to get project-specific context
- Use `chatbot config show` to see your current settings
"""
        self.console.print(Markdown(help_text))
    
    async def _display_status(self) -> None:
        """Display current session status."""
        stats = self.session_manager.get_stats()
        global_stats = self.global_memory.get_stats()
        
        self.console.print("\n📊 **Session Status:**", style="bold cyan")
        self.console.print(f"  • Messages in session: {len(self.session_manager.get_session_messages())}")
        self.console.print(f"  • Total sessions: {stats['total_sessions']}")
        self.console.print(f"  • Total insights: {global_stats['total_insights']}")
        
        if self.workspace_memory:
            ws_stats = self.workspace_memory.get_stats()
            self.console.print(f"  • Workspace notes: {ws_stats['development_notes']}")
            self.console.print(f"  • Best practices: {ws_stats['best_practices']}")
    
    def _debug_print_initialization(self) -> None:
        """Print initialization debug info."""
        if not self.debug_mode:
            return
        
        self.console.print("\n" + "🔧 DEBUG MODE ENABLED" + "\n", style="bold yellow")
        
        # Configuration info
        config_table = Table(title="🔧 Configuration Debug Info", box=None)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Provider", self.app_config.llm.provider)
        config_table.add_row("Model", self.app_config.llm.model)
        config_table.add_row("Temperature", str(self.app_config.llm.temperature))
        config_table.add_row("Max Tokens", str(self.app_config.llm.max_tokens))
        config_table.add_row("Base URL", self.app_config.llm.base_url or "Default")
        config_table.add_row("Timeout", f"{self.app_config.llm.timeout}s")
        config_table.add_row("Current Workspace", self.app_config.current_workspace or "None")
        
        self.console.print(config_table)
    
    def _debug_print_context(self, context: Dict[str, Any]) -> None:
        """Print context debug info."""
        if not self.debug_mode:
            return
        
        self.console.print("\n📋 Context Debug Info", style="bold cyan")
        
        # Show domain detection
        if 'detected_domain' in context:
            domain_color = {
                'technology': 'blue',
                'academic': 'yellow', 
                'creative': 'magenta',
                'business': 'green',
                'personal': 'cyan'
            }.get(context['detected_domain'], 'white')
            
            self.console.print(f"🎯 Detected Domain: [{domain_color}]{context['detected_domain'].title()}[/{domain_color}]")
        
        # User preferences with sources
        if 'preferences' in context:
            prefs_table = Table(title="User Preferences (Source: Global Memory)", box=None)
            prefs_table.add_column("Preference", style="cyan")
            prefs_table.add_column("Value", style="green")
            prefs_table.add_column("Source", style="yellow")
            
            prefs = context['preferences']
            domain = context.get('current_domain', 'general')
            source = f"Domain-specific ({domain})" if domain != 'general' else "Global defaults"
            
            prefs_table.add_row("Communication Style", prefs.get('communication_style', 'N/A'), source)
            prefs_table.add_row("Technical Depth", prefs.get('technical_depth', 'N/A'), source)
            prefs_table.add_row("Code Examples", prefs.get('code_examples', 'N/A'), source)
            prefs_table.add_row("Response Length", prefs.get('response_length', 'N/A'), source)
            
            self.console.print(prefs_table)
        
        # Workspace info with references
        if 'workspace' in context:
            ws = context['workspace']
            ws_table = Table(title="Workspace Context (Source: Workspace Memory)", box=None)
            ws_table.add_column("Property", style="cyan")
            ws_table.add_column("Value", style="green")
            ws_table.add_column("Reference", style="dim")
            
            ws_name = ws.get('name', 'N/A')
            ws_table.add_row("Name", ws_name, f"workspace/{ws_name}/config.yaml")
            ws_table.add_row("Project Stage", ws.get('project_stage', 'N/A'), "project_profile.project_stage")
            
            # Tech stack (only for technology domain)
            tech_stack = ws.get('tech_stack', {})
            if tech_stack:
                for category, techs in tech_stack.items():
                    if isinstance(techs, list):
                        ws_table.add_row(f"Tech Stack ({category})", ", ".join(techs), f"project_profile.tech_stack.{category}")
                    else:
                        ws_table.add_row(f"Tech Stack ({category})", str(techs), f"project_profile.tech_stack.{category}")
            
            # Domain-specific fields
            domain_type = ws.get('domain_type', 'general')
            if domain_type == 'academic' and ws.get('research_area'):
                ws_table.add_row("Research Area", ws.get('research_area'), "project_profile.research_area")
            elif domain_type == 'creative' and ws.get('creative_medium'):
                ws_table.add_row("Creative Medium", ws.get('creative_medium'), "project_profile.creative_medium")
            elif domain_type == 'business' and ws.get('business_sector'):
                ws_table.add_row("Business Sector", ws.get('business_sector'), "project_profile.business_sector")
            elif domain_type == 'personal' and ws.get('personal_goal'):
                ws_table.add_row("Personal Goal", ws.get('personal_goal'), "project_profile.personal_goal")
            
            self.console.print(ws_table)
        
        # Recent decisions with references
        if 'recent_decisions' in context and context['recent_decisions']:
            decisions_table = Table(title="Recent Architecture Decisions (Source: Workspace Memory)", box=None)
            decisions_table.add_column("Decision", style="cyan")
            decisions_table.add_column("Rationale", style="green")
            decisions_table.add_column("Reference", style="dim")
            
            for i, decision in enumerate(context['recent_decisions'][:3]):
                decisions_table.add_row(
                    decision.get('title', 'N/A'),
                    (decision.get('rationale', 'N/A')[:50] + "..." if len(decision.get('rationale', '')) > 50 else decision.get('rationale', 'N/A')),
                    f"architecture_decisions[{i}]"
                )
            
            self.console.print(decisions_table)
        
        # Best practices with references
        if 'relevant_practices' in context and context['relevant_practices']:
            practices_table = Table(title="Relevant Best Practices (Source: Workspace Memory)", box=None)
            practices_table.add_column("Category", style="cyan")
            practices_table.add_column("Practice", style="green")
            practices_table.add_column("Reference", style="dim")
            
            for i, practice in enumerate(context['relevant_practices'][:3]):
                practices_table.add_row(
                    practice.get('category', 'N/A'),
                    (practice.get('practice', 'N/A')[:60] + "..." if len(practice.get('practice', '')) > 60 else practice.get('practice', 'N/A')),
                    f"best_practices[{i}] (keyword-matched)"
                )
            
            self.console.print(practices_table)
        
        # Common patterns with references
        if 'common_patterns' in context and context['common_patterns']:
            patterns_table = Table(title="Common Patterns (Source: Workspace Memory)", box=None)
            patterns_table.add_column("Pattern", style="cyan")
            patterns_table.add_column("Implementation", style="green")
            patterns_table.add_column("Usage", style="yellow")
            patterns_table.add_column("Reference", style="dim")
            
            for i, pattern in enumerate(context['common_patterns'][:3]):
                patterns_table.add_row(
                    pattern.get('pattern', 'N/A'),
                    (pattern.get('implementation', 'N/A')[:50] + "..." if len(pattern.get('implementation', '')) > 50 else pattern.get('implementation', 'N/A')),
                    str(pattern.get('usage_count', 0)),
                    f"common_patterns[{i}] (keyword-matched)"
                )
            
            self.console.print(patterns_table)
        
        # Recent insights with sources
        if 'insights' in context and context['insights']:
            insights_table = Table(title="Recent Personal Insights (Source: Global Memory)", box=None)
            insights_table.add_column("Insight", style="green")
            insights_table.add_column("Source", style="yellow")
            insights_table.add_column("Reference", style="dim")
            
            for i, insight in enumerate(context['insights'][-3:]):
                insights_table.add_row(
                    insight[:80] + "..." if len(insight) > 80 else insight,
                    "Conversation extraction",
                    f"personal_insights[domain={context.get('current_domain', 'general')}]"
                )
            
            self.console.print(insights_table)
        
        # Knowledge domains
        if 'knowledge_domains' in context and context['knowledge_domains']:
            domains_panel = Panel(
                ", ".join(context['knowledge_domains']),
                title="Relevant Knowledge Domains (Source: Global Memory)",
                border_style="blue"
            )
            self.console.print(domains_panel)
    
    def _debug_print_conversation_history(self, recent_messages: List[Dict[str, str]]) -> None:
        """Print conversation history debug info."""
        if not self.debug_mode:
            return
        
        workspace_name = self.app_config.current_workspace or "No workspace"
        
        self.console.print(f"\n💬 Conversation History (Workspace: {workspace_name})", style="bold cyan")
        
        if not recent_messages:
            self.console.print("📝 No recent conversation history found", style="dim yellow")
            return
        
        # Show conversation history table
        history_table = Table(title=f"Recent Messages ({len(recent_messages)} messages)", box=None)
        history_table.add_column("#", style="dim", width=3)
        history_table.add_column("Role", style="cyan", width=10)
        history_table.add_column("Content Preview", style="green")
        history_table.add_column("Tokens", style="yellow", width=8)
        history_table.add_column("Time", style="dim", width=12)
        
        for i, msg in enumerate(recent_messages, 1):
            # Get content preview
            content = msg.get('content', '')
            preview = content[:100] + "..." if len(content) > 100 else content
            preview = preview.replace('\n', ' ').replace('\r', ' ')  # Clean up newlines
            
            # Estimate tokens if not available
            tokens = "~" + str(self.llm_provider.count_tokens(content))
            
            # Role styling
            role = msg.get('role', 'unknown')
            role_display = role.title()
            
            # Time (if available, otherwise show index)
            time_display = f"Msg {i}"
            
            history_table.add_row(
                str(i),
                role_display,
                preview,
                tokens,
                time_display
            )
        
        self.console.print(history_table)
        
        # Show conversation statistics and session info
        user_msgs = [m for m in recent_messages if m.get('role') == 'user']
        assistant_msgs = [m for m in recent_messages if m.get('role') == 'assistant']
        total_chars = sum(len(m.get('content', '')) for m in recent_messages)
        
        # Get current session info
        current_session = self.session_manager.current_session
        session_info = ""
        if current_session:
            session_info = f"📋 Current Session: {current_session.session_id[:8]}... | "
            if current_session.started_at:
                session_info += f"⏰ Started: {current_session.started_at.strftime('%H:%M:%S')} | "
        
        stats_panel = Panel(
            f"{session_info}"
            f"👤 User messages: {len(user_msgs)} | "
            f"🤖 Assistant messages: {len(assistant_msgs)} | "
            f"📊 Total characters: {total_chars:,} | "
            f"📁 Workspace: {workspace_name}",
            title="Conversation Statistics & Session Info",
            border_style="blue"
        )
        self.console.print(stats_panel)
        
        # Show database query details in debug
        if recent_messages:
            db_info_panel = Panel(
                f"🗄️  Database Query Details:\n"
                f"• Table: messages (SQLite)\n"
                f"• Filter: session_id = {current_session.session_id[:12] if current_session else 'unknown'}...\n"
                f"• Workspace filter: workspace_name = '{workspace_name}'\n"
                f"• Limit: max 10 recent messages\n"
                f"• Order: by timestamp DESC",
                title="Data Source Information",
                border_style="dim"
            )
            self.console.print(db_info_panel)
        
        # Show how history will be used
        context_usage_panel = Panel(
            "💡 This conversation history will be:\n"
            "• Added to the messages sent to the LLM\n"
            "• Used for domain detection and context building\n"
            "• Analyzed for insight extraction\n"
            "• Filtered by workspace to maintain project context",
            title="History Usage in Current Query",
            border_style="green"
        )
        self.console.print(context_usage_panel)
    
    def _debug_print_workspace_history(self, workspace_history: List[Dict[str, str]], workspace_name: str) -> None:
        """Print complete workspace conversation history debug info."""
        if not self.debug_mode or not workspace_history:
            return
        
        self.console.print(f"\n📚 Complete Workspace History ({workspace_name})", style="bold cyan")
        
        # Group messages by session for better visualization
        sessions = {}
        for msg in workspace_history:
            session_id = msg.get('session_id', 'unknown')
            session_key = session_id[:8] + "..." if len(session_id) > 8 else session_id
            if session_key not in sessions:
                sessions[session_key] = []
            sessions[session_key].append(msg)
        
        # Show history table
        history_table = Table(title=f"Workspace History ({len(workspace_history)} messages from {len(sessions)} sessions)", box=None)
        history_table.add_column("#", style="dim", width=3)
        history_table.add_column("Session", style="cyan", width=12)
        history_table.add_column("Role", style="yellow", width=10)
        history_table.add_column("Content Preview", style="green")
        history_table.add_column("Tokens", style="yellow", width=8)
        history_table.add_column("Time", style="dim", width=16)
        
        for i, msg in enumerate(workspace_history, 1):
            # Get content preview
            content = msg.get('content', '')
            preview = content[:80] + "..." if len(content) > 80 else content
            preview = preview.replace('\n', ' ').replace('\r', ' ')  # Clean up newlines
            
            # Estimate tokens
            tokens = "~" + str(self.llm_provider.count_tokens(content))
            
            # Role styling
            role = msg.get('role', 'unknown').title()
            
            # Session ID
            session_id = msg.get('session_id', 'unknown')
            session_display = session_id[:8] + "..." if len(session_id) > 8 else session_id
            
            # Time formatting
            timestamp = msg.get('timestamp', '')
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_display = dt.strftime('%m-%d %H:%M')
                except:
                    time_display = timestamp[:16]
            else:
                time_display = "Unknown"
            
            history_table.add_row(
                str(i),
                session_display,
                role,
                preview,
                tokens,
                time_display
            )
        
        self.console.print(history_table)
        
        # Show session statistics
        user_msgs = [m for m in workspace_history if m.get('role') == 'user']
        assistant_msgs = [m for m in workspace_history if m.get('role') == 'assistant']
        total_chars = sum(len(m.get('content', '')) for m in workspace_history)
        
        stats_panel = Panel(
            f"📊 Workspace Statistics:\n"
            f"• Total sessions: {len(sessions)}\n"
            f"• User messages: {len(user_msgs)}\n"
            f"• Assistant messages: {len(assistant_msgs)}\n"
            f"• Total characters: {total_chars:,}\n"
            f"• Average msg length: {total_chars // len(workspace_history) if workspace_history else 0} chars",
            title="Workspace Conversation Analytics",
            border_style="magenta"
        )
        self.console.print(stats_panel)
        
        # Show database query details
        db_query_panel = Panel(
            f"🗄️  Complete History Query:\n"
            f"• Query: JOIN messages + sessions ON session_id\n"
            f"• Filter: workspace_name = '{workspace_name}'\n"
            f"• Order: timestamp DESC (most recent first)\n"
            f"• Limit: 20 messages (configurable)\n"
            f"• Source: Cross-session workspace history",
            title="Database Query Details",
            border_style="dim"
        )
        self.console.print(db_query_panel)
    
    def _debug_print_system_prompt(self, system_message: str) -> None:
        """Print the complete system prompt."""
        if not self.debug_mode:
            return
        
        self.console.print("\n🤖 System Prompt Debug", style="bold cyan")
        
        # Display system message in a panel with syntax highlighting
        system_panel = Panel(
            system_message,
            title="Complete System Prompt",
            border_style="blue",
            expand=True
        )
        self.console.print(system_panel)
    
    def _debug_print_messages(self, messages: List[Dict[str, str]]) -> None:
        """Print the complete message list sent to LLM."""
        if not self.debug_mode:
            return
        
        self.console.print("\n📨 Messages Debug", style="bold cyan")
        
        for i, msg in enumerate(messages):
            role_color = {
                'system': 'blue',
                'user': 'green', 
                'assistant': 'yellow'
            }.get(msg['role'], 'white')
            
            content_preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
            
            msg_panel = Panel(
                content_preview,
                title=f"Message {i+1}: {msg['role'].title()}",
                border_style=role_color,
                expand=False
            )
            self.console.print(msg_panel)
    
    def _debug_print_api_call_info(self, messages: List[Dict[str, str]], 
                                  temperature: float, max_tokens: Optional[int],
                                  start_time: float, response = None) -> None:
        """Print API call debug info."""
        if not self.debug_mode:
            return
        
        end_time = time.time()
        call_duration = end_time - start_time
        
        # Token estimation and analysis
        estimated_input_tokens = sum(self.llm_provider.count_tokens(msg['content']) for msg in messages)
        system_tokens = self.llm_provider.count_tokens(messages[0]['content']) if messages and messages[0]['role'] == 'system' else 0
        
        api_table = Table(title="🔌 API Call Debug Info", box=None)
        api_table.add_column("Metric", style="cyan")
        api_table.add_column("Value", style="green")
        api_table.add_column("Details", style="dim")
        
        api_table.add_row("Call Duration", f"{call_duration:.2f}s", "Time to receive response")
        api_table.add_row("Provider", self.app_config.llm.provider, f"Model: {self.app_config.llm.model}")
        api_table.add_row("Temperature", str(temperature), "Creativity/randomness setting")
        api_table.add_row("Max Tokens", str(max_tokens) if max_tokens else "Default", "Output limit")
        api_table.add_row("Input Messages", str(len(messages)), f"System: 1, History: {len(messages) - 1 if messages else 0}")
        api_table.add_row("Estimated Input Tokens", str(estimated_input_tokens), f"System prompt: {system_tokens}, Others: {estimated_input_tokens - system_tokens}")
        
        if response:
            actual_input_tokens = response.metadata.get('prompt_tokens', 0)
            actual_output_tokens = response.metadata.get('completion_tokens', 0)
            
            api_table.add_row("Actual Input Tokens", str(actual_input_tokens), f"Estimation diff: {actual_input_tokens - estimated_input_tokens:+d}")
            api_table.add_row("Output Tokens", str(actual_output_tokens), "Response length")
            api_table.add_row("Total Tokens", str(actual_input_tokens + actual_output_tokens), "Billable tokens")
            api_table.add_row("Finish Reason", response.finish_reason, "Why generation stopped")
            
            # Cost estimation (rough)
            if self.app_config.llm.provider == 'openai':
                # Rough GPT-4 pricing
                input_cost = actual_input_tokens * 0.00003  # $30/1M input tokens
                output_cost = actual_output_tokens * 0.00006  # $60/1M output tokens
                total_cost = input_cost + output_cost
                api_table.add_row("Est. Cost", f"${total_cost:.4f}", f"In: ${input_cost:.4f}, Out: ${output_cost:.4f}")
            
            # Update debug info
            self._debug_info['api_call_time'] += call_duration
            self._debug_info['total_input_tokens'] += actual_input_tokens
            self._debug_info['total_output_tokens'] += actual_output_tokens
        else:
            api_table.add_row("Status", "❌ Failed", "API call did not complete")
        
        self.console.print(api_table)
        
        # Show context utilization
        if messages and messages[0]['role'] == 'system':
            self._debug_print_context_utilization(messages[0]['content'])
    
    def _debug_print_context_utilization(self, system_message: str) -> None:
        """Print analysis of how context is being used in the system prompt."""
        if not self.debug_mode:
            return
        
        # Analyze system message content
        utilization_table = Table(title="📊 Context Utilization Analysis", box=None)
        utilization_table.add_column("Component", style="cyan")
        utilization_table.add_column("Status", style="green")
        utilization_table.add_column("Details", style="dim")
        
        # Check for various context components
        components = {
            "User Preferences": ["communication_style", "technical_depth", "code_examples"],
            "Workspace Info": ["workspace", "tech_stack", "project"],
            "Architecture Decisions": ["decision", "rationale", "architecture"],
            "Best Practices": ["best practice", "practice", "guideline"],
            "Common Patterns": ["pattern", "implementation", "usage"],
            "Personal Insights": ["insight", "preference", "experience"],
            "Domain Context": ["domain", "technology", "academic", "creative", "business"]
        }
        
        for component, keywords in components.items():
            found = any(keyword.lower() in system_message.lower() for keyword in keywords)
            status = "✅ Included" if found else "❌ Not used"
            
            if found:
                # Count occurrences
                count = sum(system_message.lower().count(keyword.lower()) for keyword in keywords)
                details = f"~{count} references found"
            else:
                details = "No matching content"
            
            utilization_table.add_row(component, status, details)
        
        self.console.print(utilization_table)
        
        # Show system prompt statistics
        lines = system_message.split('\n')
        stats_panel = Panel(
            f"Lines: {len(lines)} | Characters: {len(system_message)} | Words: {len(system_message.split())}",
            title="System Prompt Statistics",
            border_style="blue"
        )
        self.console.print(stats_panel)
    
    def _debug_print_insights(self, insights: List, session_id: str) -> None:
        """Print insights extraction debug info."""
        if not self.debug_mode or not insights:
            return
        
        self.console.print("\n🧠 Insights Debug", style="bold cyan")
        
        insights_table = Table(title="Extracted Insights", box=None)
        insights_table.add_column("Type", style="cyan")
        insights_table.add_column("Target", style="yellow")
        insights_table.add_column("Confidence", style="green")
        insights_table.add_column("Content", style="white")
        
        for insight in insights:
            insights_table.add_row(
                insight.insight_type,
                insight.target_layer,
                f"{insight.confidence:.2f}",
                insight.content[:50] + "..." if len(insight.content) > 50 else insight.content
            )
        
        self.console.print(insights_table)
        
        high_confidence = [i for i in insights if i.confidence > 0.7]
        if high_confidence:
            self.console.print(f"🎯 {len(high_confidence)} high-confidence insights will be applied", style="green")
    
    def _debug_print_session_summary(self) -> None:
        """Print session summary debug info."""
        if not self.debug_mode:
            return
        
        self.console.print("\n📊 Session Summary", style="bold cyan")
        
        # Performance and usage summary
        summary_table = Table(title="Debug Session Stats", box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Details", style="dim")
        
        total_tokens = self._debug_info['total_input_tokens'] + self._debug_info['total_output_tokens']
        context_time = self._debug_info.get('context_build_time', 0)
        api_time = self._debug_info['api_call_time']
        total_time = context_time + api_time
        
        summary_table.add_row("Total Session Time", f"{total_time:.2f}s", f"Context: {context_time:.2f}s, API: {api_time:.2f}s")
        summary_table.add_row("Total Input Tokens", str(self._debug_info['total_input_tokens']), "Context + conversation history")
        summary_table.add_row("Total Output Tokens", str(self._debug_info['total_output_tokens']), "Generated responses")
        summary_table.add_row("Total Tokens", str(total_tokens), "Billable tokens used")
        
        # Cost estimation
        if self.app_config.llm.provider == 'openai' and total_tokens > 0:
            input_cost = self._debug_info['total_input_tokens'] * 0.00003
            output_cost = self._debug_info['total_output_tokens'] * 0.00006
            total_cost = input_cost + output_cost
            summary_table.add_row("Estimated Cost", f"${total_cost:.4f}", f"Input: ${input_cost:.4f}, Output: ${output_cost:.4f}")
        
        # Memory utilization
        workspace_name = self.app_config.current_workspace or "None"
        global_stats = self.global_memory.get_stats()
        
        summary_table.add_row("Active Workspace", workspace_name, "Current memory context")
        summary_table.add_row("Global Insights", str(global_stats['total_insights']), f"High confidence: {global_stats['high_confidence_insights']}")
        
        if self.workspace_memory:
            ws_stats = self.workspace_memory.get_stats()
            summary_table.add_row("Workspace Memory", f"{ws_stats['development_notes']} notes", f"Decisions: {ws_stats['architecture_decisions']}, Practices: {ws_stats['best_practices']}")
        
        self.console.print(summary_table)
        
        # Memory layer usage breakdown
        memory_panel = Panel(
            f"🧠 Memory Layers Used:\n"
            f"• Global Layer: User preferences, personal insights, cross-project knowledge\n"
            f"• Workspace Layer: {workspace_name} project context, tech stack, patterns\n"
            f"• Session Layer: Current conversation history and extracted insights",
            title="Three-Layer Memory Architecture Status",
            border_style="yellow"
        )
        self.console.print(memory_panel)
        
        # Final debug summary
        if total_time > 0:
            efficiency_msg = f"⚡ Performance: {total_tokens/total_time:.0f} tokens/sec"
            if context_time > api_time:
                efficiency_msg += " (Context building is bottleneck)"
            elif api_time > context_time * 3:
                efficiency_msg += " (API latency is bottleneck)"
            else:
                efficiency_msg += " (Balanced performance)"
            
            self.console.print(f"\n{efficiency_msg}", style="bold blue")