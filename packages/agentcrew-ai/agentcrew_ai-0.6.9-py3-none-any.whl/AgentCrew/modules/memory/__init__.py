from .chroma_service import ChromaMemoryService
from .base_service import BaseMemoryService
from .tool import (
    get_memory_retrieve_tool_definition,
    get_memory_retrieve_tool_handler,
    get_memory_forget_tool_definition,
    get_memory_forget_tool_handler,
)
from .context_persistent import ContextPersistenceService


try:
    from .mem0_service import Mem0MemoryService

    __all__ = [
        "ChromaMemoryService",
        "BaseMemoryService",
        "Mem0MemoryService",
        "get_memory_retrieve_tool_definition",
        "get_memory_retrieve_tool_handler",
        "get_memory_forget_tool_definition",
        "get_memory_forget_tool_handler",
        "ContextPersistenceService",
    ]

except ModuleNotFoundError:
    __all__ = [
        "ChromaMemoryService",
        "BaseMemoryService",
        "get_memory_retrieve_tool_definition",
        "get_memory_retrieve_tool_handler",
        "get_memory_forget_tool_definition",
        "get_memory_forget_tool_handler",
        "ContextPersistenceService",
    ]
