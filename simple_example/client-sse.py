from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import sys
sys.path.append('..')  # To import utils from parent directory
from utils import load_config
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    server_config = load_config()['server']
    host = server_config.get('host', 'localhost')
    port = server_config.get('port', 8000)
    sse_path = server_config.get('sse_path', '/sse')
    server_url = f'http://{host}:{port}{sse_path}'
    headers = {}
    async with sse_client(server_url, headers) as (read_stream, write_stream):
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
