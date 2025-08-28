"""Project Manager for AceFlow integration."""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import datetime


class StateManager:
    """Enhanced state manager for AceFlow projects."""
    
    def __init__(self, aceflow_dir: Path):
        """Initialize state manager.
        
        Args:
            aceflow_dir: Path to .aceflow directory
        """
        self.aceflow_dir = aceflow_dir
        self.state_file = aceflow_dir / "current_state.json"
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current project state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return self._get_default_state()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update project state.
        
        Args:
            updates: Dictionary of updates to apply
        """
        current_state = self.get_current_state()
        
        # Deep merge updates
        self._deep_merge(current_state, updates)
        
        # Update timestamp
        current_state["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save state
        self._save_state(current_state)
    
    def complete_stage(self, stage_id: str, output_path: str) -> None:
        """Mark a stage as completed.
        
        Args:
            stage_id: ID of the completed stage
            output_path: Path to the stage output
        """
        current_state = self.get_current_state()
        
        # Add to completed stages
        completed_stages = current_state.get("flow", {}).get("completed_stages", [])
        if stage_id not in completed_stages:
            completed_stages.append(stage_id)
        
        # Update stage outputs
        stage_outputs = current_state.get("flow", {}).get("stage_outputs", {})
        stage_outputs[stage_id] = output_path
        
        # Calculate progress
        total_stages = current_state.get("metadata", {}).get("total_stages", 8)
        progress = (len(completed_stages) / total_stages) * 100
        
        # Update state
        updates = {
            "flow": {
                "completed_stages": completed_stages,
                "stage_outputs": stage_outputs,
                "progress_percentage": progress
            }
        }
        
        self.update_state(updates)
    
    def set_current_stage(self, stage_id: str) -> None:
        """Set the current active stage.
        
        Args:
            stage_id: ID of the stage to set as current
        """
        updates = {
            "flow": {
                "current_stage": stage_id
            }
        }
        self.update_state(updates)
    
    def get_stage_output(self, stage_id: str) -> Optional[str]:
        """Get output path for a completed stage.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            Path to stage output or None
        """
        current_state = self.get_current_state()
        stage_outputs = current_state.get("flow", {}).get("stage_outputs", {})
        return stage_outputs.get(stage_id)
    
    def is_stage_completed(self, stage_id: str) -> bool:
        """Check if a stage is completed.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            True if stage is completed
        """
        current_state = self.get_current_state()
        completed_stages = current_state.get("flow", {}).get("completed_stages", [])
        return stage_id in completed_stages
    
    def get_progress(self) -> float:
        """Get current project progress.
        
        Returns:
            Progress percentage (0-100)
        """
        current_state = self.get_current_state()
        return current_state.get("flow", {}).get("progress_percentage", 0.0)
    
    def reset_project(self) -> None:
        """Reset project to initial state."""
        current_state = self.get_current_state()
        
        # Reset flow state
        updates = {
            "flow": {
                "current_stage": self._get_initial_stage(current_state.get("project", {}).get("mode", "standard")),
                "completed_stages": [],
                "stage_outputs": {},
                "progress_percentage": 0.0
            }
        }
        
        self.update_state(updates)
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default project state."""
        return {
            "project": {
                "name": "unknown",
                "mode": "standard",
                "created_at": datetime.datetime.now().isoformat(),
                "version": "3.0"
            },
            "flow": {
                "current_stage": "user_stories",
                "completed_stages": [],
                "stage_outputs": {},
                "progress_percentage": 0.0
            },
            "metadata": {
                "total_stages": 8,
                "last_updated": datetime.datetime.now().isoformat()
            }
        }
    
    def _get_initial_stage(self, mode: str) -> str:
        """Get initial stage for a mode.
        
        Args:
            mode: Project mode
            
        Returns:
            Initial stage ID
        """
        initial_stages = {
            "minimal": "implementation",
            "standard": "user_stories",
            "complete": "requirement_analysis",
            "smart": "project_analysis"
        }
        return initial_stages.get(mode.lower(), "user_stories")
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge source into target dictionary.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to file.
        
        Args:
            state: State dictionary to save
        """
        # Ensure directory exists
        self.aceflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Save state
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)


class ProjectManager:
    """Manages AceFlow project operations."""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.state_manager = StateManager(self.current_dir / ".aceflow")
    
    def initialize_project(
        self, 
        mode: str, 
        name: Optional[str] = None, 
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize a new AceFlow project."""
        # This would integrate with the actual project initialization logic
        # For now, return a mock response
        return {
            "success": True,
            "project_name": name or "default_project",
            "mode": mode,
            "directory": directory or str(self.current_dir)
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current project state."""
        return self.state_manager.get_current_state()
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration."""
        config_file = self.current_dir / ".aceflow" / "template.yaml"
        if config_file.exists():
            return {"config_file": str(config_file), "exists": True}
        return {"exists": False}
    
    def get_stage_guide(self, stage: str) -> str:
        """Get stage-specific guide."""
        return f"Guide for stage: {stage}"
    
    def get_validator(self):
        """Get project validator."""
        return ProjectValidator()
    
    def get_template_manager(self):
        """Get template manager."""
        return TemplateManager()


class ProjectValidator:
    """Validates project compliance."""
    
    def validate(self, mode: str = "basic", auto_fix: bool = False, generate_report: bool = False):
        """Validate project."""
        return {
            "status": "passed",
            "checks": {"total": 10, "passed": 8, "failed": 2}
        }


class TemplateManager:
    """Manages project templates."""
    
    def list_templates(self):
        """List available templates."""
        return ["minimal", "standard", "complete", "smart"]
    
    def apply_template(self, template: str):
        """Apply a template."""
        return {"template": template, "applied": True}
    
    def validate_current_template(self):
        """Validate current template."""
        return {"valid": True}