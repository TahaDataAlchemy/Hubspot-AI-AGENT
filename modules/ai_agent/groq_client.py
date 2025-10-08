from socket import timeout
from groq import Groq
import json
from modules.ai_agent.contacts.contact_tools import (get_contacts, create_contact, update_contact, delete_contact)
from modules.crud_ops.contacts.schema import ContactProperties, UpdateContactArgs
from modules.ai_agent.intent import get_tools
from config import CONFIG
from core.logger.logger import LOG
import time

client = Groq()
MODEL = CONFIG.model_name

# messages = [
#     {
#         "role": "system",
#         "content": (
#             "You are a HubSpot CRM assistant. Be proactive and intelligent about user requests.\n\n"
            
#             "TOOL USAGE:\n"
#             "- get_contacts(): Retrieves all contacts from CRM (no parameters needed)\n"
#             "- create_contact(): Creates new contact with provided details\n"
#             "- update_contact(): Updates existing contact by ID\n\n"
#             "- delete_contact(): Deletes existing contact by ID\n\n"
            
#             "INTELLIGENT DECISION MAKING:\n"
#             "1. If user asks to 'create' a contact but it already exists → automatically offer to update it\n"
#             "2. If user asks to 'update' but you don't have contact data → call get_contacts first\n"
#             "3. If user provides specific contact ID → use it directly without calling get_contacts\n"
#             "4. If multiple contacts match a name → show options and ask user to choose\n\n"
#             "5. When creating a contact and user give just name demand the email address (follow this very strictly)\n\n"
            
#             "PROACTIVE BEHAVIOR:\n"
#             "- When contact creation fails due to duplicate → immediately suggest updating the existing contact\n"
#             "- Don't just ask 'Would you like to update?' → be more specific: 'I can update [specific field] for you'\n"
#             "- If you have enough information to complete the task, do it\n"
#             "- Only ask for clarification when truly necessary\n\n"
            
#             "MEMORY MANAGEMENT:\n"
#             "- Once get_contacts is called, use that data for all subsequent queries in the conversation\n"
#             "- Don't call get_contacts multiple times unnecessarily\n"
#             "- Reference contact data from conversation history when available\n\n"
            
#             "CONTACT MANAGEMENT RULES:\n"
#             "- Never create fake email addresses\n"
#             "- Ask for missing required fields (email for new contacts)\n"
#             "- Use exact contact IDs from the contact data\n"
#             "- Provide clear, actionable responses\n\n"

#             "Follow stricly the point of INTELLIGENCE DECISION MAKING. \n\n"
#             "When deleting a contact, the user must provide the exact contact name.  \n\n"  
#             "If the user provides a name that is missing or misspelled, do NOT delete immediately.  \n\n"
#             "Instead, search the CRM for close matches and display them back to the user.  \n\n"
#             "Ask the user to confirm or correct the spelling.  \n\n"
#             "Only proceed with deletion once the user's input matches an existing contact name 100% exactly.  \n\n"

#             "IMPORTANT: You can only call one tool at a time. If multiple actions are needed, call them in separate turns.\n\n"
#             "Be helpful, efficient, and decisive. Take action when you have enough information. \n\n"
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
            "- update_contact(): Updates existing contact by ID\n"
            "- delete_contact(): Deletes existing contact by ID\n\n"
            
            "🚨 CRITICAL RULE - EMAIL REQUIREMENT:\n"
            "NEVER call create_contact() without a real email address provided by the user.\n"
            "- If user says 'create contact for John Doe' without email → STOP and ask: 'What is John Doe's email address?'\n"
            "- DO NOT generate fake emails like 'example@email.com' or 'johndoe@example.com'\n"
            "- DO NOT assume or invent email addresses\n"
            "- DO NOT proceed with contact creation until user provides a real email\n"
            "- Only call create_contact() when you have a legitimate email address from the user\n\n"
            
            "INTELLIGENT DECISION MAKING:\n"
            "1. If user asks to 'create' a contact but it already exists → automatically offer to update it\n"
            "2. If user asks to 'update' but you don't have contact data → call get_contacts first\n"
            "3. If user provides specific contact ID → use it directly without calling get_contacts\n"
            "4. If multiple contacts match a name → show options and ask user to choose\n"
            "5. For contact creation:\n"
            "   - User provides name only → Ask for email (MANDATORY)\n"
            "   - User provides name + email → Proceed with creation\n"
            "   - User provides incomplete data → Ask for missing required fields\n\n"
            
            "PROACTIVE BEHAVIOR:\n"
            "- When contact creation fails due to duplicate → immediately suggest updating the existing contact\n"
            "- Don't just ask 'Would you like to update?' → be more specific: 'I can update [specific field] for you'\n"
            "- If you have enough information to complete the task, do it\n"
            "- Only ask for clarification when truly necessary\n"
            "- Be assertive about getting required information before taking action\n\n"
            
            "MEMORY MANAGEMENT:\n"
            "- Once get_contacts is called, use that data for all subsequent queries in the conversation\n"
            "- Don't call get_contacts multiple times unnecessarily\n"
            "- Reference contact data from conversation history when available\n\n"
            
            "CONTACT DELETION RULES:\n"
            "- User must provide the exact contact name\n"
            "- If name is missing or misspelled → search CRM for close matches\n"
            "- Display matches and ask user to confirm\n"
            "- Only delete when user's input matches existing contact name 100% exactly\n\n"
            
            "CONTACT MANAGEMENT RULES:\n"
            "- NEVER create fake email addresses (this is the #1 priority rule)\n"
            "- Always ask for missing required fields before tool calls\n"
            "- Use exact contact IDs from the contact data\n"
            "- Provide clear, actionable responses\n\n"

            "IMPORTANT: You can only call one tool at a time. If multiple actions are needed, call them in separate turns.\n\n"
            
            "RESPONSE FLOW FOR CONTACT CREATION:\n"
            "Step 1: Check if user provided email\n"
            "Step 2: If NO email → Ask user for email and WAIT for response\n"
            "Step 3: If YES email → Proceed with create_contact()\n"
            "Step 4: Never skip Step 2\n\n"
            
            "Be helpful, efficient, and decisive. Take action when you have enough information, but NEVER create contacts without real email addresses.\n"
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
                "update_contact": (update_contact, UpdateContactArgs),
                "delete_contact":(delete_contact,None)
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



