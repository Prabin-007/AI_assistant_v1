from datetime import datetime 
import requests
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response=requests.get(url)
    return response.text
  
  
#TOOLS=[]


TOOLS=[
        {
            "type": "function",
            "function":{
                "name": "get_current_time",
                "description": "Get the current date and time as formatted string.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
            },
        },
        {
            "type":"function",
            "function":{
                "name":"get_city_weather",
                "description":"gets the weather of a city",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "city":{
                            "type":"string",
                            "description":"City and country e.g. Bogotá, Colombia"
                        },
                    },
                }
            }
        }
    ] 

FUNCTION_NAME_TO_FUNCTION_MAPPING = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
}


'''
Here is an example function definition for a get_weather function
{
  "type": "function",
  "name": "get_weather",
  "description": "Retrieves current weather for the given location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and country e.g. Bogotá, Colombia"
      },
      "units": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Units the temperature will be returned in."
      }
    },
    "required": ["location", "units"],
    "additionalProperties": false
  },
  "strict": true
}
'''
#tool call examples
'''
[
    {
        "id": "fc_12345xyz",
        "call_id": "call_12345xyz",
        "type": "function_call",
        "name": "get_weather",
        "arguments": "{\"location\":\"Paris, France\"}"
    },
    {
        "id": "fc_67890abc",
        "call_id": "call_67890abc",
        "type": "function_call",
        "name": "get_weather",
        "arguments": "{\"location\":\"Bogotá, Colombia\"}"
    },
    {
        "id": "fc_99999def",
        "call_id": "call_99999def",
        "type": "function_call",
        "name": "send_email",
        "arguments": "{\"to\":\"bob@email.com\",\"body\":\"Hi bob\"}"
    }
]
'''
