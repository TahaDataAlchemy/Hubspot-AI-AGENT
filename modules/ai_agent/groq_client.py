from socket import timeout
from groq import Groq
import json
from modules.ai_agent.contacts.contact_tools import (get_contacts, create_contact, update_contact, delete_contact,search_by_identifier)
from modules.crud_ops.contacts.schema import ContactProperties, UpdateContactArgs,Search_by_query
from modules.ai_agent.system_Prompt import system_prompt
from modules.ai_agent.intent import get_tools
from config import CONFIG
from core.logger.logger import LOG
import time

client = Groq()
MODEL = CONFIG.model_name

messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


def run_convo(user_prompt: str):
    global messages
    
    messages.append({
        "role": "user", 
        "content": str(user_prompt)
    })
    
    tools = get_tools()
    
    try:
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # LLM call - agent can decide to call tools
            response = client.chat.completions.create(
                model=MODEL,
                temperature=0.3,
                messages=messages,
                stream=False,
                tools=tools,
                tool_choice="auto",
                max_completion_tokens=4096
            )
            
            response_message = response.choices[0].message
            LOG.info(f"response of LLM call {iteration}: {response_message}")
            
            tool_calls = response_message.tool_calls
            LOG.info(f"tool calls in iteration {iteration}: {tool_calls}")
            
            messages.append(response_message)
            
            # If no tool calls, we're done
            if not tool_calls:
                return response_message.content
            
            # Process tool calls
            available_functions = {
                "get_contacts": (get_contacts, None),
                "create_contact": (create_contact, ContactProperties), 
                "update_contact": (update_contact, UpdateContactArgs),
                "delete_contact":(delete_contact,None),
                "search_by_identifier": (search_by_identifier, Search_by_query)
            }
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                
                if function_name not in available_functions:
                    LOG.error(f"Unknown function called: {function_name}")
                    continue
                
                LOG.info(f"function Called: {function_name}")
                function_to_call, model_val = available_functions[function_name]
                arguments_of_func = tool_call.function.arguments
                
                # Always empty for get_contacts
                if function_name == "get_contacts":
                    function_args = {}
                else:
                    function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}
                
                # VALIDATION FOR search_by_identifier 
                if function_name == "search_by_identifier":
                    query_value = function_args.get("query", "")
                    
                    # Check if it's a valid email or phone number
                    is_email = "@" in query_value and "." in query_value
                    is_phone = sum(c.isdigit() for c in query_value) >= 7
                    
                    if not (is_email or is_phone):
                        LOG.warning(f"Invalid search query rejected: '{query_value}'")
                        
                        # Return error to force LLM to ask for proper identifier
                        function_response = {
                            "error": "Invalid identifier provided",
                            "message": f"The query '{query_value}' is not a valid email or phone number. Please ask the user to provide a valid email address or phone number to search for this contact."
                        }
                        
                        # Add the error response to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response)
                        })
                        
                        # Skip the actual function call
                        continue
                
                # Execute the function call
                try:
                    if model_val:
                        validated_args = model_val(**function_args)
                        function_response = function_to_call(validated_args)
                    else:
                        function_response = function_to_call(**function_args)
                    
                    LOG.info(f"Response from {function_name}: {function_response}")
                        
                except Exception as e:
                    LOG.error(f"Error running {function_name}: {e}")
                    function_response = {"error": str(e)}
                
                # Add tool response to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool", 
                    "name": function_name,
                    "content": json.dumps(function_response)
                })
        
        # If we've reached max iterations, make a final call without tools
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tool_choice="none",
            max_completion_tokens=4096
        )
        
        final_message = final_response.choices[0].message
        messages.append(final_message)
        return final_message.content
        
    except Exception as e:
        LOG.error(f"Error in run_convo: {e}")
        return f"Error processing request: {str(e)}"