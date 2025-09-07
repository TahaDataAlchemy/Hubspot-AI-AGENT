from groq import Groq
import json
from modules.ai_agent.contacts.contact_tools import get_contacts, create_contact, update_contact
from modules.crud_ops.contacts.schema import ContactProperties, UpdateContactArgs
from modules.ai_agent.intent import get_tools
from config import CONFIG
from core.logger.logger import LOG

client = Groq()
MODEL = CONFIG.model_name

# messages = [
#     {
#         "role": "system",
#         "content": (
#             "You are a HubSpot CRM assistant. Follow these strict rules:\n\n"
            
#             "TOOL USAGE RULES:\n"
#             "1. get_contacts function takes NO parameters - always call it as get_contacts() with empty arguments.\n"
#             "2. After calling get_contacts once, all contact data is available in the conversation.\n"
#             "3. When user asks for specific contact details, refer to the contact data from previous messages - DO NOT call get_contacts again.\n"
#             "4. Use the conversation history to find and filter contacts by name, email, or ID.\n\n"
#             "5. any time user ask a query you have to call get_contact tool first and maintain memory and take info from it\n"
            
#             "CONTACT MANAGEMENT RULES:\n"
#             "1. Do NOT create fake or placeholder emails.\n"
#             "2. If user doesn't provide email, ask for it before creating contacts.\n"
#             "3. When retrieving contact details by name and multiple matches exist:\n"
#             "   - Show all matches with their ID and email\n"
#             "   - Ask user to specify which one they want\n"
#             "4. When user confirms their choice (by email/ID), find that contact from the previous contact data.\n\n"
            
#             "Remember: Once contacts are fetched, all subsequent queries should reference that data from the conversation history only."
#         )
#     }
# ]

# messages = [
#     {
#         "role": "system",
#         "content": (
#             "You are a HubSpot CRM assistant. Follow these rules:\n\n"
            
#             "TOOL USAGE RULES:\n"
#             "1. get_contacts() - Call ONLY when you need to search/list contacts\n"
#             "2. create_contact() - Call when user wants to create new contact\n"
#             "3. update_contact() - Call when user wants to update existing contact\n\n"
            
#             "DECISION LOGIC:\n"
#             "- If user provides contact ID directly → use it immediately\n"
#             "- If user provides name/email but no ID → call get_contacts first to find ID\n"
#             "- If multiple contacts match name → show options and ask user to choose\n\n"
            
#             "CONTACT MANAGEMENT:\n"
#             "- NEVER create fake emails\n"
#             "- Ask for missing required information\n"
#             "- Use exact contact IDs from get_contacts results\n\n"
            
#             "Be efficient - don't make unnecessary API calls."
            
#         )
#     }
# ]

messages = [
    {
        "role": "system",
        "content": (
            "You are a HubSpot CRM assistant. Be proactive and intelligent about user requests.\n\n"
            
            "TOOL USAGE:\n"
            "- get_contacts(): Retrieves all contacts from CRM (no parameters needed)\n"
            "- create_contact(): Creates new contact with provided details\n"
            "- update_contact(): Updates existing contact by ID\n\n"
            
            "INTELLIGENT DECISION MAKING:\n"
            "1. If user asks to 'create' a contact but it already exists → automatically offer to update it\n"
            "2. If user asks to 'update' but you don't have contact data → call get_contacts first\n"
            "3. If user provides specific contact ID → use it directly without calling get_contacts\n"
            "4. If multiple contacts match a name → show options and ask user to choose\n\n"
            
            "PROACTIVE BEHAVIOR:\n"
            "- When contact creation fails due to duplicate → immediately suggest updating the existing contact\n"
            "- Don't just ask 'Would you like to update?' → be more specific: 'I can update [specific field] for you'\n"
            "- If you have enough information to complete the task, do it\n"
            "- Only ask for clarification when truly necessary\n\n"
            
            "MEMORY MANAGEMENT:\n"
            "- Once get_contacts is called, use that data for all subsequent queries in the conversation\n"
            "- Don't call get_contacts multiple times unnecessarily\n"
            "- Reference contact data from conversation history when available\n\n"
            
            "CONTACT MANAGEMENT RULES:\n"
            "- Never create fake email addresses\n"
            "- Ask for missing required fields (email for new contacts)\n"
            "- Use exact contact IDs from the contact data\n"
            "- Provide clear, actionable responses\n\n"
            
            "Be helpful, efficient, and decisive. Take action when you have enough information."
        )
    }
]

# def run_convo(user_prompt: str):
#     global messages
    
#     messages.append({
#         "role": "user", 
#         "content": str(user_prompt)
#     })
    
#     tools = get_tools()
    
#     try:
#         # First LLM call - agent can decide to call tools
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages,
#             stream=False,
#             tools=tools,
#             tool_choice="auto",
#             max_completion_tokens=4096
#         )
        
#         response_message = response.choices[0].message
#         LOG.info(f"response of first LLM call: {response_message}")
        
#         tool_calls = response_message.tool_calls
#         LOG.info(f"response of tool call: {tool_calls}")
        
#         messages.append(response_message)
#         LOG.info(f"response message of assistant: {response_message.content}")
        
#         if tool_calls:
#             available_functions = {
#                 "get_contacts": (get_contacts, None),
#                 "create_contact": (create_contact, ContactProperties), 
#                 "update_contact": (update_contact, UpdateContactArgs)
#             }
            
#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
                
#                 if function_name not in available_functions:
#                     LOG.error(f"Unknown function called: {function_name}")
#                     continue
                
#                 LOG.info(f"function Called: {function_name}")
#                 function_to_call, model_val = available_functions[function_name]
#                 arguments_of_func = tool_call.function.arguments
                
#                 # Always empty for get_contacts
#                 if function_name == "get_contacts":
#                     function_args = {}
#                 else:
#                     function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}
                
#                 try:
#                     if model_val:
#                         validated_args = model_val(**function_args)
#                         function_response = function_to_call(validated_args)
#                     else:
#                         function_response = function_to_call(**function_args)
                    
#                     LOG.info(f"Response from {function_name}: {function_response}")
                        
#                 except Exception as e:
#                     LOG.error(f"Error running {function_name}: {e}")
#                     function_response = {"error": str(e)}
                
#                 # Add tool response to messages
#                 messages.append({
#                     "tool_call_id": tool_call.id,
#                     "role": "tool", 
#                     "name": function_name,
#                     "content": json.dumps(function_response)
#                 })
            
#             # Second call - now agent must only use memory, no tools
#             second_response = client.chat.completions.create(
#                 model=MODEL,
#                 messages=messages,
#                 tool_choice="none",  # disable further tool calls
#                 max_completion_tokens=4096
#             )
            
#             final_message = second_response.choices[0].message
#             messages.append(final_message)
#             return final_message.content
        
#         else:
#             # No tool calls, just normal reply
#             return response_message.content
        
#     except Exception as e:
#         LOG.error(f"Error in run_convo: {e}")
#         return f"Error processing request: {str(e)}"


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
                "update_contact": (update_contact, UpdateContactArgs)
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