# class AgentFinish:
#     def __init__(self, content: str):
#         self.content = content


# def run_convo(user_prompt: str):
#     global messages
#     messages.append({
#         "role": "user",
#         "content": str(user_prompt)  # ✅ always ensure string
#     })

#     tools = get_tools()

#     try:
#         max_iterations = 20  # reasoning iterations
#         timeout_seconds = 60  # timeout for total call of agent
#         max_repeat_calls = 3  # same tool call repeat count in a row

#         iteration = 0
#         start_time = time.time()

#         last_tool_call = None
#         repeat_count = 0

#         while iteration < max_iterations:
#             if time.time() - start_time > timeout_seconds:
#                 LOG.info("Timeout reached. Stopping agent.")
#                 return "Stopped due to timeout"

#             iteration += 1

#             # LLM call
#             response = client.chat.completions.create(
#                 model=MODEL,
#                 messages=messages,
#                 stream=False,
#                 tools=tools,
#                 tool_choice="auto",
#                 max_completion_tokens=4096
#             )

#             response_message = response.choices[0].message
#             LOG.info(f"response of LLM call {iteration}: {response_message}")

#             tool_calls = response_message.tool_calls
#             LOG.info(f"tool calls in iteration {iteration}: {tool_calls}")

#             # ✅ Only append role + content, never raw SDK object
#             messages.append({
#                 "role": response_message.role,
#                 "content": response_message.content or ""
#             })

#             # If no tool calls, maybe it's a final answer
#             if not tool_calls:
#                 content = (response_message.content or "").strip()
#                 if "FINAL_ANSWER" in content:
#                     finish = AgentFinish(content.replace("FINAL_ANSWER:", "").strip())
#                     LOG.info(f"Agent finished with content: {finish.content}")
#                     return finish.content
#                 return content

#             available_functions = {
#                 "get_contacts": (get_contacts, None),
#                 "create_contact": (create_contact, ContactProperties),
#                 "update_contact": (update_contact, UpdateContactArgs),
#                 "delete_contact": (delete_contact, None),
#             }

#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
#                 arguments_of_func = tool_call.function.arguments or "{}"

#                 # Detect repeated tool+args
#                 call_signature = f"{function_name}:{arguments_of_func}"
#                 if call_signature == last_tool_call:
#                     repeat_count += 1
#                     if repeat_count >= max_repeat_calls:
#                         LOG.warning(f"Exiting loop: tool {function_name} repeated {repeat_count} times in a row.")
#                         return f"Stopped due to repeated {function_name} calls with same args."
#                 else:
#                     repeat_count = 0
#                 last_tool_call = call_signature

#                 if function_name not in available_functions:
#                     LOG.error(f"Unknown function called: {function_name}")
#                     continue

#                 LOG.info(f"function called: {function_name}")
#                 function_to_call, model_val = available_functions[function_name]

#                 try:
#                     function_args = {} if function_name == "get_contacts" else json.loads(arguments_of_func)
#                     if model_val:
#                         validated_args = model_val(**function_args)
#                         function_response = function_to_call(validated_args)
#                     else:
#                         function_response = function_to_call(**function_args)

#                     LOG.info(f"Response from {function_name}: {function_response}")

#                 except Exception as e:
#                     LOG.error(f"Error running {function_name}: {e}")
#                     function_response = {"error": str(e)}

#                 # ✅ Tool responses must be role=tool
#                 messages.append({
#                     "tool_call_id": tool_call.id,
#                     "role": "tool",
#                     "name": function_name,
#                     "content": json.dumps(function_response)
#                 })

#         # Max iteration reached
#         LOG.warning("Max iterations reached, stopping loop.")
#         return "Stopped due to iteration cap."

#     except Exception as e:
#         LOG.error(f"Error in run_convo: {e}")
#         return f"Error processing request: {str(e)}"
