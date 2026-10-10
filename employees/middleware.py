from employees.sqlalchemy_db import db_session

class ScopedSessionMiddleware:
    """Remove the thread-scoped SQLAlchemy session after each request."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        try:
            return self.get_response(request)
        finally:
            db_session.remove()
