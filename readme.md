# AI Assistant — Learning Notes 🤖

Personal notes on building an AI assistant using Python and an LLM. These notes cover conversation history, tool calling, function mapping, JSON parsing, and argument unpacking.

## 1. Conversation History (`messages`)

The conversation is stored as a list of dictionaries.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Silchar?"}
]
```

* `system`: Instructions for the assistant.
* `user`: User's message.
* `assistant`: Model's response or tool-call request.
* `tool`: Result returned by a tool.

Passing `messages` to the LLM allows it to use the conversation history as context.

---

## 2. What Is Tool Calling?

Tool calling allows an LLM to request the execution of external functions.

For example, my assistant has two tools:

* `get_current_time()` — Returns the current date and time.
* `get_city_weather(city)` — Retrieves weather information using `wttr.in`.

**The workflow:**

1. The user asks a question.
2. The LLM decides whether a tool is needed.
3. The LLM returns a tool-call request with a function name and arguments.
4. Python executes the requested function.
5. The result is sent back to the LLM.
6. The LLM generates the final response.

**Important:** The LLM requests the function call; my Python application actually executes the function.

## 3. Tool Definitions (`TOOLS`)

The `TOOLS` list describes available functions to the LLM.

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Gets the weather of a city.",
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
]
```

The definition tells the LLM:

* Which function is available.
* What the function does.
* Which arguments it accepts.

Passing `tools=TOOLS` in the API request makes these definitions available to the model.

**Remember:** `TOOLS` describes functions; it does not execute them.

## 4. Function-to-Function-Name Mapping

```python
FUNCTION_NAME_TO_FUNCTION_MAPPING = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather
}
```

This dictionary maps **function names (strings) to actual Python function objects**.

For example:

```python
func_name = "get_city_weather"

fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
```

Now `fn` refers to the actual `get_city_weather` function.

We can execute it:

```python
result = fn(city="Silchar")
```

This is equivalent to:

```python
result = get_city_weather(city="Silchar")
```

### Why use a dictionary?

Without a mapping, we might need a long `if-elif` chain to select a function.

With a dictionary, we can retrieve and execute a function dynamically using its name.

**Remember:** `get_city_weather` refers to the function, while `get_city_weather()` executes it. We store the function without parentheses because we want to execute it later.

## 5. How Does the Import Work?

In `main.py`:

```python
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAPPING
```

Python executes the module's top-level code when it is first imported, defining the functions and creating the dictionary.

The dictionary already contains references to those functions.

Therefore, I can execute a function through the imported dictionary without importing that function separately.

---

## 6. JSON Parsing (`json.loads()`)

The LLM typically returns tool arguments as a JSON string.

Example:

```python
tool_call.function.arguments
```

Value:

```python
'{"city": "Silchar"}'
```

This is a **string**, not a Python dictionary.

To convert it:

```python
func_args = json.loads(tool_call.function.arguments)
```

Result:

```python
func_args = {
    "city": "Silchar"
}
```

`json.loads()` converts JSON text into the corresponding Python object.

Examples:

| JSON                  | Python                |
| --------------------- | --------------------- |
| `{"city": "Silchar"}` | `{"city": "Silchar"}` |
| `[1, 2, 3]`           | `[1, 2, 3]`           |
| `true`                | `True`                |
| `null`                | `None`                |

The JSON object containing `"city": "Silchar"` becomes a Python dictionary.

---

## 7. Argument Unpacking: `*` vs `**`

Unpacking allows us to pass values stored in collections as function arguments.

### A. Single Asterisk (`*`)

Unpacks an iterable into positional arguments.

```python
def add(a, b, c):
    return a + b + c

nums = [10, 20, 30]

print(add(*nums))
```

Output:

```text
60
```

`add(*nums)` is equivalent to:

```python
add(10, 20, 30)
```

The values are assigned to parameters based on their positions.

### B. Double Asterisk (`**`)

Unpacks a dictionary into keyword arguments.

```python
def introduce(name, age):
    print(name, age)

data = {
    "name": "Prabin",
    "age": 20
}

introduce(**data)
```

Output:

```text
Prabin 20
```

`introduce(**data)` is equivalent to:

```python
introduce(name="Prabin", age=20)
```

The dictionary keys match the function's parameter names.

### Quick Comparison

|                     | `*`                  | `**`              |
| ------------------- | -------------------- | ----------------- |
| Typically unpacks   | List or tuple        | Dictionary        |
| Passes              | Positional arguments | Keyword arguments |
| Matching depends on | Position             | Parameter name    |

---

## 8. How Unpacking Works in My Tool-Calling Code

This is the core part of my implementation:

```python
func_name = tool_call.function.name

func_args = json.loads(
    tool_call.function.arguments or "{}"
)

fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]

result = fn(**func_args)
```

Let's understand it step by step.

**Step 1: Get the function name**

```python
func_name = tool_call.function.name
```

Example:

```python
func_name = "get_city_weather"
```

**Step 2: Parse the arguments**

```python
func_args = json.loads(tool_call.function.arguments or "{}")
```

If the LLM returns:

```python
'{"city": "Silchar"}'
```

It becomes:

```python
{"city": "Silchar"}
```

The `or "{}"` fallback uses an empty JSON object if the arguments are empty or otherwise falsey.

**Step 3: Retrieve the function**

```python
fn = FUNCTION_NAME_TO_FUNCTION_MAPPING[func_name]
```

Now `fn` refers to `get_city_weather`.

**Step 4: Unpack the arguments and execute**

```python
result = fn(**func_args)
```

Since:

```python
func_args = {"city": "Silchar"}
```

Python effectively executes:

```python
result = get_city_weather(city="Silchar")
```

The function runs and returns the result.

**Important:** The dictionary keys must match the function's parameter names. For example, `"city"` matches `def get_city_weather(city)`, but `"location"` does not.

---

## 9. Sending Tool Results Back to the LLM

Executing the function is not the final step. The result must be returned to the model so it can formulate a response.

```python
messages.append(msg)

messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": str(result)
})
```

The `tool_call_id` associates the result with the corresponding tool call.

Then the application sends the updated conversation back to the model:

```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages
)
```

The model can now use the tool result to generate its answer.

For this to work correctly, the assistant's tool-call message must be preserved in the conversation, and each tool response must use the correct `tool_call_id`.

---

## 🔑 Final Revision: The Entire Process

```text
User asks a question
        |
        v
LLM receives messages + TOOLS
        |
        v
LLM returns a tool-call request
        |
        v
Extract function name and JSON arguments
        |
        v
json.loads() converts JSON string to dictionary
        |
        v
FUNCTION_NAME_TO_FUNCTION_MAPPING retrieves function
        |
        v
fn(**func_args) unpacks arguments and executes function
        |
        v
Python sends the result back to the LLM
        |
        v
LLM generates the final response
```

### Most Important Concepts to Remember

* **`TOOLS`** describes available functions to the LLM.
* **`FUNCTION_NAME_TO_FUNCTION_MAPPING`** maps function names to Python function objects.
* **`json.loads()`** converts JSON text into Python objects.
* **`*args`** unpacks positional arguments.
* **`**kwargs`** collects keyword arguments inside a function definition.
* **`fn(**func_args)`** unpacks a dictionary into keyword arguments during a function call.
* **Tool calling** connects the LLM's decisions with functions executed by the Python application.
* **Tool results** must be sent back to the LLM before it can use them to formulate its final response.
