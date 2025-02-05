import os
from datetime import datetime
from flask import Flask, request, jsonify
import time
import uuid
import logger_config
import logging
from utils import tools
import invoke_agent
# import sys
# sys.exit(0)

logger = logging.getLogger(__name__) 

app = Flask(__name__)

def generate_unique_user_id(max_length=50):
    """Generate a unique user ID of the specified max length (default 50)."""
    # Generate a UUID and convert it to a string
    unique_id = str(uuid.uuid4())
    
    # Truncate it to the specified max length
    return unique_id[:max_length]

@app.route("/agent_call", methods=["POST"])
def agent_call():
    ## Parsing request body
    data = request.get_json()
    user_messages = data.get("messages")
    logger.info(f'POST request from frontend\ndata')    # TODO: remove
    user_id = data.get("user_id")
    user_name = data.get("user_name", "USER")
    if user_id.lower() == "na":
        user_id = generate_unique_user_id()
        
	## Maintainence/routine CRUD operations
    logger.info(tools.create_user(
        user_id=user_id, 
        user_name=user_name
        )
    )
    logger.info(tools.refresh_order_status())
    
	## Invoke agent script and get answer to user's query
    answer = invoke_agent.infer(user_id, user_name, user_messages)
    logger.info(f'Agent response:\n{answer}')
    agent_response = {"user_id": user_id, "message": answer}
    return jsonify({"response": agent_response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)