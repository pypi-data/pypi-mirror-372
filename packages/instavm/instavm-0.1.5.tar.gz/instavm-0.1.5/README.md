# InstaVM Client

A Python client library for interacting with a simple API.

## Installation

You can install the package using pip:
     ```
     pip install instavm
     ```

## Usage

### Basic Usage
```python
from instavm import InstaVM, ExecutionError, NetworkError

# Create client with automatic session management
client = InstaVM(api_key='your_api_key')

try:
    # Execute a command
    result = client.execute("print(100**100)")
    print(result)

    # Get usage info for the session
    usage = client.get_usage()
    print(usage)

except ExecutionError as e:
    print(f"Code execution failed: {e}")
except NetworkError as e:
    print(f"Network issue: {e}")
finally:
    client.close_session()
```

### Context Manager (Recommended)
```python
from instavm import InstaVM

# Automatic session cleanup
with InstaVM(api_key='your_api_key') as client:
    result = client.execute("print('Hello from InstaVM!')")
    print(result)
    # Session automatically closed
```

### Streaming Execution
```python
from instavm import InstaVM

with InstaVM(api_key='your_api_key') as client:
    # Real-time output streaming
    for output in client.execute_streaming("pip install matplotlib && python -c 'import matplotlib; print(\"Success!\")'"):
        print(f"Output: {output}")
```

### Error Handling
```python
from instavm import InstaVM, AuthenticationError, RateLimitError, SessionError

try:
    client = InstaVM(api_key='invalid_key')
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded - try again later")
except SessionError as e:
    print(f"Session error: {e}")
```
