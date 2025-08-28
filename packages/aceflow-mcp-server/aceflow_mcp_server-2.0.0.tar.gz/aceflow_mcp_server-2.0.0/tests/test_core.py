"""Test suite for AceFlow Core modules."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from aceflow_mcp_server.core import ProjectManager, WorkflowEngine, TemplateManager


class TestProjectManager:
    """Test ProjectManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.manager = ProjectManager()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_initialize_project(self):
        """Test project initialization."""
        result = self.manager.initialize_project("standard", "test-project")
        
        assert result["success"] is True
        assert result["project_name"] == "test-project"
        assert result["mode"] == "standard"
    
    def test_get_current_state_no_project(self):
        """Test getting state when no project exists."""
        state = self.manager.get_current_state()
        assert state == {}
    
    def test_get_current_state_with_project(self):
        """Test getting state with existing project."""
        # Create mock state file
        aceflow_dir = Path(".aceflow")
        aceflow_dir.mkdir()
        
        state_data = {
            "project": {"name": "test", "mode": "STANDARD"},
            "flow": {"current_stage": "user_stories"}
        }
        
        with open(aceflow_dir / "current_state.json", 'w') as f:
            json.dump(state_data, f)
        
        state = self.manager.get_current_state()
        assert state["project"]["name"] == "test"
        assert state["project"]["mode"] == "STANDARD"
    
    def test_get_workflow_config(self):
        """Test getting workflow config."""
        config = self.manager.get_workflow_config()
        assert config["exists"] is False
        
        # Create config file
        aceflow_dir = Path(".aceflow")
        aceflow_dir.mkdir()
        (aceflow_dir / "template.yaml").touch()
        
        config = self.manager.get_workflow_config()
        assert config["exists"] is True
    
    def test_get_stage_guide(self):
        """Test getting stage guide."""
        guide = self.manager.get_stage_guide("implementation")
        assert "implementation" in guide
    
    def test_get_validator(self):
        """Test getting validator."""
        validator = self.manager.get_validator()
        assert validator is not None
        
        result = validator.validate()
        assert result["status"] == "passed"
    
    def test_get_template_manager(self):
        """Test getting template manager."""
        template_manager = self.manager.get_template_manager()
        assert template_manager is not None
        
        templates = template_manager.list_templates()
        assert "minimal" in templates


class TestWorkflowEngine:
    """Test WorkflowEngine functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.engine = WorkflowEngine()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_get_current_status(self):
        """Test getting current status."""
        status = self.engine.get_current_status()
        
        assert "current_stage" in status
        assert "progress" in status
        assert "completed_stages" in status
        assert "next_stage" in status
    
    def test_advance_to_next_stage(self):
        """Test advancing to next stage."""
        result = self.engine.advance_to_next_stage()
        
        assert "previous_stage" in result
        assert "current_stage" in result
        assert "progress" in result
    
    def test_list_all_stages(self):
        """Test listing all stages."""
        stages = self.engine.list_all_stages()
        
        assert isinstance(stages, list)
        assert len(stages) > 0
        assert "user_stories" in stages
        assert "implementation" in stages
        assert "demo" in stages
    
    def test_reset_project(self):
        """Test resetting project."""
        result = self.engine.reset_project()
        
        assert result["current_stage"] == "user_stories"
        assert result["progress"] == 0
        assert result["completed_stages"] == []


class TestTemplateManager:
    """Test TemplateManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.manager = TemplateManager()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_list_templates(self):
        """Test listing templates."""
        result = self.manager.list_templates()
        
        assert "available" in result
        assert "current" in result
        assert isinstance(result["available"], list)
        assert "minimal" in result["available"]
        assert "standard" in result["available"]
        assert "complete" in result["available"]
        assert "smart" in result["available"]
    
    def test_get_current_template_no_project(self):
        """Test getting current template when no project exists."""
        current = self.manager.get_current_template()
        assert current == "unknown"
    
    def test_get_current_template_with_project(self):
        """Test getting current template with existing project."""
        # Create mock state file
        aceflow_dir = Path(".aceflow")
        aceflow_dir.mkdir()
        
        state_data = {
            "project": {"mode": "STANDARD"}
        }
        
        with open(aceflow_dir / "current_state.json", 'w') as f:
            json.dump(state_data, f)
        
        current = self.manager.get_current_template()
        assert current == "standard"
    
    def test_apply_template_valid(self):
        """Test applying valid template."""
        result = self.manager.apply_template("minimal")
        
        assert result["template"] == "minimal"
        assert result["applied"] is True
        assert "successfully" in result["message"]
    
    def test_apply_template_invalid(self):
        """Test applying invalid template."""
        with pytest.raises(ValueError) as exc_info:
            self.manager.apply_template("invalid")
        
        assert "not available" in str(exc_info.value)
    
    def test_validate_current_template_valid(self):
        """Test validating valid template."""
        # Create mock state file with valid template
        aceflow_dir = Path(".aceflow")
        aceflow_dir.mkdir()
        
        state_data = {
            "project": {"mode": "COMPLETE"}
        }
        
        with open(aceflow_dir / "current_state.json", 'w') as f:
            json.dump(state_data, f)
        
        result = self.manager.validate_current_template()
        
        assert result["template"] == "complete"
        assert result["valid"] is True
        assert "valid" in result["message"]
    
    def test_validate_current_template_invalid(self):
        """Test validating invalid template."""
        result = self.manager.validate_current_template()
        
        assert result["template"] == "unknown"
        assert result["valid"] is False
        assert "not recognized" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__])