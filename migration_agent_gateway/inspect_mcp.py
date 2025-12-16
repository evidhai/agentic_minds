from strands.tools.mcp import MCPClient
import inspect

print("Inspecting MCPClient...")
print(f"Has __enter__: {hasattr(MCPClient, '__enter__')}")
print(f"Has __aenter__: {hasattr(MCPClient, '__aenter__')}")
print(f"Dir: {dir(MCPClient)}")

try:
    print("Docstring:")
    print(MCPClient.__doc__)
except:
    pass
