from groq import Groq
import json

from modules.ai_agent.contacts.contact_tools import get_contacts,create_contact
from modules.crud_ops.contacts.schema import ContactProperties 
from modules.ai_agent.intent import get_tools
from config import CONFIG
from core.logger.logger import LOG

client = Groq()
MODEL = CONFIG.model_name

def run_convo(user_prompt):
    messages = [
    {
        "role": "system",
        "content": (
            "You are a HubSpot CRM assistant. When creating contacts, you MUST follow these rules:\n"
            "1. NEVER create fake or placeholder emails (like example.com, test.com, etc.)\n"
            "2. If the user doesn't provide an email, ask them for it instead of creating the contact\n"
            "3. Only use real email addresses provided by the user\n"
            "4. If you cannot create a contact due to missing required fields, explain what's needed"
        )
    },
    {
        "role": "user", 
        "content": str(user_prompt)
    }
]

    tools = get_tools()
    
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


    if tool_calls:
        available_functions = {
            "get_contacts": (get_contacts,None),
            "create_contact":(create_contact,ContactProperties)
        }
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            if function_name not in available_functions:
                LOG.error(f"Unknown function called: {function_name}")
                continue
            LOG.info(f"function Called: {function_name}")
            function_to_call,model_val = available_functions[function_name]
            arguments_of_func = tool_call.function.arguments
            function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}

            try:
                if model_val:
                    validated_Args = model_val(**function_args)
                    function_response = function_to_call(validated_Args)
                else:
                    function_response = function_to_call(**function_args)
                LOG.info(f"Response from {function_name}: {function_response}")
            except Exception as e:
                LOG.error(f"Error running {function_name}: {e}")
                function_response = {"error": str(e)}
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })
        

        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return  second_response.choices[0].message.content
    return response_message.content







# import asyncio
# import json
# import time
# from groq import Groq
# from modules.ai_agent.contacts.contact_tools import get_contacts
# from modules.ai_agent.intent import get_tools
# from config import CONFIG
# from core.logger.logger import LOG

# client = Groq()
# MODEL = CONFIG.model_name

# async def call_tool(tool_call, available_functions):
#     """Runs a single tool call asynchronously with detailed logging."""
#     start_time = time.time()
#     function_name = tool_call.function.name
#     LOG.info(f"[TOOL START] ID={tool_call.id} | Function={function_name} | Args={tool_call.function.arguments}")
    
#     function_to_call = available_functions[function_name]
#     arguments_of_func = tool_call.function.arguments
#     function_args = json.loads(arguments_of_func) if arguments_of_func != "null" else {}

#     # If the function is async, await it; else run in thread
#     if asyncio.iscoroutinefunction(function_to_call):
#         function_response = await function_to_call(**function_args)
#     else:
#         loop = asyncio.get_event_loop()
#         function_response = await loop.run_in_executor(None, lambda: function_to_call(**function_args))

#     end_time = time.time()
#     LOG.info(f"[TOOL END] ID={tool_call.id} | Function={function_name} | Duration={end_time - start_time:.2f}s | Result={function_response}")

#     return {
#         "tool_call_id": tool_call.id,
#         "role": "tool",
#         "name": function_name,
#         "content": json.dumps(function_response)
#     }

# async def run_convo(user_prompt):
#     LOG.info(f"[USER PROMPT] {user_prompt}")
    
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a HubSpot CRM assistant. Whenever the user wants to perform "
#                 "any CRM action from the defined tools, perform it and return the result."
#             )
#         },
#         {
#             "role": "user",
#             "content": str(user_prompt)
#         }
#     ]

#     tools = get_tools()
    
#     LOG.info("[STEP 1] Sending first request to LLM...")
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=messages,
#         stream=False,
#         tools=tools,
#         tool_choice="auto",
#         max_completion_tokens=4096
#     )
    
#     response_message = response.choices[0].message
#     tool_calls = response_message.tool_calls
#     LOG.info(f"[LLM RESPONSE] Tool calls detected: {len(tool_calls) if tool_calls else 0}")

#     if tool_calls:
#         available_functions = {
#             "get_contacts": get_contacts
#         }
#         messages.append(response_message)

#         # Run all tool calls in parallel
#         LOG.info("[STEP 2] Running tool calls in parallel...")
#         tasks = [call_tool(tc, available_functions) for tc in tool_calls]
#         tool_results = await asyncio.gather(*tasks)

#         LOG.info(f"[STEP 3] Tool calls completed. Adding results to messages.")
#         messages.extend(tool_results)

#         LOG.info("[STEP 4] Sending second request to LLM with tool results...")
#         second_response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages
#         )
#         LOG.info("[FINAL RESPONSE RECEIVED]")
#         return second_response.choices[0].message.content

# Example run
# if __name__ == "__main__":
#     result = asyncio.run(run_convo("Show contacts and also check if Sara exists"))
#     print(result)
