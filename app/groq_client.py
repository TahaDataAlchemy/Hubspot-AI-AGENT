# from groq import Groq
# import json

# from modules.ai_agent.contacts.contact_tools import get_contacts,create_contact,update_contact
# from modules.crud_ops.contacts.schema import ContactProperties ,UpdateContactArgs
# from modules.ai_agent.intent import get_tools
# from config import CONFIG
# from core.logger.logger import LOG

# client = Groq()
# MODEL = CONFIG.model_name
# messages = [
#     {
#         "role": "system",
#         "content": (
#             "You are a HubSpot CRM assistant. Follow these strict rules when managing contacts:\n\n"
#             "1. Do NOT create fake or placeholder emails (e.g., example.com, test.com, noemail@, etc.).\n"
#             "2. If the user does not provide an email, ask them to provide one before creating the contact.\n"
#             "3. Only create contacts with real, user-provided email addresses.\n"
#             "4. If a required field (like email) is missing, explain clearly what is needed before proceeding.\n"
#             "5. When updating a contact, use the HubSpot contact ID. If the user provides only a name or email, first resolve it to the HubSpot ID before updating.\n"
#             "6. When retrieving contact details by name:\n"
#             "   - If multiple contacts share that name, return a list showing each contact's HubSpot ID and email.\n"
#             "   - Ask the user to confirm which contact they want to proceed with, based on the email.\n\n"
#             "Always follow these rules exactly when interacting with HubSpot contacts.\n"
#             "Use get_contacts only to fetch all contacts. Do not pass arguments. To filter (e.g., by email), use the tool’s response that is already in the conversation."
#         )
#     }
# ]

# def run_convo(user_prompt:str):
#     global messages

#     messages.append({
#         "role":"user",
#         "content":str(user_prompt)
#     })

#     tools = get_tools()
    
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=messages,
#         stream=False,
#         tools=tools,
#         tool_choice="auto",
#         max_completion_tokens=4096
#     )
    
#     response_message = response.choices[0].message
#     LOG.info(f"response of first LLM call: {response_message}")
#     tool_calls = response_message.tool_calls
#     LOG.info(f"response of tool call: {tool_calls}")

#     messages.append(response_message)
#     LOG.info(f"response message of assitant : {response_message.content}")


#     if tool_calls:
#         available_functions = {
#             "get_contacts": (get_contacts,None),
#             "create_contact":(create_contact,ContactProperties),
#             "update_contact": (update_contact, UpdateContactArgs)
#         }

#         for tool_call in tool_calls:
#             function_name = tool_call.function.name
#             if function_name not in available_functions:
#                 LOG.error(f"Unknown function called: {function_name}")
#                 continue
#             LOG.info(f"function Called: {function_name}")
#             function_to_call,model_val = available_functions[function_name]
#             arguments_of_func = tool_call.function.arguments
#             function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}

#             try:
#                 if model_val:
#                     validated_Args = model_val(**function_args)
#                     function_response = function_to_call(validated_Args)
#                 else:
#                     function_response = function_to_call(**function_args)
#                 LOG.info(f"Response from {function_name}: {function_response}")
#             except Exception as e:
#                 LOG.error(f"Error running {function_name}: {e}")
#                 function_response = {"error": str(e)}
            
#             messages.append({
#                 "tool_call_id": tool_call.id,
#                 "role": "tool",
#                 "name": function_name,
#                 "content": json.dumps(function_response)
#             })
        

#         second_response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages
#         )
#         final_message = second_response.choices[0].message
#         messages.append(final_message)
#         return final_message.content
#     return response_message.content


# from groq import Groq
# import json

# from modules.ai_agent.contacts.contact_tools import get_contacts,create_contact,update_contact
# from modules.crud_ops.contacts.schema import ContactProperties ,UpdateContactArgs
# from modules.ai_agent.intent import get_tools
# from config import CONFIG
# from core.logger.logger import LOG

# client = Groq()
# MODEL = CONFIG.model_name
# messages = [
#     {
#         "role": "system",
#         "content": (
#             "You are a HubSpot CRM assistant. Follow these strict rules when managing contacts:\n\n"
#             "1. Do NOT create fake or placeholder emails (e.g., example.com, test.com, noemail@, etc.).\n"
#             "2. If the user does not provide an email, ask them to provide one before creating the contact.\n"
#             "3. Only create contacts with real, user-provided email addresses.\n"
#             "4. If a required field (like email) is missing, explain clearly what is needed before proceeding.\n"
#             "5. When updating a contact, use the HubSpot contact ID. If the user provides only a name or email, first resolve it to the HubSpot ID before updating.\n"
#             "6. When retrieving contact details by name:\n"
#             "   - If multiple contacts share that name, return a list showing each contact's HubSpot ID and email.\n"
#             "   - Ask the user to confirm which contact they want to proceed with, based on the email.\n\n"
#             "Always follow these rules exactly when interacting with HubSpot contacts.\n"
#             "Use get_contacts only to fetch all contacts. Do not pass arguments. To filter (e.g., by email), use the tool’s response that is already in the conversation."
#         )
#     }
# ]

