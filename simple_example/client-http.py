from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
import sys
sys.path.append('..')
from utils import load_config
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    server_config = load_config().get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8000)
    streamable_http_path = server_config.get('streamable_http_path', '/mcp')
    server_url = f'http://{host}:{port}{streamable_http_path}'
    headers = {}
    async with streamablehttp_client(server_url, headers) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("\nSession initialized.\n")

            tools_list = await session.list_tools()
            logging.info(f"\nAvailable tools: {tools_list.tools}\n")

            resource_list = await session.list_resources()
            logging.info(f"\nAvailable resources: {resource_list.resources}\n")

            templates_list = await session.list_resource_templates()
            logging.info(f"\nAvailable resource templates: {templates_list.resourceTemplates}\n")

            prompt_list = await session.list_prompts()
            logging.info(f"\nAvailable prompts: {prompt_list.prompts}\n")

if __name__ == '__main__':
    asyncio.run(main())