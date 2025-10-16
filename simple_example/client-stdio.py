from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
import sys
sys.path.append('..')  # To import utils from parent directory
from utils import load_config, save_config
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    config = load_config()
    server_config = config.get('server', {})
    if server_config.get('transport', 'sse') != 'stdio':
        logging.warning("Transport in config is not set to 'stdio'. Overriding for stdio client.")
        server_config['transport'] = 'stdio'
        config['server'] = server_config
        save_config(config)
    
    server_params = StdioServerParameters(command="python",args=['server.py'])
    async with stdio_client(server_params) as (read_stream, write_stream):
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