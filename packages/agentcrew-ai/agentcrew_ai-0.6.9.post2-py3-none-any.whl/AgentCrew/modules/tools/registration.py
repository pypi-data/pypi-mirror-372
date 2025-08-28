from .registry import ToolRegistry


def register_tool(definition_func, handler_factory, service_instance=None, agent=None):
    """
    Register a tool with the central registry or directly with an agent

    Args:
        definition_func: Function that returns tool definition given a provider
        handler_factory: Function that creates a handler function
        service_instance: Service instance needed by the handler (optional)
        agent: Agent instance to register the tool with directly (optional)
    """
    if agent:
        # Register directly with the agent, passing the original functions
        agent.register_tool(definition_func, handler_factory, service_instance)
    else:
        # Register with the global registry
        registry = ToolRegistry.get_instance()
        registry.register_tool(definition_func, handler_factory, service_instance)
