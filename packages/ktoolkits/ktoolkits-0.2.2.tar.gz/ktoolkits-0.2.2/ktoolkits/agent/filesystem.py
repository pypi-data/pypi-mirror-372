#coding=utf-8
from dataclasses import dataclass
from typing import List

from ktoolkits.client.toolbox_api import ToolboxApi
from ktoolkits.models.sandbox import SandboxInstance
from ktoolkits.models.file_info import FileInfo

@dataclass
class FileUpload:
    """Represents a file to be uploaded to the Sandbox.

    Attributes:
        path (str): Absolute destination path in the Sandbox.
        content (bytes): File contents as a bytes object.
    """
    path: str
    content: bytes


class FileSystem:
    """Provides file system operations within a Sandbox.

    This class implements a high-level interface to file system operations that can
    be performed within a Daytona Sandbox.

    Attributes:
        instance (SandboxInstance): The Sandbox instance this file system belongs to.
    """

    def __init__(self, instance: SandboxInstance, toolbox_api: ToolboxApi):
        """Initializes a new FileSystem instance.

        Args:
            instance (SandboxInstance): The Sandbox instance this file system belongs to.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
        """
        self.instance = instance
        self.toolbox_api = toolbox_api

    def list_files(self, path: str):
        """Lists files and directories in a given path and returns their information, similar to the ls -l command.

        Args:
            path (str): Absolute path to the directory to list contents from.

        Returns:
            List[FileInfo]: List of file and directory information. Each FileInfo
            object includes the same fields as described in get_file_info().

        Example:
            ```python
            # List directory contents
            files = sandbox.fs.list_files("/workspace/data")

            # Print files and their sizes
            for file in files:
                if not file.is_dir:
                    print(f"{file.name}: {file.size} bytes")

            # List only directories
            dirs = [f for f in files if f.is_dir]
            print("Subdirectories:", ", ".join(d.name for d in dirs))
            ```
        """
        api_response =  self.toolbox_api._list_files(self.instance.info.id, path=path)
        return FileInfo.from_api_response(api_response)
    
    def upload_file(self, path: str, content: str)->bool:
        api_response =  self.toolbox_api._write_file(self.instance.info.id, path=path, content=content)
        if api_response.status_code == 200 and int(api_response.code) >= 0:
            return True
        return False
    
    def read_file(self, path: str)-> bytearray:
        return self.toolbox_api._read_file(self.instance.info.id, path=path)