# def run_convo(user_prompt:str):
#     global messages

#     messages.append({
#         "role":"user",
#         "content":str(user_prompt)
#     })

#     tools = get_tools()
    
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=messages,
#         stream=False,
#         tools=tools,
#         tool_choice="auto",
#         max_completion_tokens=4096
#     )
    
#     response_message = response.choices[0].message
#     LOG.info(f"response of first LLM call: {response_message}")
#     tool_calls = response_message.tool_calls
#     LOG.info(f"response of tool call: {tool_calls}")

#     messages.append(response_message)
#     LOG.info(f"response message of assitant : {response_message.content}")


#     if tool_calls:
#         available_functions = {
#             "get_contacts": (get_contacts,None),
#             "create_contact":(create_contact,ContactProperties),
#             "update_contact": (update_contact, UpdateContactArgs)
#         }

#         for tool_call in tool_calls:
#             function_name = tool_call.function.name
#             if function_name not in available_functions:
#                 LOG.error(f"Unknown function called: {function_name}")
#                 continue
#             LOG.info(f"function Called: {function_name}")
#             function_to_call,model_val = available_functions[function_name]
#             arguments_of_func = tool_call.function.arguments
#             function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}

#             try:
#                 if model_val:
#                     validated_Args = model_val(**function_args)
#                     function_response = function_to_call(validated_Args)
#                 else:
#                     function_response = function_to_call(**function_args)
#                 LOG.info(f"Response from {function_name}: {function_response}")
#             except Exception as e:
#                 LOG.error(f"Error running {function_name}: {e}")
#                 function_response = {"error": str(e)}
            
#             messages.append({
#                 "tool_call_id": tool_call.id,
#                 "role": "tool",
#                 "name": function_name,
#                 "content": json.dumps(function_response)
#             })
        

#         second_response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages
#         )
#         final_message = second_response.choices[0].message
#         messages.append(final_message)
#         return final_message.content
#     return response_message.content


from groq import Groq
import json
from modules.ai_agent.contacts.contact_tools import get_contacts, create_contact, update_contact
from modules.crud_ops.contacts.schema import ContactProperties, UpdateContactArgs
from modules.ai_agent.intent import get_tools
from config import CONFIG
from core.logger.logger import LOG

client = Groq()
MODEL = CONFIG.model_name

messages = [
    {
        "role": "system",
        "content": (
            "You are a HubSpot CRM assistant. Follow these strict rules:\n\n"
            
            "TOOL USAGE RULES:\n"
            "1. get_contacts function takes NO parameters - always call it as get_contacts() with empty arguments.\n"
            "2. After calling get_contacts once, all contact data is available in the conversation.\n"
            "3. When user asks for specific contact details, refer to the contact data from previous messages - DO NOT call get_contacts again.\n"
            "4. Use the conversation history to find and filter contacts by name, email, or ID.\n\n"
            
            "CONTACT MANAGEMENT RULES:\n"
            "1. Do NOT create fake or placeholder emails.\n"
            "2. If user doesn't provide email, ask for it before creating contacts.\n"
            "3. When retrieving contact details by name and multiple matches exist:\n"
            "   - Show all matches with their ID and email\n"
            "   - Ask user to specify which one they want\n"
            "4. When user confirms their choice (by email/ID), find that contact from the previous contact data.\n\n"
            
            "Remember: Once contacts are fetched, all subsequent queries should reference that data from the conversation history only."
        )
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
        # First LLM call - agent can decide to call tools
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=False,
            tools=tools,
            tool_choice="auto",
            max_completion_tokens=4096
        )
        
        response_message = response.choices[0].message
        LOG.info(f"response of first LLM call: {response_message}")
        
        tool_calls = response_message.tool_calls
        LOG.info(f"response of tool call: {tool_calls}")
        
        messages.append(response_message)
        LOG.info(f"response message of assistant: {response_message.content}")
        
        if tool_calls:
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
            
            # Second call - now agent must only use memory, no tools
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tool_choice="none",  # disable further tool calls
                max_completion_tokens=4096
            )
            
            final_message = second_response.choices[0].message
            messages.append(final_message)
            return final_message.content
        
        else:
            # No tool calls, just normal reply
            return response_message.content
        
    except Exception as e:
        LOG.error(f"Error in run_convo: {e}")
        return f"Error processing request: {str(e)}"
