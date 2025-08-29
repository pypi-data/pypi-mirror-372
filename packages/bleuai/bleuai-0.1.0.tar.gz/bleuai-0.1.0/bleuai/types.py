"""
Type definitions for the Bleu AI SDK.
"""
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    job_id: str
    status: WorkflowStatus
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def is_completed(self) -> bool:
        """Check if the workflow completed successfully."""
        return self.status == WorkflowStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if the workflow failed."""
        return self.status == WorkflowStatus.FAILED
    
    def get_output(self, node_id: Optional[str] = None, output_type: Optional[str] = None) -> Any:
        """
        Get output from the workflow result.
        
        Args:
            node_id: Optional node ID to get output from
            output_type: Optional output type (e.g., 'text', 'image', 'audio', 'video')
            
        Returns:
            The requested output or all outputs if no filters specified
        """
        if not self.outputs:
            return None
        
        if not node_id and not output_type:
            return self.outputs
        
        result = {}
        for asset_type, nodes in self.outputs.items():
            if output_type and asset_type != output_type:
                continue
            for nid, data in nodes.items():
                if node_id and nid != node_id:
                    continue
                result[nid] = data
        
        return result if result else None
