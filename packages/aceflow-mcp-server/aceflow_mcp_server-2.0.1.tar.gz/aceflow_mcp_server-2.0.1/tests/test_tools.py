"""Test suite for AceFlow MCP Tools."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from aceflow_mcp_server.tools import AceFlowTools


class TestAceFlowTools:
    """Test AceFlow MCP Tools functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.tools = AceFlowTools()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        # Note: temp_dir cleanup would be handled by tempfile
    
    def call_tool(self, tool_name, *args, **kwargs):
        """Helper method to call tools."""
        tool = getattr(self.tools, tool_name)
        return tool(*args, **kwargs)
    
    def test_aceflow_init_minimal_mode(self):
        """Test project initialization in minimal mode."""
        result = self.call_tool("aceflow_init",
            mode="minimal",
            project_name="test-project"
        )
        
        assert result["success"] is True
        assert "test-project" in result["message"]
        assert result["project_info"]["mode"] == "minimal"
        assert result["project_info"]["name"] == "test-project"
        
        # Check if files were created
        assert Path(".clinerules").exists()
        assert Path(".aceflow").exists()
        assert Path("aceflow_result").exists()
    
    def test_aceflow_init_invalid_mode(self):
        """Test project initialization with invalid mode."""
        result = self.call_tool("aceflow_init", mode="invalid")
        
        assert result["success"] is False
        assert "Invalid mode" in result["error"]
    
    def test_aceflow_init_all_modes(self):
        """Test project initialization with all valid modes."""
        modes = ["minimal", "standard", "complete", "smart"]
        
        for i, mode in enumerate(modes):
            # Create a new subdirectory for each mode
            mode_dir = Path(f"test-{mode}")
            mode_dir.mkdir(exist_ok=True)
            
            result = self.call_tool("aceflow_init",
                mode=mode,
                project_name=f"test-{mode}",
                directory=str(mode_dir)
            )
            
            assert result["success"] is True
            assert result["project_info"]["mode"] == mode
            
            # Check specific files exist
            assert (mode_dir / ".clinerules").exists()
            assert (mode_dir / ".aceflow" / "current_state.json").exists()
            assert (mode_dir / ".aceflow" / "template.yaml").exists()
    
    def test_aceflow_stage_status(self):
        """Test stage status functionality."""
        # First initialize a project
        self.call_tool("aceflow_init", mode="standard", project_name="test")
        
        result = self.call_tool("aceflow_stage", action="status")
        
        assert result["success"] is True
        assert "result" in result
        assert "current_stage" in result["result"]
    
    def test_aceflow_stage_list(self):
        """Test stage list functionality."""
        result = self.call_tool("aceflow_stage", action="list")
        
        assert result["success"] is True
        assert "stages" in result["result"]
        assert isinstance(result["result"]["stages"], list)
    
    def test_aceflow_validate_basic(self):
        """Test basic validation functionality."""
        result = self.call_tool("aceflow_validate", mode="basic")
        
        assert result["success"] is True
        assert "validation_result" in result
        assert "status" in result["validation_result"]
    
    def test_aceflow_template_list(self):
        """Test template listing functionality."""
        result = self.call_tool("aceflow_template", action="list")
        
        assert result["success"] is True
        assert "available_templates" in result["result"]
        assert isinstance(result["result"]["available_templates"], list)
    
    def test_project_state_file_creation(self):
        """Test that project state file is created correctly."""
        result = self.call_tool("aceflow_init",
            mode="standard",
            project_name="state-test"
        )
        
        assert result["success"] is True
        
        # Check state file content
        state_file = Path(".aceflow/current_state.json")
        assert state_file.exists()
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        assert state["project"]["name"] == "state-test"
        assert state["project"]["mode"] == "STANDARD"
        assert "created_at" in state["project"]
        assert state["flow"]["current_stage"] == "user_stories"
    
    def test_clinerules_file_content(self):
        """Test that .clinerules file contains correct content."""
        result = self.call_tool("aceflow_init",
            mode="complete",
            project_name="clinerules-test"
        )
        
        assert result["success"] is True
        
        clinerules_file = Path(".clinerules")
        assert clinerules_file.exists()
        
        with open(clinerules_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "clinerules-test" in content
        assert "complete" in content
        assert "AceFlow v3.0" in content
        assert "aceflow_result/" in content
    
    def test_directory_parameter(self):
        """Test project initialization with custom directory."""
        custom_dir = Path("custom-project-dir")
        
        result = self.call_tool("aceflow_init",
            mode="minimal",
            project_name="dir-test",
            directory=str(custom_dir)
        )
        
        assert result["success"] is True
        assert custom_dir.exists()
        assert (custom_dir / ".clinerules").exists()
        assert (custom_dir / ".aceflow").exists()
    
    def test_aceflow_stage_next(self):
        """Test stage next functionality."""
        # First initialize a project
        self.call_tool("aceflow_init", mode="standard", project_name="test")
        
        result = self.call_tool("aceflow_stage", action="next")
        
        assert result["success"] is True
        assert "result" in result
        assert "previous_stage" in result["result"]
        assert "current_stage" in result["result"]
    
    def test_aceflow_stage_reset(self):
        """Test stage reset functionality."""
        result = self.call_tool("aceflow_stage", action="reset")
        
        assert result["success"] is True
        assert result["result"]["current_stage"] == "user_stories"
        assert result["result"]["progress"] == 0
    
    def test_aceflow_stage_invalid_action(self):
        """Test stage with invalid action."""
        result = self.call_tool("aceflow_stage", action="invalid")
        
        assert result["success"] is False
        assert "Invalid action" in result["error"]
    
    def test_aceflow_validate_complete_mode(self):
        """Test validation in complete mode."""
        result = self.call_tool("aceflow_validate", mode="complete", fix=True, report=True)
        
        assert result["success"] is True
        assert result["validation_result"]["mode"] == "complete"
        assert result["validation_result"]["auto_fix_enabled"] is True
        assert result["validation_result"]["report_generated"] is True
    
    def test_aceflow_template_apply(self):
        """Test template apply functionality."""
        result = self.call_tool("aceflow_template", action="apply", template="minimal")
        
        assert result["success"] is True
        assert result["result"]["template"] == "minimal"
        assert result["result"]["applied"] is True
    
    def test_aceflow_template_apply_no_template(self):
        """Test template apply without template name."""
        result = self.call_tool("aceflow_template", action="apply")
        
        assert result["success"] is False
        assert "required" in result["error"]
    
    def test_aceflow_template_validate(self):
        """Test template validate functionality."""
        result = self.call_tool("aceflow_template", action="validate")
        
        assert result["success"] is True
        assert "template" in result["result"]
        assert "valid" in result["result"]
    
    def test_aceflow_template_invalid_action(self):
        """Test template with invalid action."""
        result = self.call_tool("aceflow_template", action="invalid")
        
        assert result["success"] is False
        assert "Invalid action" in result["error"]
    
    def test_aceflow_init_existing_project(self):
        """Test initializing project in directory with existing project."""
        # First initialize a project
        self.call_tool("aceflow_init", mode="minimal", project_name="first")
        
        # Try to initialize again
        result = self.call_tool("aceflow_init", mode="standard", project_name="second")
        
        assert result["success"] is False
        assert "already contains" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__])