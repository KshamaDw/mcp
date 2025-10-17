from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
import asyncio
import json
import logging
logging.basicConfig(level=logging.INFO)

async def main():
    server_url = 'http://0.0.0.0:8000/mcp'#'https://vocabulary-server-fsl6.onrender.com/mcp'
    headers = {}
    async with streamablehttp_client(server_url, headers) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("\nClient session initialized.\n")

            user_name = input("Enter your name for the greeting resource: ")
            greeting_response = await session.read_resource(f'greeting://{user_name}')
            logging.info(f" - {greeting_response.contents[0].text}\n")

            tools_list = await session.list_tools()
            logging.info(f"\nAvailable tools: {tools_list.tools}\n")

            user_query = input(f"Enter your input for the {tools_list.tools[0].name} tool: ")
            response = await session.call_tool(tools_list.tools[0].name, {"text": user_query})
            logging.info(f"\nTool response: {json.loads(response.content[0].text)}\n")

            prompts_list = await session.list_prompts()
            logging.info(f"\nAvailable prompts:\n")
            for prompt in prompts_list.prompts:
                logging.info(f" - Name: {prompt.name}")
                logging.info(f" - Description: {prompt.description}")
                content = await session.get_prompt(prompt.name)
                logging.info(f" - Content: {content.messages[0].content.text}\n")

if __name__ == '__main__':
    asyncio.run(main())