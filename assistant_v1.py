import os 

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
    
    
    for step in range(MAX_ITERATIONS):
        if not msg.tool_calls:
            break
        
        log(f"Step {step + 1}: model requested {len(msg.tool_calls)} tool calls")
        #tool call is requried
        messages.append(msg)
        
        for tool_call in msg.tool_calls:
            
            result = run_tool(tool_call)
            
            messages.append({
                "role": "tool",
                "tool_id": tool_call.id,
                "content": str(result),
            })
            
        #2nd call to the model with the tool result
        
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS,
        )
        
        msg=response.choices[0].message
    else:
        fallback = "sorry, I am unable to provide a response at this time."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print("Assistant: " + fallback)
        continue
    messages.append({
        "role" : "assistant",
        "content" : msg.content
    })
    print("Assistant:", msg.content or "") #string + null is invalid, so we use empty string 
            
            
    