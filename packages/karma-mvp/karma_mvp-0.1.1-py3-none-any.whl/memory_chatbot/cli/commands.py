"""CLI commands for the memory chatbot."""

import click
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text

from ..config.loader import ConfigLoader
from ..core.global_memory import GlobalMemory
from ..core.workspace_memory import WorkspaceMemory
from ..core.session_manager import SessionManager, Session, Message
from ..providers import ProviderRegistry
from ..utils.crypto import CryptoManager


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Memory Chatbot - Three-layer memory architecture AI assistant."""
    pass


@cli.command()
@click.argument('prompt', required=False)
@click.option('--model', default=None, help='LLM model to use')
@click.option('--temperature', default=0.7, help='Sampling temperature')
@click.option('--max-tokens', default=None, type=int, help='Maximum tokens to generate')
@click.option('--debug', is_flag=True, help='Enable debug mode to show system prompts and detailed info')
def chat(prompt: Optional[str], model: Optional[str], temperature: float, max_tokens: Optional[int], debug: bool):
    """Start an interactive chat session or send a single message."""
    from ..core.chat_controller import ChatController
    
    controller = ChatController(debug_mode=debug)
    
    if prompt:
        # Single prompt mode
        asyncio.run(controller.single_chat(prompt, model=model, temperature=temperature, max_tokens=max_tokens))
    else:
        # Interactive mode
        asyncio.run(controller.interactive_chat(model=model, temperature=temperature, max_tokens=max_tokens))


@cli.command()
@click.argument('prompt')
@click.option('--model', default=None, help='LLM model to use')
@click.option('--temperature', default=0.7, help='Sampling temperature')
@click.option('--max-tokens', default=None, type=int, help='Maximum tokens to generate')
@click.option('--debug', is_flag=True, help='Enable debug mode to show system prompts and detailed info')
def ask(prompt: str, model: Optional[str], temperature: float, max_tokens: Optional[int], debug: bool):
    """Send a single question to the chatbot."""
    from ..core.chat_controller import ChatController
    
    controller = ChatController(debug_mode=debug)
    asyncio.run(controller.single_chat(prompt, model=model, temperature=temperature, max_tokens=max_tokens))


# Workspace management commands
@cli.group()
def workspace():
    """Workspace management commands."""
    pass


@workspace.command('create')
@click.argument('name')
@click.option('--description', default="", help='Workspace description')
@click.option('--domain', type=click.Choice(['technology', 'academic', 'creative', 'business', 'personal']), 
              default='technology', help='Domain type for workspace')
@click.option('--tech-stack', help='Comma-separated list of technologies (for technology domain)')
@click.option('--research-area', help='Research area (for academic domain)')
@click.option('--creative-medium', help='Creative medium (for creative domain)')
@click.option('--business-sector', help='Business sector (for business domain)')
@click.option('--personal-goal', help='Personal goal (for personal domain)')
def create_workspace(name: str, description: str, domain: str, tech_stack: Optional[str],
                    research_area: Optional[str], creative_medium: Optional[str], 
                    business_sector: Optional[str], personal_goal: Optional[str]):
    """Create a new workspace."""
    try:
        ws_memory = WorkspaceMemory()
        
        # Build domain-specific profile
        profile_data = {
            'domain_type': domain,
            'team_size': 1,
            'project_stage': 'planning'
        }
        
        # Add domain-specific fields
        if domain == 'technology' and tech_stack:
            technologies = [tech.strip() for tech in tech_stack.split(',')]
            profile_data['tech_stack'] = {'technologies': technologies}
        elif domain == 'academic' and research_area:
            profile_data['research_area'] = research_area
        elif domain == 'creative' and creative_medium:
            profile_data['creative_medium'] = creative_medium
        elif domain == 'business' and business_sector:
            profile_data['business_sector'] = business_sector
        elif domain == 'personal' and personal_goal:
            profile_data['personal_goal'] = personal_goal
        
        # Create workspace with domain-specific template
        _create_domain_workspace(ws_memory, name, description, domain, profile_data)
        
        # Update app config to switch to new workspace
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        app_config.current_workspace = name
        config_loader.save_app_config(app_config)
        
        console.print(f"✅ {domain.title()} workspace '{name}' created successfully!", style="green")
        console.print(f"🔄 Switched to workspace '{name}'", style="blue")
        
    except Exception as e:
        console.print(f"❌ Error creating workspace: {e}", style="red")


@workspace.command('switch')
@click.argument('name')
def switch_workspace(name: str):
    """Switch to a different workspace."""
    try:
        # Check if workspace exists
        workspaces = WorkspaceMemory.list_workspaces()
        if name not in workspaces:
            console.print(f"❌ Workspace '{name}' does not exist", style="red")
            console.print(f"Available workspaces: {', '.join(workspaces)}", style="yellow")
            return
        
        # Update app config
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        app_config.current_workspace = name
        config_loader.save_app_config(app_config)
        
        console.print(f"🔄 Switched to workspace '{name}'", style="green")
        
    except Exception as e:
        console.print(f"❌ Error switching workspace: {e}", style="red")


@workspace.command('list')
def list_workspaces():
    """List all available workspaces."""
    try:
        workspaces = WorkspaceMemory.list_workspaces()
        
        if not workspaces:
            console.print("No workspaces found. Create one with 'chatbot workspace create <name>'", style="yellow")
            return
        
        # Get current workspace
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        current = app_config.current_workspace
        
        table = Table(title="Available Workspaces")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        
        for ws in workspaces:
            status = "Current" if ws == current else ""
            table.add_row(ws, status)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error listing workspaces: {e}", style="red")


@workspace.command('delete')
@click.argument('name')
@click.option('--force', is_flag=True, help='Skip confirmation')
def delete_workspace(name: str, force: bool):
    """Delete a workspace."""
    try:
        # Check if workspace exists
        workspaces = WorkspaceMemory.list_workspaces()
        if name not in workspaces:
            console.print(f"❌ Workspace '{name}' does not exist", style="red")
            return
        
        # Confirm deletion
        if not force:
            if not Confirm.ask(f"Are you sure you want to delete workspace '{name}'?"):
                console.print("❌ Deletion cancelled", style="yellow")
                return
        
        WorkspaceMemory.delete_workspace(name)
        console.print(f"✅ Workspace '{name}' deleted successfully!", style="green")
        
        # If current workspace was deleted, clear it
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        if app_config.current_workspace == name:
            app_config.current_workspace = None
            config_loader.save_app_config(app_config)
            console.print("🔄 No active workspace", style="blue")
        
    except Exception as e:
        console.print(f"❌ Error deleting workspace: {e}", style="red")


@workspace.command('info')
@click.argument('name', required=False)
def workspace_info(name: Optional[str]):
    """Show workspace information."""
    try:
        if not name:
            # Get current workspace
            config_loader = ConfigLoader()
            app_config = config_loader.load_app_config()
            name = app_config.current_workspace
        
        if not name:
            console.print("❌ No workspace specified and no current workspace set", style="red")
            return
        
        # Load workspace
        ws_path = Path.cwd() / name / "workspace"
        ws_memory = WorkspaceMemory(ws_path)
        ws_memory.load_workspace()
        
        # Display info
        info = ws_memory.get_stats()
        
        table = Table(title=f"Workspace Information: {name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Name", info['name'])
        table.add_row("Tech Stack Categories", str(info['tech_stack_categories']))
        table.add_row("Architecture Decisions", str(info['architecture_decisions']))
        table.add_row("Best Practices", str(info['best_practices']))
        table.add_row("Common Patterns", str(info['common_patterns']))
        table.add_row("Development Notes", str(info['development_notes']))
        table.add_row("Last Updated", info['last_updated'] or "Never")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error getting workspace info: {e}", style="red")


# Memory management commands
@cli.group()
def memory():
    """Memory management commands."""
    pass


@memory.command('show')
@click.option('--global', 'show_global', is_flag=True, help='Show global memory')
@click.option('--workspace', 'show_workspace', is_flag=True, help='Show workspace memory')
@click.option('--sessions', 'show_sessions', is_flag=True, help='Show session memory')
def show_memory(show_global: bool, show_workspace: bool, show_sessions: bool):
    """Show memory information."""
    try:
        if not any([show_global, show_workspace, show_sessions]):
            # Show all by default
            show_global = show_workspace = show_sessions = True
        
        if show_global:
            console.print("[bold cyan]Global Memory[/bold cyan]")
            global_memory = GlobalMemory()
            stats = global_memory.get_stats()
            
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Insights", str(stats['total_insights']))
            table.add_row("High Confidence Insights", str(stats['high_confidence_insights']))
            table.add_row("Knowledge Domains", str(stats['knowledge_domains']))
            table.add_row("Last Updated", stats['last_updated'] or "Never")
            
            console.print(table)
            console.print()
        
        if show_workspace:
            console.print("[bold cyan]Workspace Memory[/bold cyan]")
            
            # Get current workspace
            config_loader = ConfigLoader()
            app_config = config_loader.load_app_config()
            
            if not app_config.current_workspace:
                console.print("❌ No active workspace", style="red")
            else:
                ws_path = Path.cwd() / app_config.current_workspace / "workspace"
                ws_memory = WorkspaceMemory(ws_path)
                ws_memory.load_workspace()
                stats = ws_memory.get_stats()
                
                table = Table()
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Workspace", stats['name'])
                table.add_row("Architecture Decisions", str(stats['architecture_decisions']))
                table.add_row("Best Practices", str(stats['best_practices']))
                table.add_row("Common Patterns", str(stats['common_patterns']))
                table.add_row("Development Notes", str(stats['development_notes']))
                
                console.print(table)
            console.print()
        
        if show_sessions:
            console.print("[bold cyan]Session Memory[/bold cyan]")
            session_manager = SessionManager()
            stats = session_manager.get_stats()
            
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Sessions", str(stats['total_sessions']))
            table.add_row("Total Messages", str(stats['total_messages']))
            table.add_row("Total Insights", str(stats['total_insights']))
            table.add_row("Applied Insights", str(stats['applied_insights']))
            table.add_row("Pending Insights", str(stats['pending_insights']))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error showing memory: {e}", style="red")


@memory.command('clean')
@click.option('--sessions', is_flag=True, help='Clean old sessions')
@click.option('--older-than', default=90, type=int, help='Days threshold for cleanup')
@click.option('--force', is_flag=True, help='Skip confirmation')
def clean_memory(sessions: bool, older_than: int, force: bool):
    """Clean old memory data."""
    try:
        if not sessions:
            console.print("❌ Specify what to clean with --sessions", style="red")
            return
        
        if not force:
            if not Confirm.ask(f"Are you sure you want to clean sessions older than {older_than} days?"):
                console.print("❌ Cleanup cancelled", style="yellow")
                return
        
        session_manager = SessionManager()
        removed = session_manager.clean_old_sessions(older_than)
        
        console.print(f"✅ Cleaned {removed} old sessions", style="green")
        
    except Exception as e:
        console.print(f"❌ Error cleaning memory: {e}", style="red")


# History commands
@cli.group()
def history():
    """Conversation history management commands."""
    pass


@history.command('list')
@click.option('--workspace', help='Filter by workspace name')
@click.option('--limit', default=10, help='Number of sessions to show')
@click.option('--with-messages', is_flag=True, help='Show messages in each session')
def list_sessions(workspace: Optional[str], limit: int, with_messages: bool):
    """List conversation sessions."""
    try:
        session_manager = SessionManager()
        sessions = session_manager.get_sessions(workspace_name=workspace, limit=limit)
        
        if not sessions:
            filter_text = f" in workspace '{workspace}'" if workspace else ""
            console.print(f"No sessions found{filter_text}.", style="yellow")
            return
        
        # Display sessions
        table = Table(title=f"Conversation History{' - ' + workspace if workspace else ''}")
        table.add_column("Session", style="cyan")
        table.add_column("Workspace", style="green")
        table.add_column("Started", style="blue")
        table.add_column("Messages", style="yellow", justify="right")
        table.add_column("Duration", style="magenta")
        
        for session in sessions:
            # Calculate duration
            end_time = session.ended_at or datetime.now()
            duration = end_time - session.started_at
            duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
            
            # Truncate session ID for display
            session_display = session.session_id[:8] + "..."
            
            table.add_row(
                session_display,
                session.workspace_name or "None",
                session.started_at.strftime("%Y-%m-%d %H:%M"),
                str(session.message_count),
                duration_str
            )
        
        console.print(table)
        
        if with_messages:
            console.print("\n" + "=" * 60, style="cyan")
            console.print("📝 Messages in Sessions", style="bold cyan")
            console.print("=" * 60, style="cyan")
            
            for session in sessions:
                _display_session_messages(session.session_id, session.workspace_name)
        
    except Exception as e:
        console.print(f"❌ Error listing sessions: {e}", style="red")


@history.command('show')
@click.argument('session_id')
@click.option('--format', type=click.Choice(['table', 'chat', 'json']), default='chat', help='Display format')
def show_session(session_id: str, format: str):
    """Show detailed conversation for a specific session."""
    try:
        session_manager = SessionManager()
        
        # Find session by partial ID match
        sessions = session_manager.get_sessions(limit=100)
        matching_session = None
        
        for session in sessions:
            if session.session_id.startswith(session_id):
                matching_session = session
                break
        
        if not matching_session:
            console.print(f"❌ Session not found: {session_id}", style="red")
            console.print("💡 Use 'chatbot history list' to see available sessions", style="blue")
            return
        
        # Get messages for the session
        messages = session_manager.get_session_messages(matching_session.session_id)
        
        if not messages:
            console.print(f"No messages found in session {session_id}", style="yellow")
            return
        
        # Display session info
        _display_session_info(matching_session, messages)
        
        # Display messages in chosen format
        if format == 'table':
            _display_messages_table(messages)
        elif format == 'json':
            _display_messages_json(messages)
        else:  # chat format (default)
            _display_messages_chat(messages)
    
    except Exception as e:
        console.print(f"❌ Error showing session: {e}", style="red")


@history.command('search')
@click.argument('query')
@click.option('--workspace', help='Search within specific workspace')
@click.option('--limit', default=20, help='Number of matching messages to show')
def search_messages(query: str, workspace: Optional[str], limit: int):
    """Search for messages containing specific text."""
    try:
        session_manager = SessionManager()
        
        # Get all sessions (filtered by workspace if specified)
        sessions = session_manager.get_sessions(workspace_name=workspace, limit=500)
        
        matching_messages = []
        
        for session in sessions:
            messages = session_manager.get_session_messages(session.session_id)
            for message in messages:
                if query.lower() in message.content.lower():
                    matching_messages.append((session, message))
                    if len(matching_messages) >= limit:
                        break
            if len(matching_messages) >= limit:
                break
        
        if not matching_messages:
            filter_text = f" in workspace '{workspace}'" if workspace else ""
            console.print(f"No messages found containing '{query}'{filter_text}.", style="yellow")
            return
        
        console.print(f"\n🔍 Found {len(matching_messages)} messages containing '{query}'", style="bold cyan")
        console.print("=" * 60, style="cyan")
        
        for session, message in matching_messages:
            # Highlight the search term
            content_preview = message.content[:200] + "..." if len(message.content) > 200 else message.content
            highlighted_content = content_preview.replace(
                query, f"[bold yellow]{query}[/bold yellow]"
            ).replace(
                query.lower(), f"[bold yellow]{query.lower()}[/bold yellow]"
            ).replace(
                query.upper(), f"[bold yellow]{query.upper()}[/bold yellow]"
            )
            
            console.print(f"\n📅 {message.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                         f"🏢 {session.workspace_name or 'No workspace'} | "
                         f"👤 {message.role.title()}", style="dim")
            console.print(f"💬 {highlighted_content}")
    
    except Exception as e:
        console.print(f"❌ Error searching messages: {e}", style="red")


@history.command('clean')
@click.option('--older-than', default=90, type=int, help='Days threshold for cleanup')
@click.option('--force', is_flag=True, help='Skip confirmation')
def clean_history(older_than: int, force: bool):
    """Clean old conversation history."""
    try:
        if not force:
            if not Confirm.ask(f"Are you sure you want to clean conversations older than {older_than} days?"):
                console.print("❌ Cleanup cancelled", style="yellow")
                return
        
        session_manager = SessionManager()
        removed = session_manager.clean_old_sessions(older_than)
        
        console.print(f"✅ Cleaned {removed} old conversations", style="green")
        
    except Exception as e:
        console.print(f"❌ Error cleaning history: {e}", style="red")


def _display_session_info(session: Session, messages: List) -> None:
    """Display session information."""
    info_table = Table(title=f"Session {session.session_id[:8]}...", box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Full Session ID", session.session_id)
    info_table.add_row("Workspace", session.workspace_name or "None")
    info_table.add_row("Started", session.started_at.strftime("%Y-%m-%d %H:%M:%S"))
    info_table.add_row("Ended", session.ended_at.strftime("%Y-%m-%d %H:%M:%S") if session.ended_at else "Ongoing")
    info_table.add_row("Messages", str(len(messages)))
    
    if messages:
        total_tokens = sum(msg.tokens_used for msg in messages if msg.tokens_used)
        info_table.add_row("Total Tokens", str(total_tokens) if total_tokens else "Unknown")
    
    console.print(info_table)


def _display_session_messages(session_id: str, workspace_name: Optional[str]) -> None:
    """Display messages for a specific session."""
    session_manager = SessionManager()
    messages = session_manager.get_session_messages(session_id)
    
    if not messages:
        return
    
    console.print(f"\n📋 Session {session_id[:8]}... ({workspace_name or 'No workspace'})", style="bold blue")
    
    for i, msg in enumerate(messages[-3:], 1):  # Show last 3 messages
        role_style = "green" if msg.role == "user" else "yellow"
        content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        console.print(f"  {i}. [{role_style}]{msg.role.title()}:[/{role_style}] {content_preview}")


def _display_messages_table(messages: List) -> None:
    """Display messages in table format."""
    table = Table(title="Conversation Messages")
    table.add_column("Time", style="blue")
    table.add_column("Role", style="green")
    table.add_column("Content", style="white", max_width=60)
    table.add_column("Tokens", style="yellow", justify="right")
    
    for msg in messages:
        content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        table.add_row(
            msg.timestamp.strftime("%H:%M:%S"),
            msg.role.title(),
            content_preview,
            str(msg.tokens_used) if msg.tokens_used else "-"
        )
    
    console.print(table)


def _display_messages_chat(messages: List) -> None:
    """Display messages in chat format."""
    console.print("\n💬 Conversation", style="bold cyan")
    console.print("=" * 60, style="cyan")
    
    for msg in messages:
        role_color = "green" if msg.role == "user" else "yellow"
        timestamp = msg.timestamp.strftime("%H:%M")
        
        console.print(f"\n[{role_color}]👤 {msg.role.title()} ({timestamp}):[/{role_color}]")
        
        # Format content with proper line breaks
        content_lines = msg.content.split('\n')
        for line in content_lines:
            console.print(f"  {line}")
        
        if msg.tokens_used:
            console.print(f"  [dim](Tokens: {msg.tokens_used})[/dim]")


def _display_messages_json(messages: List) -> None:
    """Display messages in JSON format."""
    import json
    from datetime import datetime
    
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            "id": msg.id,
            "session_id": msg.session_id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp,
            "tokens_used": msg.tokens_used
        })
    
    json_output = json.dumps(messages_data, indent=2, default=json_serializer)
    console.print(json_output)


def _create_domain_workspace(ws_memory, name: str, description: str, domain: str, profile_data: Dict[str, Any]) -> None:
    """Create workspace with domain-specific templates and initial content."""
    
    # Domain-specific templates
    domain_templates = {
        'technology': {
            'best_practices': [
                {'category': 'Code Quality', 'practice': 'Write clean, readable code with proper documentation', 'reason': 'Improves maintainability and team collaboration'},
                {'category': 'Testing', 'practice': 'Implement comprehensive unit and integration tests', 'reason': 'Ensures code reliability and prevents regressions'},
                {'category': 'Version Control', 'practice': 'Use meaningful commit messages and feature branches', 'reason': 'Facilitates collaboration and code history tracking'}
            ],
            'patterns': [
                {'pattern': 'MVC Architecture', 'implementation': 'Separate concerns using Model-View-Controller pattern'},
                {'pattern': 'Dependency Injection', 'implementation': 'Use DI containers for loose coupling and testability'}
            ]
        },
        'academic': {
            'best_practices': [
                {'category': 'Research Methodology', 'practice': 'Follow systematic literature review protocols', 'reason': 'Ensures comprehensive and unbiased research'},
                {'category': 'Data Management', 'practice': 'Maintain detailed research logs and version control', 'reason': 'Enables reproducibility and collaboration'},
                {'category': 'Citation Standards', 'practice': 'Use consistent citation style and reference management', 'reason': 'Maintains academic integrity and credibility'}
            ],
            'patterns': [
                {'pattern': 'Research Design', 'implementation': 'Define clear research questions, hypotheses, and methodology'},
                {'pattern': 'Data Analysis', 'implementation': 'Use appropriate statistical methods and document all assumptions'}
            ]
        },
        'creative': {
            'best_practices': [
                {'category': 'Creative Process', 'practice': 'Maintain regular creative practice and experimentation', 'reason': 'Develops skills and generates new ideas'},
                {'category': 'Feedback Integration', 'practice': 'Seek diverse perspectives and iterate based on feedback', 'reason': 'Improves work quality and audience connection'},
                {'category': 'Portfolio Management', 'practice': 'Document creative process and maintain organized portfolio', 'reason': 'Tracks progress and showcases capabilities'}
            ],
            'patterns': [
                {'pattern': 'Design Thinking', 'implementation': 'Empathize, define, ideate, prototype, and test iteratively'},
                {'pattern': 'Creative Constraints', 'implementation': 'Use limitations to spark creativity and focus effort'}
            ]
        },
        'business': {
            'best_practices': [
                {'category': 'Strategic Planning', 'practice': 'Define clear objectives with measurable outcomes', 'reason': 'Provides direction and enables progress tracking'},
                {'category': 'Stakeholder Management', 'practice': 'Maintain regular communication with all stakeholders', 'reason': 'Ensures alignment and identifies issues early'},
                {'category': 'Risk Management', 'practice': 'Identify, assess, and mitigate potential risks', 'reason': 'Protects business continuity and value'}
            ],
            'patterns': [
                {'pattern': 'SWOT Analysis', 'implementation': 'Regularly assess Strengths, Weaknesses, Opportunities, and Threats'},
                {'pattern': 'Agile Planning', 'implementation': 'Use iterative planning with regular review and adaptation'}
            ]
        },
        'personal': {
            'best_practices': [
                {'category': 'Goal Setting', 'practice': 'Set specific, measurable, achievable goals', 'reason': 'Provides clear direction and motivation'},
                {'category': 'Habit Formation', 'practice': 'Start small and build consistency gradually', 'reason': 'Creates sustainable long-term changes'},
                {'category': 'Reflection', 'practice': 'Regular self-assessment and learning review', 'reason': 'Promotes continuous improvement and self-awareness'}
            ],
            'patterns': [
                {'pattern': 'Growth Mindset', 'implementation': 'View challenges as opportunities to learn and improve'},
                {'pattern': 'Time Management', 'implementation': 'Prioritize important tasks and eliminate distractions'}
            ]
        }
    }
    
    # Create workspace with domain template
    template = domain_templates.get(domain, domain_templates['technology'])
    ws_memory.create_workspace(name, description, profile_data)
    
    # Add domain-specific initial content
    for bp in template['best_practices']:
        ws_memory.add_best_practice(bp['category'], bp['practice'], bp['reason'])
    
    for pattern in template['patterns']:
        ws_memory.add_common_pattern(pattern['pattern'], pattern['implementation'])
    
    # Add domain-specific development note
    domain_descriptions = {
        'technology': f"🛠️  Technology workspace for {name}. Focus on code quality, testing, and scalable architecture.",
        'academic': f"🎓 Academic workspace for {name}. Emphasis on rigorous methodology and reproducible research.",
        'creative': f"🎨 Creative workspace for {name}. Encouraging experimentation and iterative refinement.", 
        'business': f"💼 Business workspace for {name}. Strategic focus on objectives, stakeholders, and risk management.",
        'personal': f"🌱 Personal workspace for {name}. Supporting growth, habits, and continuous learning."
    }
    
    ws_memory.add_development_note(
        f"{domain.title()} Workspace Setup",
        domain_descriptions[domain],
        [domain, "setup", "template"]
    )


# Configuration commands  
@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command('show')
@click.option('--global', 'show_global', is_flag=True, help='Show global config')
@click.option('--workspace', 'show_workspace', is_flag=True, help='Show workspace config')
@click.option('--llm', 'show_llm', is_flag=True, help='Show LLM config')
def show_config(show_global: bool, show_workspace: bool, show_llm: bool):
    """Show configuration."""
    try:
        if not any([show_global, show_workspace, show_llm]):
            show_global = show_workspace = show_llm = True
        
        if show_global:
            console.print("[bold cyan]Global Configuration[/bold cyan]")
            global_memory = GlobalMemory()
            prefs = global_memory.get_preferences()
            
            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Communication Style", prefs.communication_style)
            table.add_row("Technical Depth", prefs.technical_depth)
            table.add_row("Code Examples", prefs.code_examples)
            table.add_row("Language", prefs.language_preference)
            table.add_row("Response Length", prefs.response_length)
            
            console.print(table)
            console.print()
        
        if show_workspace:
            console.print("[bold cyan]Workspace Configuration[/bold cyan]")
            
            config_loader = ConfigLoader()
            app_config = config_loader.load_app_config()
            
            if not app_config.current_workspace:
                console.print("❌ No active workspace", style="red")
            else:
                ws_path = Path.cwd() / app_config.current_workspace / "workspace"
                ws_memory = WorkspaceMemory(ws_path)
                ws_memory.load_workspace()
                
                profile = ws_memory.config.project_profile
                
                table = Table()
                table.add_column("Setting", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Project Stage", profile.project_stage)
                table.add_row("Team Size", str(profile.team_size))
                
                for category, techs in profile.tech_stack.items():
                    if isinstance(techs, list):
                        table.add_row(f"Tech Stack ({category})", ", ".join(techs))
                    else:
                        table.add_row(f"Tech Stack ({category})", str(techs))
                
                console.print(table)
                console.print()
        
        if show_llm:
            console.print("[bold cyan]LLM Configuration[/bold cyan]")
            
            config_loader = ConfigLoader()
            app_config = config_loader.load_app_config()
            llm = app_config.llm
            
            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Provider", llm.provider)
            table.add_row("Model", llm.model)
            table.add_row("Temperature", str(llm.temperature))
            table.add_row("Max Tokens", str(llm.max_tokens))
            table.add_row("Base URL", llm.base_url or "Default")
            table.add_row("Organization", llm.organization or "None")
            table.add_row("Timeout", f"{llm.timeout}s")
            table.add_row("API Key", "***configured***" if llm.api_key_encrypted else "❌ Not set")
            
            console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error showing config: {e}", style="red")


@config.command('models')
@click.option('--provider', help='Show models for specific provider')
@click.option('--available', is_flag=True, help='Show available models from API (requires API key)')
def list_models(provider: Optional[str], available: bool):
    """List supported models for providers."""
    try:
        from ..providers.base import ProviderRegistry
        from ..config.loader import ConfigLoader
        from ..utils.crypto import CryptoManager
        
        if provider:
            # Show models for specific provider
            if provider not in ProviderRegistry.list_providers():
                console.print(f"❌ Unknown provider: {provider}", style="red")
                console.print(f"Available providers: {', '.join(ProviderRegistry.list_providers())}")
                return
            
            supported_models = ProviderRegistry.get_supported_models(provider)
            
            console.print(f"\n[bold cyan]🤖 {provider.upper()} Models[/bold cyan]")
            console.print("=" * 50)
            
            if available:
                # Show available models from API
                console.print("📡 Fetching available models from API...")
                
                try:
                    # Load configuration
                    loader = ConfigLoader()
                    app_config = loader.load_app_config()
                    crypto_manager = CryptoManager()
                    
                    # Check if we have an API key
                    if not app_config.llm.api_key_encrypted:
                        console.print("⚠️  No API key configured. Use 'chatbot config api-key' first.", style="yellow")
                        return
                    
                    # Decrypt API key
                    api_key = crypto_manager.decrypt(app_config.llm.api_key_encrypted)
                    
                    # Create provider instance with full configuration
                    provider_kwargs = {
                        'base_url': app_config.llm.base_url,
                        'timeout': app_config.llm.timeout,
                    }
                    
                    # Add provider-specific configurations
                    if provider == 'openai':
                        if app_config.llm.organization:
                            provider_kwargs['organization'] = app_config.llm.organization
                    
                    provider_instance = ProviderRegistry.create_provider(
                        provider, 
                        api_key=api_key, 
                        model=supported_models[0] if supported_models else 'default',
                        **provider_kwargs
                    )
                    
                    # Get available models
                    available_models = asyncio.run(provider_instance.list_available_models())
                    
                    console.print(f"\n[bold green]✅ Available models from {provider} API:[/bold green]")
                    for model in available_models:
                        status = "[green]✓[/green]" if model in supported_models else "[dim]○[/dim]"
                        console.print(f"  {status} {model}")
                    
                    console.print(f"\n[dim]Legend: [green]✓[/green] = Supported by chatbot, [dim]○[/dim] = Available but not configured[/dim]")
                    
                except Exception as e:
                    console.print(f"❌ Failed to fetch available models: {e}", style="red")
                    console.print("\n[bold blue]📋 Supported models (configured in chatbot):[/bold blue]")
                    for model in supported_models:
                        console.print(f"  [green]✓[/green] {model}")
            else:
                # Show only supported models
                console.print("[bold blue]📋 Supported models:[/bold blue]")
                for model in supported_models:
                    console.print(f"  [green]✓[/green] {model}")
                
                console.print(f"\n[dim]💡 Use --available to see models from {provider} API[/dim]")
        else:
            # Show models for all providers
            all_models = ProviderRegistry.get_all_supported_models()
            
            console.print("\n[bold cyan]🤖 All Provider Models[/bold cyan]")
            console.print("=" * 50)
            
            for provider_name, models in all_models.items():
                console.print(f"\n[bold]{provider_name.upper()}:[/bold]")
                for model in models:
                    console.print(f"  [green]✓[/green] {model}")
            
            console.print("\n[dim]💡 Use --provider <name> for provider-specific details[/dim]")
            console.print("[dim]💡 Use --available to check API availability[/dim]")
    
    except Exception as e:
        console.print(f"❌ Error listing models: {e}", style="red")


@config.command('api-key')
@click.option('--provider', help='Specify provider (openai, claude)')
def set_api_key(provider: Optional[str]):
    """Set or update API key for LLM provider."""
    try:
        from ..utils.crypto import CryptoManager
        
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        
        # Determine provider
        if provider:
            if provider not in ['openai', 'claude']:
                console.print(f"❌ Invalid provider: {provider}", style="red")
                console.print("Valid providers: openai, claude", style="yellow")
                return
            app_config.llm.provider = provider
        
        current_provider = app_config.llm.provider
        
        console.print(f"\n🔑 Setting API key for {current_provider}", style="cyan")
        
        # Show where to get API key
        if current_provider == 'openai':
            console.print("Get your API key from: https://platform.openai.com/api-keys", style="blue")
        elif current_provider == 'claude':
            console.print("Get your API key from: https://console.anthropic.com/", style="blue")
        
        # Prompt for API key
        api_key = Prompt.ask("\nEnter your API key", password=True, console=console)
        
        if not api_key or not api_key.strip():
            console.print("❌ API key cannot be empty", style="red")
            return
        
        api_key = api_key.strip()
        
        # Validate format
        if current_provider == 'openai' and not api_key.startswith('sk-'):
            if not Confirm.ask("⚠️  OpenAI API keys typically start with 'sk-'. Continue anyway?"):
                return
        elif current_provider == 'claude' and not api_key.startswith('sk-ant-'):
            if not Confirm.ask("⚠️  Claude API keys typically start with 'sk-ant-'. Continue anyway?"):
                return
        
        # Encrypt and save
        crypto_manager = CryptoManager()
        encrypted_key = crypto_manager.encrypt(api_key)
        app_config.llm.api_key_encrypted = encrypted_key
        
        config_loader.save_app_config(app_config)
        
        console.print("✅ API key updated and encrypted successfully!", style="green")
        
    except Exception as e:
        console.print(f"❌ Error setting API key: {e}", style="red")


@config.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """Set a configuration value."""
    try:
        # Parse key to determine target
        parts = key.split('.')
        
        if parts[0] == 'global':
            global_memory = GlobalMemory()
            
            valid_prefs = {
                'communication_style': ['simple', 'detailed', 'balanced'],
                'technical_depth': ['beginner', 'intermediate', 'expert'],  
                'code_examples': ['always', 'on_demand', 'rarely'],
                'language_preference': None,  # Any string
                'response_length': ['short', 'medium', 'long']
            }
            
            if len(parts) != 2 or parts[1] not in valid_prefs:
                console.print(f"❌ Invalid global setting: {key}", style="red")
                console.print(f"Valid settings: {', '.join(valid_prefs.keys())}", style="yellow")
                return
            
            setting = parts[1]
            valid_values = valid_prefs[setting]
            
            if valid_values and value not in valid_values:
                console.print(f"❌ Invalid value '{value}' for {setting}", style="red")
                console.print(f"Valid values: {', '.join(valid_values)}", style="yellow")
                return
            
            global_memory.update_preferences(**{setting: value})
            console.print(f"✅ Updated {setting} = {value}", style="green")
            
        elif parts[0] == 'llm':
            config_loader = ConfigLoader()
            app_config = config_loader.load_app_config()
            
            if len(parts) != 2:
                console.print(f"❌ Invalid LLM setting: {key}", style="red")
                return
            
            setting = parts[1]
            
            # Handle API key specially (requires encryption)
            if setting == 'api_key':
                from ..utils.crypto import CryptoManager
                crypto_manager = CryptoManager()
                
                # Validate API key format
                provider = app_config.llm.provider
                if provider == 'openai' and not value.startswith('sk-'):
                    console.print("⚠️  OpenAI API keys typically start with 'sk-'", style="yellow")
                elif provider == 'claude' and not value.startswith('sk-ant-'):
                    console.print("⚠️  Claude API keys typically start with 'sk-ant-'", style="yellow")
                
                try:
                    encrypted_key = crypto_manager.encrypt(value)
                    app_config.llm.api_key_encrypted = encrypted_key
                    config_loader.save_app_config(app_config)
                    console.print("✅ API key updated and encrypted successfully", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to encrypt API key: {e}", style="red")
                return
            
            # Validate LLM settings and convert types
            valid_llm_settings = {
                'provider': {'type': str, 'values': ['openai', 'claude']},
                'model': {'type': str, 'values': None},
                'temperature': {'type': float, 'values': None},
                'max_tokens': {'type': int, 'values': None},
                'base_url': {'type': str, 'values': None},
                'organization': {'type': str, 'values': None},
                'timeout': {'type': float, 'values': None}
            }
            
            if setting not in valid_llm_settings:
                console.print(f"❌ Unknown LLM setting: {setting}", style="red")
                console.print(f"Valid settings: {', '.join(valid_llm_settings.keys())}", style="yellow")
                return
            
            setting_info = valid_llm_settings[setting]
            
            # Special validation for model setting
            if setting == 'model':
                # Validate model is supported by current provider
                from ..providers.base import ProviderRegistry
                from ..utils.crypto import CryptoManager
                
                current_provider = app_config.llm.provider
                if current_provider:
                    supported_models = ProviderRegistry.get_supported_models(current_provider)
                    
                    # If model is not in static supported list, check API available models
                    if value not in supported_models:
                        console.print(f"⚠️  Model '{value}' not found in predefined list. Checking API...", style="yellow")
                        
                        try:
                            # Check if we have API key to validate against API
                            if app_config.llm.api_key_encrypted:
                                crypto_manager = CryptoManager()
                                api_key = crypto_manager.decrypt(app_config.llm.api_key_encrypted)
                                
                                # Create provider instance to check available models
                                provider_kwargs = {
                                    'base_url': app_config.llm.base_url,
                                    'timeout': app_config.llm.timeout,
                                }
                                
                                if current_provider == 'openai' and app_config.llm.organization:
                                    provider_kwargs['organization'] = app_config.llm.organization
                                
                                # Use a dummy model first, we'll validate the real one via API
                                temp_model = supported_models[0] if supported_models else 'gpt-3.5-turbo'
                                provider_instance = ProviderRegistry.create_provider(
                                    current_provider, 
                                    api_key=api_key, 
                                    model=temp_model,
                                    **provider_kwargs
                                )
                                
                                # Get available models from API
                                available_models = asyncio.run(provider_instance.list_available_models())
                                
                                if value in available_models:
                                    console.print(f"✅ Model '{value}' found in {current_provider} API", style="green")
                                else:
                                    console.print(f"❌ Model '{value}' is not available from {current_provider} API", style="red")
                                    console.print(f"[dim]Available models from API:[/dim]")
                                    for model in available_models[:5]:  # Show first 5
                                        console.print(f"  [green]✓[/green] {model}")
                                    if len(available_models) > 5:
                                        console.print(f"  [dim]... and {len(available_models)-5} more[/dim]")
                                    console.print(f"\n[dim]💡 Use 'chatbot config models --provider {current_provider} --available' for full list[/dim]")
                                    return
                            else:
                                console.print(f"❌ Model '{value}' is not in predefined list and no API key configured to validate", style="red")
                                console.print(f"[dim]Predefined models for {current_provider}:[/dim]")
                                for model in supported_models[:5]:  # Show first 5
                                    console.print(f"  [green]✓[/green] {model}")
                                if len(supported_models) > 5:
                                    console.print(f"  [dim]... and {len(supported_models)-5} more[/dim]")
                                console.print(f"\n[dim]💡 Configure API key first, then use 'chatbot config models --provider {current_provider} --available' to see all available models[/dim]")
                                return
                        except Exception as e:
                            console.print(f"⚠️  Could not validate model via API: {e}", style="yellow")
                            console.print(f"❌ Model '{value}' is not in predefined list for {current_provider} provider", style="red")
                            console.print(f"[dim]Predefined models for {current_provider}:[/dim]")
                            for model in supported_models[:5]:  # Show first 5
                                console.print(f"  [green]✓[/green] {model}")
                            if len(supported_models) > 5:
                                console.print(f"  [dim]... and {len(supported_models)-5} more[/dim]")
                            console.print(f"\n[dim]💡 Use 'chatbot config models --provider {current_provider}' for full list[/dim]")
                            return
                else:
                    console.print("⚠️  No provider configured. Set provider first.", style="yellow")
                    return
            
            # Special validation for provider setting
            elif setting == 'provider':
                # Validate if model is still supported after provider change
                current_model = app_config.llm.model
                if current_model:
                    from ..providers.base import ProviderRegistry
                    
                    try:
                        new_supported_models = ProviderRegistry.get_supported_models(value)
                        if current_model not in new_supported_models:
                            console.print(f"⚠️  Current model '{current_model}' is not supported by {value} provider", style="yellow")
                            console.print(f"[dim]You may need to update the model after changing provider.[/dim]")
                            console.print(f"[dim]Use 'chatbot config models --provider {value}' to see supported models[/dim]")
                    except:
                        pass  # Continue with provider change
            
            # Validate values if constrained
            if setting_info['values'] and value not in setting_info['values']:
                console.print(f"❌ Invalid value '{value}' for {setting}", style="red")
                console.print(f"Valid values: {', '.join(setting_info['values'])}", style="yellow")
                return
            
            # Convert type
            try:
                if setting_info['type'] == float:
                    converted_value = float(value)
                elif setting_info['type'] == int:
                    converted_value = int(value)
                else:
                    converted_value = value if value.lower() != 'none' else None
            except ValueError:
                console.print(f"❌ Invalid {setting_info['type'].__name__} value: {value}", style="red")
                return
            
            # Set the value
            setattr(app_config.llm, setting, converted_value)
            config_loader.save_app_config(app_config)
            console.print(f"✅ Updated LLM {setting} = {converted_value}", style="green")
        
        else:
            console.print(f"❌ Unknown config section: {parts[0]}", style="red")
            console.print("Valid sections: global, llm", style="yellow")
            
    except Exception as e:
        console.print(f"❌ Error setting config: {e}", style="red")


if __name__ == '__main__':
    cli()