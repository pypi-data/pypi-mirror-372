#coding=utf-8

from typing import Optional


class SandboxInfo:
    """Structured information about a Sandbox.

    Attributes:
        id (str): Unique identifier for the Sandbox.
        image (str): Docker image used for the Sandbox.
        webapp_addr (str): web server public address
        webapp_pass (str): web server indentify password
        status (str): Current state of the Sandbox (e.g., "started", "stopped").
        created_at (Optional[str]): When the snapshot was created.
        updated_at (str): When the Sandbox was last updated.
        auto_stop_interval (int): Auto-stop interval in minutes.
    """
    id: str
    image: str
    webapp_addr: str
    mcpapp_addr: str
    webapp_pass: str
    status: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    auto_stop_interval: int


class SandboxInstance:
    """Represents a Sandbox instance."""
    info: Optional[SandboxInfo]