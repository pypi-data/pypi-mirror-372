"""Workspace memory management for project-specific knowledge."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..config.settings import (
    WorkspaceConfig, WorkspaceInfo, ProjectProfile,
    ArchitectureDecision, BestPractice, CommonPattern, DevelopmentNote
)
from ..config.loader import ConfigLoader, ConfigurationError


class WorkspaceMemoryError(Exception):
    """Workspace memory related errors."""
    pass


class WorkspaceMemory:
    """Manages project-specific knowledge and workspace configuration."""
    
    def __init__(self, workspace_path: Optional[Path] = None, config_loader: Optional[ConfigLoader] = None):
        self.workspace_path = workspace_path or Path.cwd() / "workspace"
        self.config_loader = config_loader or ConfigLoader()
        self._config: Optional[WorkspaceConfig] = None
        self._workspace_name: Optional[str] = None
    
    def create_workspace(self, name: str, description: str = "", profile_data: Optional[Dict[str, Any]] = None) -> None:
        """Create a new workspace."""
        workspace_path = Path.cwd() / name / "workspace"
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        
        # Extract profile data
        if profile_data is None:
            profile_data = {}
        
        config = WorkspaceConfig(
            workspace_info=WorkspaceInfo(
                name=name,
                description=description or f"Workspace for {name} project",
                created_at=now,
                last_updated=now
            ),
            project_profile=ProjectProfile(
                domain_type=profile_data.get('domain_type', 'general'),
                tech_stack=profile_data.get('tech_stack', {}),
                team_size=profile_data.get('team_size', 1),
                project_stage=profile_data.get('project_stage', 'development'),
                research_area=profile_data.get('research_area', ''),
                creative_medium=profile_data.get('creative_medium', ''),
                business_sector=profile_data.get('business_sector', ''),
                personal_goal=profile_data.get('personal_goal', '')
            )
        )
        
        try:
            self.config_loader.save_workspace_config(config, workspace_path)
        except ConfigurationError as e:
            raise WorkspaceMemoryError(f"Failed to create workspace: {e}")
    
    def load_workspace(self, workspace_path: Optional[Path] = None) -> WorkspaceConfig:
        """Load workspace configuration from specified path."""
        if workspace_path:
            self.workspace_path = workspace_path
        
        try:
            self._config = self.config_loader.load_workspace_config(self.workspace_path)
            if self._config.workspace_info:
                self._workspace_name = self._config.workspace_info.name
            return self._config
        except ConfigurationError as e:
            raise WorkspaceMemoryError(f"Failed to load workspace: {e}")
    
    def save_workspace(self) -> None:
        """Save current workspace configuration."""
        if self._config is None:
            raise WorkspaceMemoryError("No workspace configuration loaded to save")
        
        try:
            if self._config.workspace_info:
                self._config.workspace_info.last_updated = datetime.now()
            self.config_loader.save_workspace_config(self._config, self.workspace_path)
        except ConfigurationError as e:
            raise WorkspaceMemoryError(f"Failed to save workspace: {e}")
    
    @property
    def config(self) -> WorkspaceConfig:
        """Get current workspace configuration, loading if necessary."""
        if self._config is None:
            self.load_workspace()
        return self._config
    
    @property
    def name(self) -> str:
        """Get workspace name."""
        if self._workspace_name is None and self.config.workspace_info:
            self._workspace_name = self.config.workspace_info.name
        return self._workspace_name or "unknown"
    
    def update_project_profile(self, tech_stack: Optional[Dict[str, List[str]]] = None,
                             team_size: Optional[int] = None, 
                             project_stage: Optional[str] = None) -> None:
        """Update project profile information."""
        profile = self.config.project_profile
        
        if tech_stack is not None:
            profile.tech_stack = tech_stack
        if team_size is not None:
            profile.team_size = team_size
        if project_stage is not None:
            valid_stages = ["planning", "development", "production"]
            if project_stage not in valid_stages:
                raise WorkspaceMemoryError(f"Invalid project stage: {project_stage}")
            profile.project_stage = project_stage
        
        self.save_workspace()
    
    def add_architecture_decision(self, title: str, decision: str, rationale: str) -> None:
        """Add an architecture decision record."""
        ad = ArchitectureDecision(
            title=title,
            decision=decision,
            rationale=rationale,
            date=datetime.now()
        )
        
        self.config.project_knowledge.architecture_decisions.append(ad)
        self.save_workspace()
    
    def add_best_practice(self, category: str, practice: str, reason: str, 
                         examples: Optional[List[str]] = None) -> None:
        """Add a best practice record."""
        bp = BestPractice(
            category=category,
            practice=practice,
            reason=reason,
            examples=examples or []
        )
        
        self.config.project_knowledge.best_practices.append(bp)
        self.save_workspace()
    
    def add_common_pattern(self, pattern: str, implementation: str) -> None:
        """Add or update a common pattern usage."""
        patterns = self.config.project_knowledge.common_patterns
        
        # Check if pattern already exists
        for existing_pattern in patterns:
            if existing_pattern.pattern == pattern:
                existing_pattern.usage_count += 1
                existing_pattern.last_used = datetime.now()
                existing_pattern.implementation = implementation  # Update implementation
                self.save_workspace()
                return
        
        # Add new pattern
        cp = CommonPattern(
            pattern=pattern,
            implementation=implementation,
            usage_count=1,
            last_used=datetime.now()
        )
        patterns.append(cp)
        self.save_workspace()
    
    def add_development_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> None:
        """Add a development note."""
        note = DevelopmentNote(
            title=title,
            content=content,
            tags=tags or [],
            created_at=datetime.now()
        )
        
        self.config.development_notes.append(note)
        self.save_workspace()
    
    def search_notes(self, query: str, tags: Optional[List[str]] = None) -> List[DevelopmentNote]:
        """Search development notes by content or tags."""
        results = []
        query_lower = query.lower()
        
        for note in self.config.development_notes:
            # Check content
            if query_lower in note.title.lower() or query_lower in note.content.lower():
                if tags is None or any(tag in note.tags for tag in tags):
                    results.append(note)
            # Check tags
            elif tags and any(tag in note.tags for tag in tags):
                results.append(note)
        
        # Sort by creation date, newest first
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results
    
    def get_relevant_patterns(self, keywords: List[str]) -> List[CommonPattern]:
        """Get common patterns relevant to keywords."""
        relevant = []
        
        for pattern in self.config.project_knowledge.common_patterns:
            pattern_text = f"{pattern.pattern} {pattern.implementation}".lower()
            if any(keyword.lower() in pattern_text for keyword in keywords):
                relevant.append(pattern)
        
        # Sort by usage count and recency
        relevant.sort(key=lambda x: (x.usage_count, x.last_used or datetime.min), reverse=True)
        return relevant
    
    def get_context_for_prompt(self, keywords: Optional[List[str]] = None, 
                              include_history: bool = True) -> Dict[str, Any]:
        """Get relevant workspace context for prompt injection."""
        context = {
            "workspace": {
                "name": self.name,
                "tech_stack": self.config.project_profile.tech_stack,
                "project_stage": self.config.project_profile.project_stage
            }
        }
        
        # Add relevant architecture decisions (latest 3)
        if self.config.project_knowledge.architecture_decisions:
            context["recent_decisions"] = [
                {
                    "title": ad.title,
                    "decision": ad.decision,
                    "rationale": ad.rationale
                }
                for ad in sorted(
                    self.config.project_knowledge.architecture_decisions,
                    key=lambda x: x.date, reverse=True
                )[:3]
            ]
        
        # Add relevant best practices
        if keywords:
            relevant_practices = []
            for bp in self.config.project_knowledge.best_practices:
                if any(keyword.lower() in bp.category.lower() or 
                      keyword.lower() in bp.practice.lower() for keyword in keywords):
                    relevant_practices.append({
                        "category": bp.category,
                        "practice": bp.practice,
                        "reason": bp.reason
                    })
            if relevant_practices:
                context["relevant_practices"] = relevant_practices[:5]  # Top 5
            
            # Add relevant patterns
            relevant_patterns = self.get_relevant_patterns(keywords)
            if relevant_patterns:
                context["common_patterns"] = [
                    {
                        "pattern": cp.pattern,
                        "implementation": cp.implementation,
                        "usage_count": cp.usage_count
                    }
                    for cp in relevant_patterns[:3]  # Top 3
                ]
        
        return context
    
    def export_workspace(self, export_path: Path) -> None:
        """Export workspace configuration to specified path."""
        try:
            self.config_loader.save_workspace_config(self.config, export_path.parent)
            # The config will be saved as config.yaml in the export_path parent directory
        except Exception as e:
            raise WorkspaceMemoryError(f"Failed to export workspace: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get workspace memory statistics."""
        return {
            "name": self.name,
            "tech_stack_categories": len(self.config.project_profile.tech_stack),
            "architecture_decisions": len(self.config.project_knowledge.architecture_decisions),
            "best_practices": len(self.config.project_knowledge.best_practices),
            "common_patterns": len(self.config.project_knowledge.common_patterns),
            "development_notes": len(self.config.development_notes),
            "last_updated": (self.config.workspace_info.last_updated.isoformat() 
                           if self.config.workspace_info else None)
        }
    
    def clean_old_notes(self, days_threshold: int = 180) -> int:
        """Clean old development notes."""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_threshold)
        
        original_count = len(self.config.development_notes)
        self.config.development_notes = [
            note for note in self.config.development_notes
            if note.created_at >= cutoff_date
        ]
        
        removed_count = original_count - len(self.config.development_notes)
        if removed_count > 0:
            self.save_workspace()
        
        return removed_count
    
    @staticmethod
    def list_workspaces(base_dir: Path = Path.cwd()) -> List[str]:
        """List all available workspaces in the base directory."""
        workspaces = []
        
        for item in base_dir.iterdir():
            if item.is_dir():
                workspace_config = item / "workspace" / "config.yaml"
                if workspace_config.exists():
                    workspaces.append(item.name)
        
        return sorted(workspaces)
    
    @staticmethod
    def delete_workspace(name: str, base_dir: Path = Path.cwd()) -> None:
        """Delete a workspace directory."""
        workspace_dir = base_dir / name
        if not workspace_dir.exists():
            raise WorkspaceMemoryError(f"Workspace '{name}' does not exist")
        
        try:
            import shutil
            shutil.rmtree(workspace_dir)
        except Exception as e:
            raise WorkspaceMemoryError(f"Failed to delete workspace: {e}")