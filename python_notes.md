# Python Revision Notes

## 1. Imports

```python
from datetime import datetime
import json
import requests
```

* `from module import item` imports a specific function, class, or variable.
* `import json` imports the module, allowing us to use `json.loads()` and `json.dumps()`.
* When a Python file is imported, its top-level code executes, and its functions and variables become accessible to the importing file.

## 2. Dictionaries

A dictionary stores data as key-value pairs.

```python
student = {
    "name": "Prabin",
    "age": 20
}

print(student["name"])  # Prabin
```

Access a value using its key:

```python
student["age"]
```

## 3. Functions as Dictionary Values

Functions can be stored in dictionaries.

```python
def add(a, b):
    return a + b

FUNCTIONS = {
    "add": add
}
```

Notice that we use `add`, not `add()`.

* `add` refers to the function itself.
* `add()` executes the function.

We can retrieve and execute it dynamically:

```python
fn = FUNCTIONS["add"]
result = fn(10, 20)

print(result)  # 30
```

## 4. `*` vs `**`

### `*` — Unpacking an Iterable

```python
def add(a, b, c):
    return a + b + c

nums = [10, 20, 30]

add(*nums)
```

Equivalent to:

```python
add(10, 20, 30)
```

### `**` — Unpacking a Dictionary

```python
def greet(name, age):
    return f"{name} is {age} years old"

data = {"name": "Prabin", "age": 20}

greet(**data)
```

Equivalent to:

```python
greet(name="Prabin", age=20)
```

**Remember:** Dictionary keys must match the function's parameter names unless the function accepts arbitrary keyword arguments.

### `**kwargs` in Function Definitions

```python
def show(**kwargs):
    print(kwargs)

show(name="Prabin", age=20)
```

Output:

```python
{'name': 'Prabin', 'age': 20}
```

Here, `**kwargs` collects keyword arguments into a dictionary.

**Difference:**

* `fn(**data)` unpacks a dictionary.
* `def fn(**kwargs)` collects keyword arguments into a dictionary.

## 5. JSON Handling

JSON is a data format commonly used for exchanging information between applications.

### `json.loads()` — JSON String to Python Object

```python
args = '{"city": "Silchar"}'

data = json.loads(args)

print(data)
# {'city': 'Silchar'}
```

### `json.dumps()` — Python Object to JSON String

```python
data = {"city": "Silchar"}

result = json.dumps(data)
```

**Remember:** `loads` converts a JSON string into a Python object; `dumps` converts a Python object into a JSON string.

## 6. The `or` Operator

```python
arguments = ""
result = arguments or "{}"
```

If `arguments` is falsy, `or` returns `"{}"`.

Falsy values include:

* `""`
* `None`
* `0`
* `False`
* `[]`
* `{}`

In our project:

```python
func_args = json.loads(
    tool_call.function.arguments or "{}"
)
```

This provides an empty JSON object when the arguments string is empty or otherwise falsy.

## 7. Keyword Arguments and Dynamic Function Calls

```python
def get_city_weather(city):
    return f"Getting weather for {city}"

func_args = {"city": "Silchar"}

fn = get_city_weather
result = fn(**func_args)
```

Equivalent to:

```python
result = get_city_weather(city="Silchar")
```

This is useful when function names and arguments are received dynamically rather than written directly in the code.

## 8. String Formatting

Use an f-string to insert variables into a string.

```python
city = "Silchar"

url = f"https://wttr.in/{city}?format=3"
```

The value of `city` is inserted into the string.

## 9. Working with APIs Using `requests`

```python
import requests

url = "https://wttr.in/Silchar?format=3"

response = requests.get(url)

print(response.text)
```

* `requests.get(url)` sends an HTTP GET request.
* `response.text` gives the response body as text.

For real applications, also handle network errors and unsuccessful HTTP responses.
