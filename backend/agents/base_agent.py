"""
Base Agent class for all agents in the system
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str):
        self.name = name
        self.memory: list[Dict[str, Any]] = []

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass

    def add_to_memory(self, interaction: Dict[str, Any]):
        """Add interaction to agent memory"""
        self.memory.append(interaction)
        logger.debug(f"{self.name} memory updated: {len(self.memory)} items")

    def get_memory_context(self, last_n: int = 5) -> str:
        """Get recent memory as context string"""
        recent = self.memory[-last_n:] if len(self.memory) > last_n else self.memory
        context = []
        for item in recent:
            context.append(f"[{item.get('type', 'unknown')}] {item.get('content', '')}")
        return "\n".join(context)
