"""
Bleu AI SDK Client implementation.
"""
import asyncio
import uuid
from typing import Dict, Any, Optional, Union
import httpx
from realtime import AsyncRealtimeClient, RealtimeSubscribeStates
from .exceptions import (
    AuthenticationError,
    WorkflowNotFoundError,
    InsufficientCreditsError,
    WorkflowExecutionError,
    ConnectionError
)
from .types import WorkflowResult, WorkflowStatus


class BleuAI:
    """
    Bleu AI client for executing workflows.
    
    Example:
        >>> client = BleuAI(api_key="your-api-key")
        >>> result = await client.run_workflow(
        ...     workflow_id="workflow-uuid",
        ...     inputs={"prompt": "Generate an image of a sunset"}
        ... )
        >>> print(result.outputs)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.buildbleu.com",
        realtime_url: str = "wss://zxtnotyhvaxmhnfpjuui.supabase.co/realtime/v1",
        supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4dG5vdHlodmF4bWhuZnBqdXVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIxMTgwMDIsImV4cCI6MjA2NzY5NDAwMn0.SRO3eh42DhpKlgzHAdr3m3EZAm9wh6-oEhtOuiQksjg"
    ):
        """
        Initialize the Bleu AI client.
        
        Args:
            api_key: Your Bleu AI API key
            base_url: Base URL for the Bleu AI API
            realtime_url: Realtime WebSocket URL for workflow updates
            supabase_anon_key: Supabase anonymous key for realtime connection
        """
        self.api_key = api_key
        self.base_url = base_url
        self.realtime_url = realtime_url
        self.supabase_anon_key = supabase_anon_key
        self._http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()
    
    async def run_workflow(
        self,
        workflow_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = True,
        timeout: float = 600.0
    ) -> WorkflowResult:
        """
        Run a workflow and optionally wait for completion.
        
        Args:
            workflow_id: UUID of the workflow to run
            inputs: Optional dictionary of user inputs for the workflow
            wait_for_completion: Whether to wait for the workflow to complete
            timeout: Maximum time to wait for completion (seconds)
            
        Returns:
            WorkflowResult containing the job ID, status, and outputs
            
        Raises:
            AuthenticationError: If API key is invalid
            WorkflowNotFoundError: If workflow doesn't exist or you don't have access
            InsufficientCreditsError: If you don't have enough credits
            WorkflowExecutionError: If the workflow fails to execute
            ConnectionError: If connection to services fails
        """
        # Generate job ID upfront
        job_id = str(uuid.uuid4())
        
        # Prepare request payload
        payload = {
            "job_id": job_id,
            "document_id": workflow_id,
            "user_inputs": inputs or {}
        }
        
        # Make request to run workflow
        try:
            response = await self._http_client.post(
                f"{self.base_url}/functions/v1/run-workflow-test",
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Bleu AI services: {str(e)}")
        
        # Handle response errors
        if response.status_code == 401:
            raise AuthenticationError("Invalid or inactive API key")
        elif response.status_code == 403:
            error_data = response.json() if response.content else {}
            if "owner does not have access" in error_data.get("error", ""):
                raise WorkflowNotFoundError(f"Workflow {workflow_id} not found or you don't have access")
            raise AuthenticationError(error_data.get("error", "Access denied"))
        elif response.status_code == 404:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        elif response.status_code != 200:
            error_data = response.json() if response.content else {}
            raise WorkflowExecutionError(f"Failed to start workflow: {error_data.get('error', response.text)}")
        
        # Parse response
        try:
            result_data = response.json()
        except Exception:
            raise WorkflowExecutionError("Invalid response from server")
        
        # If not waiting for completion, return immediately
        if not wait_for_completion:
            return WorkflowResult(
                job_id=job_id,
                status=WorkflowStatus.PENDING
            )
        
        # Wait for completion using realtime subscription
        return await self._wait_for_completion(job_id, timeout)
    
    async def _wait_for_completion(self, job_id: str, timeout: float) -> WorkflowResult:
        """
        Wait for a workflow to complete using realtime subscription.
        
        Args:
            job_id: The job ID to monitor
            timeout: Maximum time to wait (seconds)
            
        Returns:
            WorkflowResult with final status and outputs
        """
        # Create realtime client with Supabase anon key for WebSocket authentication
        # The API key will be validated server-side when messages are received
        socket = AsyncRealtimeClient(self.realtime_url, self.supabase_anon_key)
        
        # Create channel for this specific workflow (matching frontend format)
        channel = socket.channel(f"workflow:{job_id}", {
            "config": {
                "broadcast": {"ack": False, "self": False}
            }
        })
        
        # Create a future to track completion
        completion_future = asyncio.Future()
        result_data = {"status": WorkflowStatus.PENDING}
        
        def on_broadcast_message(payload):
            """Handle broadcast messages from the workflow."""
            try:
                # The actual workflow data is nested in payload['payload']
                workflow_data = payload.get("payload", {})
                status_str = workflow_data.get("status", "").lower()
                
                # Update result data
                if status_str == "completed":
                    result_data["status"] = WorkflowStatus.COMPLETED
                    result_data["outputs"] = workflow_data.get("result", {}).get("output", {})
                    if not completion_future.done():
                        completion_future.set_result(True)
                elif status_str == "failed":
                    result_data["status"] = WorkflowStatus.FAILED
                    result_data["error"] = workflow_data.get("error", "Workflow execution failed")
                    if not completion_future.done():
                        completion_future.set_result(True)
                elif status_str in ["running", "processing", "initializing"]:
                    result_data["status"] = WorkflowStatus.RUNNING
            except Exception as e:
                # Silently handle errors in broadcast processing
                pass
        
        def on_subscribe(status: RealtimeSubscribeStates, err: Optional[Exception]):
            """Handle subscription status changes."""
            if status == RealtimeSubscribeStates.CHANNEL_ERROR:
                if not completion_future.done():
                    completion_future.set_exception(
                        ConnectionError(f"Failed to subscribe to workflow updates: {err}")
                    )
            elif status == RealtimeSubscribeStates.TIMED_OUT:
                if not completion_future.done():
                    completion_future.set_exception(
                        ConnectionError("Realtime server did not respond in time")
                    )
        
        try:
            # Set up broadcast listener
            channel.on_broadcast("workflow_update", on_broadcast_message)
            
            # Subscribe to the channel
            await channel.subscribe(on_subscribe)
            
            # Wait for completion or timeout
            await asyncio.wait_for(completion_future, timeout=timeout)
            
        except asyncio.TimeoutError:
            # Timeout occurred
            result_data["status"] = WorkflowStatus.FAILED
            result_data["error"] = f"Workflow execution timed out after {timeout} seconds"
        except Exception as e:
            result_data["status"] = WorkflowStatus.FAILED
            result_data["error"] = f"Error waiting for workflow completion: {str(e)}"
        finally:
            # Clean up the socket connection
            try:
                await socket.remove_channel(channel)
            except Exception:
                # Silently handle cleanup errors
                pass
        
        # Check for insufficient credits error
        if result_data.get("error") and "insufficient credits" in result_data["error"].lower():
            raise InsufficientCreditsError(result_data["error"])
        
        # Return result
        return WorkflowResult(
            job_id=job_id,
            status=result_data["status"],
            outputs=result_data.get("outputs"),
            error=result_data.get("error")
        )
    
    async def run_workflow_sync(
        self,
        workflow_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        timeout: float = 300.0
    ) -> WorkflowResult:
        """
        Synchronous wrapper for run_workflow (for non-async contexts).
        
        This is a convenience method that creates an event loop if needed.
        Prefer using the async version when possible.
        
        Args:
            workflow_id: UUID of the workflow to run
            inputs: Optional dictionary of user inputs
            timeout: Maximum time to wait for completion
            
        Returns:
            WorkflowResult containing the outputs
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.run_workflow(workflow_id, inputs, wait_for_completion=True, timeout=timeout)
        )
