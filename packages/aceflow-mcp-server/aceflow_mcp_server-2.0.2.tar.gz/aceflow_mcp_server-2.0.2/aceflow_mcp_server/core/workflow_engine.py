"""Workflow Engine for AceFlow stage management."""

from typing import Dict, Any, List
from pathlib import Path
import json
import datetime


class WorkflowEngine:
    """Manages workflow stages and transitions."""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.state_file = self.current_dir / ".aceflow" / "current_state.json"
        
        # Standard mode stages
        self.standard_stages = [
            "S1_user_stories",
            "S2_task_breakdown", 
            "S3_test_design",
            "S4_implementation",
            "S5_unit_test",
            "S6_integration_test",
            "S7_code_review",
            "S8_demo"
        ]
    
    def _load_state(self) -> Dict[str, Any]:
        """Load current project state."""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_state(self, state: Dict[str, Any]) -> bool:
        """Save project state."""
        try:
            # Update last_updated timestamp
            state["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        state = self._load_state()
        if not state:
            return {
                "current_stage": "unknown",
                "progress": 0,
                "completed_stages": [],
                "next_stage": "unknown"
            }
        
        current_stage = state["flow"]["current_stage"]
        completed_stages = state["flow"]["completed_stages"]
        
        # Calculate progress
        total_stages = len(self.standard_stages)
        progress = (len(completed_stages) / total_stages) * 100
        
        # Find next stage
        try:
            current_index = self.standard_stages.index(current_stage)
            next_stage = self.standard_stages[current_index + 1] if current_index + 1 < len(self.standard_stages) else None
        except ValueError:
            next_stage = None
        
        # Convert stage names for display
        display_stage = current_stage.replace("S1_", "").replace("S2_", "").replace("S3_", "").replace("S4_", "").replace("S5_", "").replace("S6_", "").replace("S7_", "").replace("S8_", "")
        display_next = next_stage.replace("S1_", "").replace("S2_", "").replace("S3_", "").replace("S4_", "").replace("S5_", "").replace("S6_", "").replace("S7_", "").replace("S8_", "") if next_stage else None
        
        return {
            "current_stage": display_stage,
            "progress": round(progress, 1),
            "completed_stages": [s.split("_", 1)[1] if "_" in s else s for s in completed_stages],
            "next_stage": display_next
        }
    
    def advance_to_next_stage(self) -> Dict[str, Any]:
        """Advance to the next stage."""
        state = self._load_state()
        if not state:
            return {
                "success": False,
                "error": "No project state found"
            }
        
        current_stage = state["flow"]["current_stage"]
        completed_stages = state["flow"]["completed_stages"]
        
        try:
            current_index = self.standard_stages.index(current_stage)
            
            # Mark current stage as completed
            if current_stage not in completed_stages:
                completed_stages.append(current_stage)
            
            # Move to next stage
            if current_index + 1 < len(self.standard_stages):
                next_stage = self.standard_stages[current_index + 1]
                state["flow"]["current_stage"] = next_stage
                state["flow"]["completed_stages"] = completed_stages
                
                # Update progress
                progress = ((current_index + 1) / len(self.standard_stages)) * 100
                state["flow"]["progress_percentage"] = round(progress, 1)
                
                # Save state
                if self._save_state(state):
                    return {
                        "previous_stage": current_stage.split("_", 1)[1] if "_" in current_stage else current_stage,
                        "current_stage": next_stage.split("_", 1)[1] if "_" in next_stage else next_stage,
                        "progress": round(progress, 1)
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to save state"
                    }
            else:
                return {
                    "success": False,
                    "error": "Already at final stage"
                }
                
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown stage: {current_stage}"
            }
    
    def list_all_stages(self) -> List[str]:
        """List all available stages."""
        return [s.split("_", 1)[1] if "_" in s else s for s in self.standard_stages]
    
    def reset_project(self) -> Dict[str, Any]:
        """Reset project to initial stage."""
        state = self._load_state()
        if not state:
            return {
                "success": False,
                "error": "No project state found"
            }
        
        # Reset to initial stage
        state["flow"]["current_stage"] = self.standard_stages[0]
        state["flow"]["completed_stages"] = []
        state["flow"]["progress_percentage"] = 0
        
        if self._save_state(state):
            return {
                "current_stage": self.standard_stages[0].split("_", 1)[1],
                "progress": 0,
                "completed_stages": []
            }
        else:
            return {
                "success": False,
                "error": "Failed to save state"
            }