"""
Abstract interfaces.
Defines contracts that implementations must folloW.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IPipelineService(ABC):
    """Interface for query pipeline execution."""
    
    @abstractmethod
    async def execute(self, question: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """Execute a single query."""
        pass
    
    @abstractmethod
    async def execute_batch(self, questions: list, user_id: str = "anonymous") -> list:
        """Execute multiple queries concurrently."""
        pass


class ILogger(ABC):
    """Interface for logging."""
    
    @abstractmethod
    def info(self, message: str):
        pass
    
    @abstractmethod
    def error(self, message: str, exc_info: bool = False):
        pass
    
    @abstractmethod
    def debug(self, message: str):
        pass


class IRequestValidator(ABC):
    """Interface for request validation."""
    
    @abstractmethod
    def validate_question(self, question: str) -> bool:
        pass
    
    @abstractmethod
    def validate_batch(self, questions: list) -> bool:
        pass
