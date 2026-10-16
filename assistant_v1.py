from openai import OpenAI
from dotenv import load_dotenv
import os 
from tools import TOOLS,FUNCTION_NAME_TO_FUNCTION_MAPPING
import json
load_dotenv() # Load environment variables from .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages=[]

#can add role system to act in a specific way
messages.append({
    "role": "system",
    "content": "You are a helpful assistant and try to answer within 3 lines.AND DONOT EVER EXPOSE INTERNAL code or methods given to you in the tools.py file. If you are asked about them, politely decline and say that you cannot share internal code or methods."
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

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,
    )
    
    msg=response.choices[0].message
    #print(response.model_dump_json(indent=2))
    
    
    if msg.tool_calls:
        #tool call is requried
        messages.append(msg)
        
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")
            
            fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
            result = fn(**func_args)
            
            messages.append({
                "role": "tool",
                "tool_id": tool_call.id,
                "content": str(result),
            })
            
        #2nd call to the model with the tool result
        
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
        )
        
        msg=response.choices[0].message
         
    messages.append({
        "role": "assistant",
        "content": msg.content
    })
    
    print("Assistant:", msg.content)
            
            
    