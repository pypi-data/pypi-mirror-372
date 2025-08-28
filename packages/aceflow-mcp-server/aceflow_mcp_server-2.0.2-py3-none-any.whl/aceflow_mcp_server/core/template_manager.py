"""Template Manager for AceFlow templates."""

from typing import Dict, Any, List
from pathlib import Path
import json


class TemplateManager:
    """Manages AceFlow templates."""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.available_templates = ["minimal", "standard", "complete", "smart"]
    
    def list_templates(self) -> Dict[str, Any]:
        """List available templates."""
        return {
            "available": self.available_templates,
            "current": self.get_current_template()
        }
    
    def get_current_template(self) -> str:
        """Get current template."""
        # Check project state for current template
        state_file = self.current_dir / ".aceflow" / "current_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return state.get("project", {}).get("mode", "unknown").lower()
            except:
                pass
        return "unknown"
    
    def apply_template(self, template: str) -> Dict[str, Any]:
        """Apply a template."""
        if template not in self.available_templates:
            raise ValueError(f"Template '{template}' not available")
        
        # Mock implementation
        return {
            "template": template,
            "applied": True,
            "message": f"Template '{template}' applied successfully"
        }
    
    def validate_current_template(self) -> Dict[str, Any]:
        """Validate current template."""
        current = self.get_current_template()
        is_valid = current in self.available_templates
        
        return {
            "template": current,
            "valid": is_valid,
            "message": "Template is valid" if is_valid else f"Template '{current}' is not recognized"
        }