"""Custom exceptions for InstaVM operations"""

class InstaVMError(Exception):
    """Base exception for InstaVM operations"""
    pass

class AuthenticationError(InstaVMError):
    """Authentication failed"""
    pass

class SessionError(InstaVMError):
    """Session-related errors"""
    pass

class ExecutionError(InstaVMError):
    """Code execution failed"""
    pass

class NetworkError(InstaVMError):
    """Network connectivity issues"""
    pass

class RateLimitError(InstaVMError):
    """API rate limit exceeded"""
    pass