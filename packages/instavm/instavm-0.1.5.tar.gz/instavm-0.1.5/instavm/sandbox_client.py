import requests
import time
import json
from typing import Optional, Dict, Any, Generator, Callable
from .exceptions import InstaVMError, AuthenticationError, SessionError, ExecutionError, NetworkError, RateLimitError
class InstaVM:
    def __init__(self, api_key=None, base_url="https://api.instavm.io", timeout=300, max_retries=0):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        if self.api_key:
            self.start_session()

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic and proper error handling"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                # Handle specific HTTP status codes
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or session expired")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    raise NetworkError(f"Server error: {response.status_code}")

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout as e:
                last_exception = NetworkError(f"Request timeout after {self.timeout}s")
            except requests.exceptions.ConnectionError as e:
                last_exception = NetworkError(f"Connection failed: {str(e)}")
            except (AuthenticationError, RateLimitError) as e:
                # Don't retry these
                raise e
            except requests.exceptions.HTTPError as e:
                if e.response.status_code < 500:
                    # Client errors shouldn't be retried
                    raise InstaVMError(f"HTTP {e.response.status_code}: {e.response.text}")
                last_exception = NetworkError(f"HTTP error: {str(e)}")

            if attempt < self.max_retries:
                # Exponential backoff
                time.sleep(2 ** attempt)

        raise last_exception or NetworkError("Max retries exceeded")

    def start_session(self):
        if not self.api_key:
            raise AuthenticationError("API key not set. Please provide an API key or create one first.")

        url = f"{self.base_url}/session"
        data = {"api_key": self.api_key}

        try:
            response = self._make_request("POST", url, json=data)
            result = response.json()
            self.session_id = result.get("session_id")
            if not self.session_id:
                raise SessionError("Failed to get session ID from server response")
            return self.session_id
        except Exception as e:
            if isinstance(e, (InstaVMError)):
                raise e
            raise SessionError(f"Failed to start session: {str(e)}")

    def execute(self, command: str, language: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/execute"
        data = {
            "command": command,
            "api_key": self.api_key,
            "session_id": self.session_id,
        }

        if language:
            data["language"] = language
        if timeout is not None:
            data["timeout"] = timeout

        try:
            response = self._make_request("POST", url, json=data)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise ExecutionError(f"Failed to execute command: {str(e)}")

    def get_usage(self) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/usage/{self.session_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = self._make_request("GET", url, headers=headers)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise InstaVMError(f"Failed to get usage: {str(e)}")

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/upload/"
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    "api_key": self.api_key,
                    "session_id": self.session_id,
                }
                response = self._make_request("POST", url, data=data, files=files)
            return response.json()
        except FileNotFoundError:
            raise InstaVMError(f"File not found: {file_path}")
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise InstaVMError(f"Failed to upload file: {str(e)}")

    def execute_streaming(self, command: str, on_output: Optional[Callable[[str], None]] = None) -> Generator[str, None, None]:
        """Execute command with real-time streaming output"""
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/execute/stream"
        data = {
            "command": command,
            "api_key": self.api_key,
            "session_id": self.session_id,
        }

        try:
            response = self.session.post(
                url,
                json=data,
                stream=True,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or session expired")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif not response.ok:
                raise ExecutionError(f"Execution failed: {response.text}")

            # Stream the response line by line
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        # Try to parse as JSON for structured output
                        data = json.loads(line)
                        output = data.get('output', data.get('data', str(data)))
                    except json.JSONDecodeError:
                        # Fallback to raw line if not JSON
                        output = line

                    if on_output:
                        on_output(output)
                    yield output

        except requests.exceptions.Timeout:
            raise NetworkError(f"Streaming request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed during streaming: {str(e)}")
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise ExecutionError(f"Streaming execution failed: {str(e)}")

    def close_session(self) -> bool:
        """Properly close the current session"""
        if not self.session_id:
            return True

        url = f"{self.base_url}/session/{self.session_id}"
        try:
            response = self._make_request("DELETE", url)
            self.session_id = None
            return True
        except Exception as e:
            # Log but don't fail - session might already be expired
            print(f"Warning: Failed to close session: {str(e)}. It will auto-expire in a few minutes.")
            self.session_id = None
            return False

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.session_id:
            raise SessionError("No active session")

        url = f"{self.base_url}/session/{self.session_id}"
        try:
            response = self._make_request("GET", url)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise SessionError(f"Failed to get session info: {str(e)}")

    def is_session_active(self) -> bool:
        """Check if current session is still active"""
        try:
            self.get_session_info()
            return True
        except (SessionError, AuthenticationError):
            return False
        except Exception:
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close session"""
        self.close_session()