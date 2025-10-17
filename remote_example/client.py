from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
import asyncio
import json
import logging
logging.basicConfig(level=logging.INFO)

async def main():
    server_url = 'http://0.0.0.0:8000/mcp'
    # server_url = 'https://vocabulary-server-fsl6.onrender.com/mcp'
    headers = {}
    async with streamablehttp_client(server_url, headers) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("\nClient session initialized.\n")

            tools_list = await session.list_tools()
            logging.info(f"\nAvailable tools:\n")
            for tool in tools_list.tools:
                logging.info(f" - Name: {tool.name}")
                logging.info(f" - Description: {tool.description}\n")

            user_query = input(f"\nEnter your input for the {tools_list.tools[0].name} tool: ")
            response = await session.call_tool(tools_list.tools[0].name, {"text": user_query})
            logging.info(f"\nTool response: {json.loads(response.content[0].text)}\n")

            resources_list = await session.list_resources()
            logging.info(f"\nAvailable resources:\n")
            for resource in resources_list.resources:
                resource_content = await session.read_resource(resource.uri)
                logging.info(f" - Name: {resource.name}")
                logging.info(f" - Description: {resource.description}")
                logging.info(f" - Content: {json.loads(resource_content.contents[0].text)}\n")

            templates_list = await session.list_resource_templates()
            logging.info(f"\nAvailable resource templates:\n")
            for template in templates_list.resourceTemplates:
                logging.info(f" - Name: {template.name}")
                logging.info(f" - Description: {template.description}\n")
            
            user_name = input("\nEnter your name for the greeting resource template: ")
            greeting_response = await session.read_resource(f'greeting://{user_name}')
            logging.info(f"\nTemplate response: {greeting_response.contents[0].text}\n")

            prompts_list = await session.list_prompts()
            logging.info(f"\nAvailable prompts:\n")
            for prompt in prompts_list.prompts:
                logging.info(f" - Name: {prompt.name}")
                logging.info(f" - Description: {prompt.description}")
                content = await session.get_prompt(prompt.name)
                logging.info(f" - Content: {content.messages[0].content.text}\n")

if __name__ == '__main__':
    asyncio.run(main())