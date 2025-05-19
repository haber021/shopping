from django.utils import timezone
import threading

# Thread local storage
_thread_locals = threading.local()

def get_current_user():
    """Returns the current user or None if not available"""
    return getattr(_thread_locals, 'user', None)

class ActiveUserMiddleware:
    """
    Middleware to make the current user available throughout the application
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store user in thread local storage
        _thread_locals.user = request.user if request.user.is_authenticated else None
        
        # Update last activity time for authenticated users
        if request.user.is_authenticated:
            request.user.last_login = timezone.now()
            request.user.save(update_fields=['last_login'])
        
        response = self.get_response(request)
        
        # Clean up thread local storage
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        
        return response
