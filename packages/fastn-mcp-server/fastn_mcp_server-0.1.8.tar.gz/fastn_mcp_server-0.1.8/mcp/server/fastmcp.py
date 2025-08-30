class FastMCP:
    def __init__(self, name=None):
        self.name = name
        self.tools = {}
        
    def tool(self, name=None, description=None):
        """Decorator for registering tools"""
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = {
                "function": func,
                "description": description or func.__doc__ or ""
            }
            return func
        return decorator
    
    def run(self, transport='stdio'):
        """Run the MCP server with the given transport"""
        if transport == 'stdio':
            # Implement stdio transport logic
            import json
            import sys
            print(f"FastMCP server '{self.name}' running with {len(self.tools)} tools registered")
            # Add implementation as needed

# Re-export FastMCP
__all__ = ["FastMCP"] 