from mcp.server.fastmcp import FastMCP
import socket
import sys
sys.path.append('..')  # To import utils from parent directory
from utils import load_config
import logging
logging.basicConfig(level=logging.INFO)

config = load_config()
server_config = config.get('server', {})
transport = server_config.get('transport', 'sse')
host = server_config.get('host', '0.0.0.0')
port = server_config.get('port', 8000)
streamable_http_path = server_config.get('streamable_http_path', '/mcp')
sse_path = server_config.get('sse_path', '/sse')
server_url = f'http://{host}:{port}{sse_path}' if transport == 'sse' else f'http://{host}:{port}{streamable_http_path}'

server = FastMCP(name='demo', 
                     host=host, 
                     port=port, 
                     streamable_http_path=streamable_http_path,
                     sse_path=sse_path)

@server.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@server.resource('file://greeting.txt')
def greet():
    """Return a greeting message."""
    with open('greeting.txt', 'r') as f:
        return f.read()
    
@server.resource('greeting://{name}')
def personalized_greet(name: str) -> str:
    """Return a personalized greeting message."""
    with open('greeting.txt', 'r') as f:
        greeting = f.read().strip()
    return f"Hello, {name}! {greeting}"

@server.prompt()
def intent_prompt():
    """LLM Prompt to ask the user for their intent."""
    return "Please ask the user for their intent for the conversation."

if __name__ == '__main__':
    logging.info(f"Running MCP server with {transport} transport at {server_url}!") 
    logging.info(f"Absolute IP address: {socket.gethostbyname(socket.gethostname())}")
    server.run(transport=transport)