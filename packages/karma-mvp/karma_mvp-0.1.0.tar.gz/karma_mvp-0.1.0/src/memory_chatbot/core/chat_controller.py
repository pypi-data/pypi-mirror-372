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
        """Build context from memory layers with domain detection."""
        context = {}
        
        # Detect current conversation domain
        workspace_domain = None
        if self.workspace_memory:
            workspace_domain = getattr(self.workspace_memory.config.project_profile, 'domain_type', 'general')
        
        # Analyze recent messages for domain detection
        current_domain = 'general'
        if recent_messages:
            domain_analysis = self.domain_detector.analyze_conversation(recent_messages, workspace_domain)
            if domain_analysis:
                # Get domain with highest confidence, but require minimum threshold
                top_domain = max(domain_analysis.keys(), key=lambda d: domain_analysis[d])
                if domain_analysis[top_domain] > 0.4:
                    current_domain = top_domain
        
        # Use workspace domain as fallback
        if current_domain == 'general' and workspace_domain:
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
        
        # Store detected domain for debugging
        context['detected_domain'] = current_domain
        
        return context
    
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
        
        # User preferences
        if 'preferences' in context:
            prefs_table = Table(title="User Preferences", box=None)
            prefs_table.add_column("Preference", style="cyan")
            prefs_table.add_column("Value", style="green")
            
            prefs = context['preferences']
            prefs_table.add_row("Communication Style", prefs.get('communication_style', 'N/A'))
            prefs_table.add_row("Technical Depth", prefs.get('technical_depth', 'N/A'))
            prefs_table.add_row("Code Examples", prefs.get('code_examples', 'N/A'))
            prefs_table.add_row("Response Length", prefs.get('response_length', 'N/A'))
            
            self.console.print(prefs_table)
        
        # Workspace info
        if 'workspace' in context:
            ws = context['workspace']
            ws_table = Table(title="Workspace Context", box=None)
            ws_table.add_column("Property", style="cyan")
            ws_table.add_column("Value", style="green")
            
            ws_table.add_row("Name", ws.get('name', 'N/A'))
            ws_table.add_row("Project Stage", ws.get('project_stage', 'N/A'))
            
            # Tech stack (only for technology domain)
            tech_stack = ws.get('tech_stack', {})
            if tech_stack:
                for category, techs in tech_stack.items():
                    if isinstance(techs, list):
                        ws_table.add_row(f"Tech Stack ({category})", ", ".join(techs))
                    else:
                        ws_table.add_row(f"Tech Stack ({category})", str(techs))
            
            # Domain-specific fields
            domain_type = ws.get('domain_type', 'general')
            if domain_type == 'academic' and ws.get('research_area'):
                ws_table.add_row("Research Area", ws.get('research_area'))
            elif domain_type == 'creative' and ws.get('creative_medium'):
                ws_table.add_row("Creative Medium", ws.get('creative_medium'))
            elif domain_type == 'business' and ws.get('business_sector'):
                ws_table.add_row("Business Sector", ws.get('business_sector'))
            elif domain_type == 'personal' and ws.get('personal_goal'):
                ws_table.add_row("Personal Goal", ws.get('personal_goal'))
            
            self.console.print(ws_table)
        
        # Recent insights
        if 'insights' in context and context['insights']:
            insights_panel = Panel(
                "\n".join([f"• {insight}" for insight in context['insights'][-3:]]),
                title="Recent Personal Insights",
                border_style="yellow"
            )
            self.console.print(insights_panel)
    
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
        
        # Token estimation
        estimated_input_tokens = sum(self.llm_provider.count_tokens(msg['content']) for msg in messages)
        
        api_table = Table(title="🔌 API Call Debug Info", box=None)
        api_table.add_column("Metric", style="cyan")
        api_table.add_column("Value", style="green")
        
        api_table.add_row("Call Duration", f"{call_duration:.2f}s")
        api_table.add_row("Temperature", str(temperature))
        api_table.add_row("Max Tokens", str(max_tokens) if max_tokens else "Default")
        api_table.add_row("Input Messages", str(len(messages)))
        api_table.add_row("Estimated Input Tokens", str(estimated_input_tokens))
        
        if response:
            api_table.add_row("Actual Tokens Used", str(response.tokens_used))
            api_table.add_row("Output Tokens", str(response.metadata.get('completion_tokens', 'N/A')))
            api_table.add_row("Finish Reason", response.finish_reason)
            
            # Update debug info
            self._debug_info['api_call_time'] += call_duration
            self._debug_info['total_input_tokens'] += response.metadata.get('prompt_tokens', 0)
            self._debug_info['total_output_tokens'] += response.metadata.get('completion_tokens', 0)
        
        self.console.print(api_table)
    
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
        
        summary_table = Table(title="Debug Session Stats", box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total API Call Time", f"{self._debug_info['api_call_time']:.2f}s")
        summary_table.add_row("Total Input Tokens", str(self._debug_info['total_input_tokens']))
        summary_table.add_row("Total Output Tokens", str(self._debug_info['total_output_tokens']))
        summary_table.add_row("Total Tokens", str(self._debug_info['total_input_tokens'] + self._debug_info['total_output_tokens']))
        
        self.console.print(summary_table)