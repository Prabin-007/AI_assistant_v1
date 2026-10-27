import os
from types import SimpleNamespace 

from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS,run_tool
from Utilities.utilities import log

load_dotenv() # Load environment variables from .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages=[]

MAX_ITERATIONS = 5

def stream_chat(history):
   
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True,
    )  
    
    full_response = ""
    calls = {}   # index -> tool call being built
    label_printed = False #to avoid printing the label multiple times for the same response

    try:
        for chunk in stream:
            if not chunk.choices:                       # some servers send chunks with no choices
                continue
            
            delta=chunk.choices[0].delta
            
            #1. we donot have content from LLM
            if delta.content:
                full_response += delta.content
                if not label_printed: #to not print(assistant:) again and again for the same response 
                    print("Assistant:", end=" ", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True) #streaming
            #2. tool_call
            for tc in (delta.tool_calls or[]):
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name: #function name can also arrive in chunks
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:#function arguments can also arrive in chunks
                    obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
        print("\nStreaming interrupted by user.")
        calls={}
        
    if label_printed:
        print()  # Move to the next line after streaming is done
    
    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])
    
    return full_response, calls_list
    
def build_tool_calls_payload(tool_calls):
    """
    Converts our collected tool calls into the dict format
    that the API expects inside an assistant message.
    """
    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }
        payload.append(tool_call_dict)

    return payload
     
#can add role system to act in a specific way
messages.append({
    "role": "system",
    "content": "You are a helpful, humble assistant. "
        "Answer general questions (programming, science, advice) from your own knowledge. "
        "Use a tool ONLY when the user asks for the current time, the weather, or their city. "
        "Keep answers under 50 words."
})
#always sent as the first message to the model to set the context of the conversation (index = 0)

while True:
    terminates = ["exit", "quit", "bye"]

    prompt = input("Prabin:")
    
    if prompt.lower() in terminates:
        break
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    #chained tool calling
    for step in range(MAX_ITERATIONS):
        full_response,tool_calls=stream_chat(messages)
        
        
        if not tool_calls:
            break
        
        log(f"Step {step + 1}: model requested {len(tool_calls)} tool calls")
        #tool call is requried
        messages.append({
            "role": "assistant",
            "content": full_response,
            "tool_calls": build_tool_calls_payload(tool_calls)
        })
        
        for tool_call in tool_calls:
            
            result = run_tool(tool_call)
            
            messages.append({
                "role": "tool",
                "tool_call_id":tool_call.id,
                "content": str(result),
            })

    else:
        fallback = "sorry, I am unable to provide a response at this time."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print("Assistant: " + fallback)
        continue
    messages.append({"role": "assistant", "content": full_response})
    
            
            
    