from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
from mcp.types import CreateMessageResult, TextContent, ElicitResult
import asyncio
import json
import logging
logging.basicConfig(level=logging.INFO)

class LoggingCallback:
    async def __call__(self, params) -> None:
        logging.info(f'Message from server: {params.data}')

async def sampling_callback(context, params):
    text_input = input(params.messages[0].content.text)
    logging.info('Returning from sampling callback. Sending user input to server...')
    return CreateMessageResult(
        role="user",
        content=TextContent(type='text', text=text_input),
        model='user_input',
    )

async def elicitation_callback(context, params):
    lemmatize = input(params.message).strip()
    logging.info('Returning from elicitation callback. Sending user input to server...')
    if lemmatize:
        return ElicitResult(action="accept", content={"lemmatize": lemmatize})
    else:
        return ElicitResult(action="decline", content=None)

async def main():
    server_url = 'http://0.0.0.0:8000/mcp'
    # server_url = 'https://vocabulary-server-fsl6.onrender.com/mcp'
    headers = {}
    async with streamablehttp_client(server_url, headers) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, 
                                 write_stream,
                                 logging_callback=LoggingCallback(),
                                 sampling_callback=sampling_callback,
                                 elicitation_callback=elicitation_callback) as session:
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

            response = await session.call_tool(tools_list.tools[1].name)
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