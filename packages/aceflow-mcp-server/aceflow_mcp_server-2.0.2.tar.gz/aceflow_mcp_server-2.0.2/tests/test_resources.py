"""Test suite for AceFlow MCP Resources."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from aceflow_mcp_server.resources import AceFlowResources
from aceflow_mcp_server.tools import AceFlowTools


class TestAceFlowResources:
    """Test AceFlow MCP Resources functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.resources = AceFlowResources()
        self.tools = AceFlowTools()  # For setting up test projects
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def call_resource(self, resource_name, *args, **kwargs):
        """Helper method to call resources."""
        resource = getattr(self.resources, resource_name)
        return resource(*args, **kwargs)
    
    def call_tool(self, tool_name, *args, **kwargs):
        """Helper method to call tools."""
        tool = getattr(self.tools, tool_name)
        return tool(*args, **kwargs)
    
    def test_project_state_no_project(self):
        """Test project state resource when no project exists."""
        result = self.call_resource("project_state", project_id="current")
        
        # Should be valid JSON
        state = json.loads(result)
        assert "project" in state
        assert state["project"]["status"] == "not_initialized"
    
    def test_project_state_with_project(self):
        """Test project state resource with initialized project."""
        # First initialize a project
        self.call_tool("aceflow_init", mode="standard", project_name="test-project")
        
        result = self.call_resource("project_state", project_id="current")
        
        # Should be valid JSON
        state = json.loads(result)
        assert state["project"]["name"] == "test-project"
        assert state["project"]["mode"] == "STANDARD"
        assert "created_at" in state["project"]
    
    def test_workflow_config_no_project(self):
        """Test workflow config resource when no project exists."""
        result = self.call_resource("workflow_config", config_id="default")
        
        # Should be valid JSON
        config = json.loads(result)
        assert config["status"] == "not_found"
    
    def test_workflow_config_with_project(self):
        """Test workflow config resource with initialized project."""
        # First initialize a project
        self.call_tool("aceflow_init", mode="complete", project_name="config-test")
        
        result = self.call_resource("workflow_config", config_id="default")
        
        # Should be valid JSON
        config = json.loads(result)
        assert config["status"] == "found"
        assert "template_content" in config
        assert "Complete Workflow" in config["template_content"]
    
    def test_stage_guide_valid_stage(self):
        """Test stage guide resource for valid stages."""
        valid_stages = [
            "user_stories", "task_breakdown", "test_design",
            "implementation", "unit_test", "integration_test",
            "code_review", "demo"
        ]
        
        for stage in valid_stages:
            result = self.call_resource("stage_guide", stage)
            
            # Should contain stage-specific content
            assert "## 目标" in result
            assert "## 主要任务" in result
            assert "## 输出要求" in result
    
    def test_stage_guide_invalid_stage(self):
        """Test stage guide resource for invalid stage."""
        result = self.call_resource("stage_guide", "invalid_stage")
        
        # Should contain error message with suggestions
        assert "invalid_stage" in result
        assert "可用阶段指南" in result
        assert "user_stories" in result  # Should list available stages
    
    def test_stage_guide_case_insensitive(self):
        """Test that stage guide works with different cases."""
        result_lower = self.call_resource("stage_guide", "user_stories")
        result_upper = self.call_resource("stage_guide", "USER_STORIES")
        result_mixed = self.call_resource("stage_guide", "User_Stories")
        
        # All should return the same guide (case insensitive)
        assert "用户故事分析阶段指南" in result_lower
        assert "用户故事分析阶段指南" in result_upper
        assert "用户故事分析阶段指南" in result_mixed
    
    def test_find_aceflow_project_root(self):
        """Test finding AceFlow project root."""
        # Create nested directory structure
        nested_dir = Path("level1/level2/level3")
        nested_dir.mkdir(parents=True)
        
        # Initialize project in root
        self.call_tool("aceflow_init", mode="minimal", project_name="nested-test")
        
        # Change to nested directory
        os.chdir(nested_dir)
        
        # Resources should still find the project root
        result = self.call_resource("project_state")
        state = json.loads(result)
        
        assert state["project"]["name"] == "nested-test"
    
    def test_resource_error_handling(self):
        """Test resource error handling."""
        # Create a broken state file
        aceflow_dir = Path(".aceflow")
        aceflow_dir.mkdir()
        
        state_file = aceflow_dir / "current_state.json"
        with open(state_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle the error gracefully
        result = self.call_resource("project_state")
        
        # Should be valid JSON with error information
        try:
            state = json.loads(result)
            assert "error" in state or "message" in state
        except json.JSONDecodeError:
            pytest.fail("Resource should return valid JSON even on error")


if __name__ == "__main__":
    pytest.main([__file__])