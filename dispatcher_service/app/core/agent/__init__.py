# Core/agent/__init__.py
from .agent_template_v2 import AgentBase
from .agents import WriteAgent, ReadAgent, ContentWriter

__all__ = ["AgentBase","WriteAgent", "ReadAgent", "ContentWriter"]