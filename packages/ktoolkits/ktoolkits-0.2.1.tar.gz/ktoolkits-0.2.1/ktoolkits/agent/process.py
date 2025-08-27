import asyncio
import base64
import json
import time
from typing import Callable, Dict, List, Optional

#inner models
from ktoolkits.models.execute_result import ExecuteResult
from ktoolkits.models.sandbox import SandboxInstance,SandboxInfo


from ktoolkits.client.toolbox_api import ToolboxApi

from typing import Dict, List, Optional


class Process:
    """Handles process and code execution within a Sandbox.

    Attributes:
        code_toolbox (SandboxPythonCodeToolbox): Language-specific code execution toolbox.
        toolbox_api (ToolboxApi): API client for Sandbox operations.
        instance (SandboxInstance): The Sandbox instance this process belongs to.
    """

    def __init__(
        self,
        toolbox_api: ToolboxApi,
        instance: SandboxInstance,
    ):
        """Initialize a new Process instance.

        Args:
            code_toolbox (SandboxPythonCodeToolbox): Language-specific code execution toolbox.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
            instance (SandboxInstance): The Sandbox instance this process belongs to.
        """
        self.toolbox_api = toolbox_api
        self.instance = instance

    def exec(
        self,
        command: str,
        is_deamon: bool = False,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ExecuteResult:
        """Execute a shell command in the Sandbox.

        Args:
            command (str): Shell command to execute.
            cwd (Optional[str]): Working directory for command execution. If not
                specified, uses the Sandbox root directory.
            env (Optional[Dict[str, str]]): Environment variables to set for the command.
            timeout (Optional[int]): Maximum time in seconds to wait for the command
                to complete. 0 means wait indefinitely.

        Returns:
            ExecuteResponse: Command execution results containing:
                - exit_code: The command's exit status
                - result: Standard output from the command
                - artifacts: ExecutionArtifacts object containing `stdout` (same as result)
                and `charts` (matplotlib charts metadata)

        Example:
            ```python
            # Simple command
            response = sandbox.process.exec("echo 'Hello'")
            print(response.artifacts.stdout)  # Prints: Hello

            # Command with working directory
            result = sandbox.process.exec("ls", cwd="/workspace/src")

            # Command with timeout
            result = sandbox.process.exec("sleep 10", timeout=5)
            ```
        """
        base64_user_cmd = base64.b64encode(command.encode()).decode()
        command = f"echo '{base64_user_cmd}' | base64 -d | sh"

        if env and len(env.items()) > 0:
            safe_env_exports = (
                ";".join(
                    [
                        f"export {key}=$(echo '{base64.b64encode(value.encode()).decode()}' | base64 -d)"
                        for key, value in env.items()
                    ]
                )
                + ";"
            )
            command = f"{safe_env_exports} {command}"

        command = f'sh -c "{command}"'

        api_response = self.toolbox_api._execute_command(
                                                        sandbox_id=self.instance.info.id, 
                                                        command=command,
                                                        cwd=cwd,
                                                        is_deamon=is_deamon)

        execute_result = ExecuteResult.from_api_response(api_response)

        return execute_result