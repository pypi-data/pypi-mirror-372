#coding=utf-8
import ktoolkits
from ktoolkits.client.toolbox_api import ToolboxApi

from ktoolkits.agent.process import Process
from ktoolkits.agent.filesystem import FileSystem

from ktoolkits.models.sandbox import SandboxInstance
from ktoolkits.models.execute_result import ExecuteResult


class Sandbox:
    """
    ktoolkits Sandbox Class.
    """
    def __init__(
        self,
        id: str,
        instance: SandboxInstance,
        toolbox_api: ToolboxApi,
    ):
        """Initialize a new Sandbox instance.

        Args:
            id (str): Unique identifier for the Sandbox.
            instance (SandboxInstance): The underlying Sandbox instance.
            sandbox_api (SandboxApi): API client for Sandbox operations.
            toolbox_api (ToolboxApi): API client for toolbox operations.
        """
        self.id = id
        self.instance = instance
        
        self.process = Process(toolbox_api, instance)
        self.fs = FileSystem(instance, toolbox_api)

        self.toolbox_api = toolbox_api

    
    def get_web_service(self) -> str:
        web_endpoint = ktoolkits.base_http_api_url.split("/console")[0] 
        web_addr = web_endpoint + f"/sandbox/webapp-{self.instance.info.webapp_addr}/"
        return web_addr
    
    def get_mcp_service(self) -> str:
        web_endpoint = ktoolkits.base_http_api_url.split("/console")[0] 
        web_addr = web_endpoint + f"/sandbox/webapp-{self.instance.info.mcpapp_addr}/"
        return web_addr
    
    def start(self) -> None:
        """Start the Sandbox instance.

        Raises:
            KToolAPIError: If the removal operation fails.
        """
        self.toolbox_api._start_sandbox(self.id)

    
    def stop(self) -> None:
        """Stop the Sandbox instance.

        Raises:
            KToolAPIError: If the removal operation fails.
        """
        self.toolbox_api._stop_sandbox(self.id)


    def remove(self) -> None:
        """Remove the Sandbox instance.

        Raises:
            KToolAPIError: If the removal operation fails.
        """
        self.toolbox_api._remove_sandbox(self.id)
