import re
import ast
from .config import *
import logging

logger = logging.getLogger(__name__) 

class Agent():
    def __init__(self, messages, available_tools, llm_service_client, model_id):
        self.messages = messages
        self.available_tools = available_tools
        self.client = llm_service_client
        self.model_id = model_id
        self.answer_re = r"Answer:\s*(.*)$"
        self.action_re = re.compile('^Action: (\w+): (.*)$')

    def __call__(self):
        response = self.execute()
        return response
    
    def execute(self, max_turns=10):
        turns = 0
        while turns < max_turns:
            response_content = self.llm_call()
            self.messages.append({"role": "assistant", "content": response_content})
            logger.info(f">assistant ({turns}):\n{response_content}\n")
            actions = [self.action_re.match(a) for a in response_content.split("\n") if self.action_re.match(a)]
            if actions:
                # There are actions to run
                for match in actions:
                    action = match.group(1)
                    tool_inputs = match.group(2)
                    kwargs = ast.literal_eval(tool_inputs)
                    logging.info(f"action: {action}, kwargs: {kwargs}")
                    if action not in self.available_tools:
                        logger.info(f"Action not recognized:\n\taction: {action}, kwargs: {kwargs}")
                        observation = "--Unknown action: {}: {}\nRefer to the available actions and choose again.".format(action, kwargs)
                        self.messages.append({"role": "assistant", "content": observation})
                    else:
                        logger.info(">action {}:\n\t tool: {}\n\t input: {}\n".format(turns, action, kwargs))

                        # observation = self.available_tools[action](**kwargs)
                        # self.messages.append({"role": "assistant", "content": str(observation)})
                        # turns += 1

                        try:
                            observation = self.available_tools[action](**kwargs)
                            logger.info(f">observation ({turns}):\n{observation}")
                            self.messages.append({"role": "assistant", "content": str(observation)})
                        except Exception as e:
                            logger.info(f'>!!ERROR IN ACTION CALL!!\n\t details: {e}')
                            observation = f"Error in action call: {action}: {kwargs} => {e}\nMake appropriate changes to the action call and/or action input."
                            logger.info(f">observation ({turns}):\n{observation}")
                            self.messages.append({"role": "assistant", "content": observation})
            else:
                # Search for the pattern with re.DOTALL to capture multiline text
                match = re.search(self.answer_re, response_content, re.DOTALL)
                if match:
                    result = match.group(1)  # Extracts the captured text after "Answer: "
                    return result
            turns += 1
        correction_message = "It seems your response does not include the phrase: Answer: <final answer here>. Please ensure your next response explicitly includes 'Answer:' followed by the final answer."
        return self(correction_message)

    def llm_call(self):
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=self.messages
            )
        return response.choices[0].message.content