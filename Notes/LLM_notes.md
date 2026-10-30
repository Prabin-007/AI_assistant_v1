# LLM and Tool Calling — Revision Notes

## 1. What Is Tool Calling?

An LLM can decide that it needs an external function to answer a question.

For example:

**User:** What's the weather in Silchar?

The LLM can request the `get_city_weather` function. Our Python application executes it and sends the result back to the LLM.

**Important:** The LLM requests the function call; our Python code actually executes the function.

## 2. Two Things Required for Tool Calling

### A. Tool Definitions — `TOOLS`

A tool definition tells the LLM which functions are available, what they do, and what arguments they accept.

Example:

```python
{
    "type": "function",
    "function": {
        "name": "get_city_weather",
        "description": "Gets the weather of a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city"
                }
            },
            "required": ["city"]
        }
    }
}
```

This is a schema, not the actual Python function.

### B. Actual Python Functions

```python
def get_city_weather(city):
    ...
```

This contains the code that performs the operation.

**Remember:**

* `TOOLS` tells the LLM what it can request.
* The Python function performs the actual work.

## 3. How Does the LLM Know Which Function to Call?

We send the tool definitions along with the conversation:

```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages,
    tools=TOOLS
)
```

The LLM examines the user's request and decides whether to respond normally or request a tool call.

For example, it might return a tool call containing:

* Function name: `get_city_weather`
* Arguments: `{"city": "Silchar"}`

These are instructions returned by the LLM, not a direct execution of Python code.

## 4. Function Name to Function Mapping

```python
FUNCTION_NAME_TO_FUNCTION_MAPPING = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather
}
```

The LLM returns a function name as a string.

We use this dictionary to find the corresponding Python function:

```python
func_name = tool_call.function.name

fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
```

If `func_name` is `"get_city_weather"`, then `fn` refers to the actual `get_city_weather` function.

We can then execute it:

```python
result = fn(**func_args)
```

This is called **dynamic function dispatch**.

## 5. Understanding Function Arguments

The LLM may return arguments as a JSON string:

```json
{"city": "Silchar"}
```

Our Python code converts this string into a dictionary:

```python
func_args = json.loads(
    tool_call.function.arguments or "{}"
)
```

Then:

```python
result = fn(**func_args)
```

The `**` unpacks the dictionary into keyword arguments.

Effectively, this becomes:

```python
get_city_weather(city="Silchar")
```

## 6. What Is `tool_call.id`?

A tool call can contain an ID, a function name, and its arguments.

For example:

```text
id: call_abc123
name: get_city_weather
arguments: {"city": "Silchar"}
```

The ID identifies that particular tool call.

When sending the result back, we use the same ID so the API can associate the result with the correct request.

## 7. Sending the Tool Result Back

After executing the function:

```python
result = fn(**func_args)
```

We add its result to the conversation:

```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": str(result)
})
```

* `role: "tool"` indicates that this message contains a tool's result.
* `tool_call_id` links the result to the original tool call.
* `content` contains the result converted to a string.

**Important:** The correct field name is `tool_call_id`, not `tool_id`.

## 8. Why Call the LLM Again?

The tool result is not necessarily the final answer.

For example, the Python function might return:

```text
Silchar: 28°C, Partly cloudy
```

We send the updated conversation back to the LLM:

```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages
)
```

The LLM can now use the tool result to produce a natural-language answer.

For example:

> It's currently 28°C and partly cloudy in Silchar.

The second API call lets the LLM interpret the result and respond to the user.

## 9. What Is `messages`?

`messages` stores the conversation history.

Common message roles:

| Role        | Purpose                                   |
| ----------- | ----------------------------------------- |
| `system`    | Instructions for the assistant            |
| `user`      | User's message                            |
| `assistant` | Assistant's response or tool-call request |
| `tool`      | Result returned by a tool                 |

We maintain the history so the LLM can understand the conversation and the results of previous tool calls.

When a tool call occurs, we must also preserve the assistant's tool-call message and send the matching tool result.

## 10. Understanding `response` and `msg`

```python
response = client.chat.completions.create(...)
msg = response.choices[0].message
```

* `response` is the complete API response object.
* `response.choices[0]` is the first generated choice.
* `.message` contains the assistant's message.

To inspect the message:

```python
print(msg)
```

To print just the text:

```python
print(msg.content)
```

When the assistant requests a tool call, `msg.content` can be `None` because the message may contain tool-call instructions instead of normal text.

Check:

```python
if msg.tool_calls:
    ...
```

## 11. Complete Tool Calling Flow

1. User sends a message.
2. Add it to `messages`.
3. Send `messages` and `TOOLS` to the LLM.
4. The LLM returns a normal response or a tool-call request.
5. If a tool call is requested, extract its function name and arguments.
6. Use `FUNCTION_NAME_TO_FUNCTION_MAPPING` to find the Python function.
7. Execute it using `fn(**func_args)`.
8. Append the tool result using the matching `tool_call_id`.
9. Send the updated conversation back to the LLM.
10. Display the final answer.

**Core idea:** The LLM decides what operation is needed, Python executes it, and the LLM uses the result to answer the user.
