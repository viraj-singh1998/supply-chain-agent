import inspect
from openai import OpenAI
from dotenv import load_dotenv
from utils import agent, tools
from utils.config import config
from pprint import pprint
import logging

# import sys
# sys.exit(0)

logger = logging.getLogger(__name__) 

load_dotenv()

def get_agent_tools():
    """
    Collects all the functions present in utils.tools module and gets their name, funcition object and docstring
    Args:
        -- None --
    Returns:
        tuple of (tools_desc, available_tools)
        tools_desc:
            str: name of each tool and its description
        available_tools:
            dict: whose each item is a tuple (function_name, function_object)
    """
    tool_specs = [(name, func, func.__doc__) for name, func in inspect.getmembers(tools, inspect.isfunction) if func.__module__ == "utils.tools"]
    tools_desc = ""
    for tool_name, func_object, func_doc in tool_specs:
        tools_desc = tools_desc + f"tool_name: {tool_name}\ntool_description: {func_doc}\n\n"
    # logger.info(f'Tools provided to agent: {tools_desc}')
    return tools_desc, {name: func for name, func, docstring in tool_specs}


def infer(user_id, user_name, user_messages):
    ## Gathering and re-factoring tools for the agent
    tools_desc, available_tools = get_agent_tools()

    ## Read exemplar outputs
    with open('exemplars.txt', 'r') as f:
        examples = f.read()

    ## Agent (LLM) Call
    client = OpenAI()
    messages = [
        {
            "role": "system", 
            "content": config.SYSTEM_MESSAGE.format(
                tools=tools_desc, 
                examples=examples,
                user_id=user_id, 
                user_name=user_name
                )
		}
	]
    messages.extend(user_messages)

    logger.info(f'Input messages: {[message for message in messages if message['role'] != 'system']}')
    
    agent_instance = agent.Agent( 
        messages=messages,
        available_tools=available_tools,
        llm_service_client=client, 
        model_id='gpt-4o-mini', 
        )
    answer = agent_instance()
    return answer