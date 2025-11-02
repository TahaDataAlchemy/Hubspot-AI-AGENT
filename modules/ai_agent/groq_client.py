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
from datetime import datetime
from modules.auth.user_id import get_user_id_from_token
from modules.database.mongo_db.mongo_ops import MessageOperations
from modules.database.redis.redis_client import (redis_client,get_converstaion_key,get_messages_from_redis,save_messages_to_redis)

client = Groq()
MODEL = CONFIG.model_name

def run_convo(user_prompt: str):
    message_ops = MessageOperations()

    start_time = time.time()
    user_id = get_user_id_from_token()
    LOG.info(f"User id : {user_id}")
    
    messages = get_messages_from_redis(user_id)
    messages.append({
        "role": "user", 
        "content": str(user_prompt)
    })

    save_messages_to_redis(user_id,messages)
    
    tools = get_tools()
    total_tokens = 0
    total_tool_calls = 0
    react_cycles = []
    final_response = ""
    status = "completed"
    error_msg = None
    
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

            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            total_tokens += tokens_used
            
            tool_calls = response_message.tool_calls
            LOG.info(f"tool calls in iteration {iteration}: {tool_calls}")
            
            messages.append(response_message)
            save_messages_to_redis(user_id,messages)

            cycle_data = {
                "cycle_number":iteration,
                "timestamp":datetime.now().isoformat(),
                "llm_response":response_message.content,
                "tool_calls":[],
                "token_used":tokens_used
            }


            
            # If no tool calls, we're done
            if not tool_calls:
                final_response = response_message.content
                react_cycles.append(cycle_data)
                break
            
            # Process tool calls
            available_functions = {
                "get_contacts": (get_contacts, None),
                "create_contact": (create_contact, ContactProperties), 
                "update_contact": (update_contact, UpdateContactArgs),
                "delete_contact":(delete_contact,None),
                "search_by_identifier": (search_by_identifier, Search_by_query)
            }

            total_tool_calls +=len(tool_calls)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                tool_start = time.time()
                
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
                        save_messages_to_redis(user_id,messages)
                        tool_execution_time = int((time.time() - tool_start) * 1000)
                        cycle_data["tool_calls"].append({
                            "tool_call_id": tool_call.id,
                            "function_name": function_name,
                            "arguments": function_args,
                            "response": function_response,
                            "execution_time_ms": tool_execution_time,
                            "status": "error",
                            "timestamp": datetime.now().isoformat()
                        })
 
                        continue
                
                # Execute the function call
                try:
                    if model_val:
                        validated_args = model_val(**function_args)
                        function_response = function_to_call(validated_args)
                    else:
                        function_response = function_to_call(**function_args)
                    
                    LOG.info(f"Response from {function_name}: {function_response}")
                    tool_status = "success"
                        
                except Exception as e:
                    LOG.error(f"Error running {function_name}: {e}")
                    function_response = {"error": str(e)}
                    tool_status = "error"
                

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool", 
                    "name": function_name,
                    "content": json.dumps(function_response)
                })
                save_messages_to_redis(user_id,messages)
                tool_execution_time = int((time.time() - tool_start) * 1000)
                cycle_data["tool_calls"].append({
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "arguments": function_args,
                    "response": function_response,
                    "execution_time_ms": tool_execution_time,
                    "status": tool_status,
                    "timestamp": datetime.now().isoformat()
                })
            
            react_cycles.append(cycle_data)
        
            if iteration >= max_iterations and not final_response:
                final_call = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tool_choice="none",
                    max_completion_tokens=4096
                )
                
                final_response = final_call.choices[0].message.content
                total_tokens += final_call.usage.total_tokens if hasattr(final_call, 'usage') else 0
                messages.append({"role":"assistant","content":final_response})
                save_messages_to_redis(user_id,messages)
                
                react_cycles.append({
                    "cycle_number": iteration + 1,
                    "timestamp": datetime.now().isoformat(),
                    "llm_response": final_response,
                    "tool_calls": [],
                    "tokens_used": final_call.usage.total_tokens if hasattr(final_call, 'usage') else 0
                })
        
    except Exception as e:
        LOG.error(f"Error in run_convo: {e}")
        final_response = f"Error processing request: {str(e)}"
        status = "error"
        error_msg = str(e)
    
    response_time = time.time() - start_time

    message_data = {
        "user_id": user_id,
        "user_query": user_prompt.query,
        "ai_response": final_response,
        "react_cycles": react_cycles,
        "total_tokens": total_tokens,
        "total_tool_calls": total_tool_calls,
        "total_react_cycles": len(react_cycles),
        "response_time_seconds": round(response_time, 2),
        "model": MODEL,
        "status": status,
        "error": error_msg
    }

    message_id = message_ops.save_message(message_data)

    return {
        "message_id": message_id,
        "response": final_response,
        "tokens_used": total_tokens,
        "tool_calls": total_tool_calls,
        "react_cycles": len(react_cycles),
        "response_time": round(response_time, 2)
    }
