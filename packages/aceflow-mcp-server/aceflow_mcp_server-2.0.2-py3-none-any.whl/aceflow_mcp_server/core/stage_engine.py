"""Stage Engine for AceFlow workflow execution."""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json
import yaml
from jinja2 import Template, Environment, FileSystemLoader

from .document_generator import DocumentGenerator
from .template_manager import TemplateManager
from .project_manager import StateManager


@dataclass
class StageDefinition:
    """Definition of a workflow stage."""
    id: str
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    template: str
    quality_gates: List[str]


@dataclass
class StageResult:
    """Result of stage execution."""
    success: bool
    stage_id: str
    output_path: Optional[str] = None
    quality_score: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None
    execution_time: float = 0.0
    
    @classmethod
    def success_result(cls, stage_id: str, output_path: str, quality_score: float = 1.0):
        return cls(
            success=True,
            stage_id=stage_id,
            output_path=output_path,
            quality_score=quality_score,
            errors=[],
            warnings=[]
        )
    
    @classmethod
    def failed_result(cls, stage_id: str, errors: List[str]):
        return cls(
            success=False,
            stage_id=stage_id,
            errors=errors or [],
            warnings=[]
        )


class StageEngine:
    """Core engine for executing AceFlow workflow stages."""
    
    def __init__(self, project_root: Path):
        """Initialize the stage engine.
        
        Args:
            project_root: Root directory of the AceFlow project
        """
        self.project_root = project_root
        self.aceflow_dir = project_root / ".aceflow"
        self.result_dir = project_root / "aceflow_result"
        self.clinerules_dir = project_root / ".clinerules"
        
        # Initialize components
        self.document_generator = DocumentGenerator(self.clinerules_dir)
        self.template_manager = TemplateManager(self.clinerules_dir)
        self.state_manager = StateManager(self.aceflow_dir)
        
        # Load mode definition
        self.mode_definition = self._load_mode_definition()
    
    def execute_current_stage(self) -> StageResult:
        """Execute the current stage based on project state."""
        current_state = self.state_manager.get_current_state()
        current_stage = current_state.get("flow", {}).get("current_stage")
        
        if not current_stage:
            return StageResult.failed_result("unknown", ["No current stage defined"])
        
        return self.execute_stage(current_stage)
    
    def execute_stage(self, stage_id: str) -> StageResult:
        """Execute a specific stage.
        
        Args:
            stage_id: ID of the stage to execute
            
        Returns:
            StageResult with execution details
        """
        start_time = datetime.now()
        
        try:
            # 1. Get stage definition
            stage_def = self._get_stage_definition(stage_id)
            if not stage_def:
                return StageResult.failed_result(stage_id, [f"Stage '{stage_id}' not found"])
            
            # 2. Validate inputs
            input_validation = self._validate_stage_inputs(stage_def)
            if not input_validation[0]:
                return StageResult.failed_result(stage_id, input_validation[1])
            
            # 3. Collect input data
            input_data = self._collect_input_data(stage_def)
            
            # 4. Generate document
            document_result = self.document_generator.generate_stage_document(
                stage_def, input_data
            )
            
            if not document_result.success:
                return StageResult.failed_result(stage_id, document_result.errors)
            
            # 5. Save output
            output_path = self._save_stage_output(stage_def, document_result.content)
            
            # 6. Update project state
            self.state_manager.complete_stage(stage_id, str(output_path))
            
            # 7. Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = StageResult.success_result(
                stage_id, str(output_path), document_result.quality_score
            )
            result.execution_time = execution_time
            result.warnings = document_result.warnings
            
            return result
            
        except Exception as e:
            return StageResult.failed_result(stage_id, [f"Execution error: {str(e)}"])
    
    def get_stage_requirements(self, stage_id: str) -> Dict[str, Any]:
        """Get requirements for a specific stage.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            Dictionary with stage requirements
        """
        stage_def = self._get_stage_definition(stage_id)
        if not stage_def:
            return {"error": f"Stage '{stage_id}' not found"}
        
        return {
            "stage_id": stage_id,
            "name": stage_def.name,
            "description": stage_def.description,
            "required_inputs": stage_def.inputs,
            "expected_outputs": stage_def.outputs,
            "quality_gates": stage_def.quality_gates
        }
    
    def validate_stage_readiness(self, stage_id: str) -> Dict[str, Any]:
        """Validate if a stage is ready to execute.
        
        Args:
            stage_id: ID of the stage to validate
            
        Returns:
            Validation result with details
        """
        stage_def = self._get_stage_definition(stage_id)
        if not stage_def:
            return {
                "ready": False,
                "errors": [f"Stage '{stage_id}' not found"]
            }
        
        input_validation = self._validate_stage_inputs(stage_def)
        
        return {
            "ready": input_validation[0],
            "stage_name": stage_def.name,
            "required_inputs": stage_def.inputs,
            "missing_inputs": input_validation[1] if not input_validation[0] else [],
            "errors": input_validation[1] if not input_validation[0] else []
        }
    
    def get_next_stage(self) -> Optional[str]:
        """Get the next stage in the workflow.
        
        Returns:
            Next stage ID or None if at the end
        """
        current_state = self.state_manager.get_current_state()
        current_stage = current_state.get("flow", {}).get("current_stage")
        
        if not current_stage or not self.mode_definition:
            return None
        
        stages = self.mode_definition.get("stages", [])
        current_index = -1
        
        for i, stage in enumerate(stages):
            if stage.get("id") == current_stage:
                current_index = i
                break
        
        if current_index >= 0 and current_index < len(stages) - 1:
            return stages[current_index + 1].get("id")
        
        return None
    
    def advance_to_next_stage(self) -> Dict[str, Any]:
        """Advance to the next stage in the workflow.
        
        Returns:
            Result of stage advancement
        """
        next_stage = self.get_next_stage()
        if not next_stage:
            return {
                "success": False,
                "message": "No next stage available"
            }
        
        # Update current stage
        self.state_manager.set_current_stage(next_stage)
        
        return {
            "success": True,
            "previous_stage": self.state_manager.get_current_state().get("flow", {}).get("current_stage"),
            "current_stage": next_stage,
            "message": f"Advanced to stage: {next_stage}"
        }
    
    def _load_mode_definition(self) -> Optional[Dict[str, Any]]:
        """Load the mode definition for the current project."""
        try:
            current_state = self.state_manager.get_current_state()
            mode = current_state.get("project", {}).get("mode", "").lower()
            
            mode_file = self.clinerules_dir / "config" / "mode_definitions.yaml"
            if not mode_file.exists():
                return None
            
            with open(mode_file, 'r', encoding='utf-8') as f:
                definitions = yaml.safe_load(f)
            
            return definitions.get("modes", {}).get(mode)
            
        except Exception:
            return None
    
    def _get_stage_definition(self, stage_id: str) -> Optional[StageDefinition]:
        """Get definition for a specific stage."""
        if not self.mode_definition:
            return None
        
        stages = self.mode_definition.get("stages", [])
        for stage_data in stages:
            if stage_data.get("id") == stage_id:
                return StageDefinition(
                    id=stage_data.get("id"),
                    name=stage_data.get("name"),
                    description=stage_data.get("description", ""),
                    inputs=stage_data.get("inputs", []),
                    outputs=stage_data.get("outputs", []),
                    template=stage_data.get("template", ""),
                    quality_gates=stage_data.get("quality_gates", [])
                )
        
        return None
    
    def _validate_stage_inputs(self, stage_def: StageDefinition) -> Tuple[bool, List[str]]:
        """Validate that all required inputs are available.
        
        Args:
            stage_def: Stage definition
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        missing_inputs = []
        
        for required_input in stage_def.inputs:
            if not self._check_input_availability(required_input):
                missing_inputs.append(required_input)
        
        if missing_inputs:
            return False, [f"Missing required inputs: {', '.join(missing_inputs)}"]
        
        return True, []
    
    def _check_input_availability(self, input_name: str) -> bool:
        """Check if a required input is available.
        
        Args:
            input_name: Name of the input to check
            
        Returns:
            True if input is available
        """
        # Check for existing documents in aceflow_result
        if "文档" in input_name or "document" in input_name.lower():
            # Look for corresponding stage output
            for file_path in self.result_dir.glob("*.md"):
                if input_name.lower().replace("文档", "").replace("document", "").strip() in file_path.stem.lower():
                    return True
        
        # Check for PRD document
        if "prd" in input_name.lower() or "需求" in input_name:
            prd_locations = [
                self.project_root / "docs" / "PRD.md",
                self.project_root / "PRD.md",
                self.project_root / "docs" / "requirements.md"
            ]
            return any(path.exists() for path in prd_locations)
        
        # Check for other common inputs
        if "业务需求" in input_name:
            return True  # Assume business requirements are available
        
        return False
    
    def _collect_input_data(self, stage_def: StageDefinition) -> Dict[str, Any]:
        """Collect input data for stage execution.
        
        Args:
            stage_def: Stage definition
            
        Returns:
            Dictionary with input data
        """
        input_data = {
            "project": self.state_manager.get_current_state().get("project", {}),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "stage": {
                "id": stage_def.id,
                "name": stage_def.name,
                "description": stage_def.description
            }
        }
        
        # Collect specific input files
        for input_name in stage_def.inputs:
            input_content = self._load_input_content(input_name)
            if input_content:
                input_data[input_name.lower().replace(" ", "_")] = input_content
        
        return input_data
    
    def _load_input_content(self, input_name: str) -> Optional[str]:
        """Load content from an input file.
        
        Args:
            input_name: Name of the input
            
        Returns:
            Content of the input file or None
        """
        try:
            # Handle PRD document
            if "prd" in input_name.lower() or "需求" in input_name:
                prd_locations = [
                    self.project_root / "docs" / "PRD.md",
                    self.project_root / "PRD.md"
                ]
                for path in prd_locations:
                    if path.exists():
                        return path.read_text(encoding='utf-8')
            
            # Handle other stage outputs
            for file_path in self.result_dir.glob("*.md"):
                if input_name.lower().replace("文档", "").replace("document", "").strip() in file_path.stem.lower():
                    return file_path.read_text(encoding='utf-8')
            
            return None
            
        except Exception:
            return None
    
    def _save_stage_output(self, stage_def: StageDefinition, content: str) -> Path:
        """Save the generated content to output file.
        
        Args:
            stage_def: Stage definition
            content: Generated content
            
        Returns:
            Path to the saved file
        """
        # Ensure result directory exists
        self.result_dir.mkdir(exist_ok=True)
        
        # Generate filename based on stage
        stage_number = stage_def.id.split("_")[0] if "_" in stage_def.id else "00"
        stage_name = stage_def.id.split("_", 1)[1] if "_" in stage_def.id else stage_def.id
        
        filename = f"{stage_number}_{stage_name}.md"
        output_path = self.result_dir / filename
        
        # Save content
        output_path.write_text(content, encoding='utf-8')
        
        return output_path