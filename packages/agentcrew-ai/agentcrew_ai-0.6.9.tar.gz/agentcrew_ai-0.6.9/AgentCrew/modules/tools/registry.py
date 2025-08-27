from typing import Dict, Any, Callable, List, Optional


class ToolRegistry:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ToolRegistry()
        return cls._instance

    def __init__(self):
        self.tools = {}  # {tool_name: (definition_func, handler_factory, service_instance)}

    def register_tool(
        self,
        definition_func: Callable,
        handler_factory: Callable,
        service_instance=None,
    ):
        """
        Register a tool with the registry

        Args:
            definition_func: Function that returns tool definition given a provider
            handler_factory: Function that creates a handler given service instance
            service_instance: Instance of the service needed by the handler (optional)
        """
        # Call definition_func with default provider to get tool name
        default_def = definition_func()
        tool_name = self._extract_tool_name(default_def)

        self.tools[tool_name] = (definition_func, handler_factory, service_instance)

    def _extract_tool_name(self, tool_def: Dict) -> str:
        """Extract tool name from definition regardless of format"""
        if "name" in tool_def:
            return tool_def["name"]
        elif "function" in tool_def and "name" in tool_def["function"]:
            return tool_def["function"]["name"]
        else:
            raise ValueError("Could not extract tool name from definition")

    def get_tool_definitions(self, provider: str) -> List[Dict[str, Any]]:
        """Get all tool definitions formatted for the specified provider"""
        definitions = []
        for name, (definition_func, _, _) in self.tools.items():
            try:
                tool_def = definition_func(provider)
                definitions.append(tool_def)
            except Exception as e:
                print(f"Error getting definition for tool {name}: {e}")
        return definitions

    def get_tool_handler(self, tool_name: str) -> Optional[Callable]:
        """Get the handler for a specific tool"""
        if tool_name not in self.tools:
            return None

        _, handler_factory, service_instance = self.tools[tool_name]
        return (
            handler_factory(service_instance) if service_instance else handler_factory()
        )
