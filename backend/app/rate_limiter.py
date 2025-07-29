from flask import request
from flask_limiter import Limiter
from flask_jwt_extended import get_jwt_identity
from flask_limiter.util import get_remote_address


def get_rate_limit_key():
    try:
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except:
        pass

    return get_remote_address()


def create_limiter(app):
    """Create and configure the Flask-Limiter."""
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL'),
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '100 per hour')],
        enabled=app.config.get('RATELIMIT_ENABLED', True)
    )

    @limiter.request_filter
    def rate_limit_filter():  # to skip rate limiting for certain endpoints
        if request.endpoint == 'health':
            return True
        return False

    return limiter


RATE_LIMITS = {
    'auth': {
        'login': '5 per minute',        # strict auth operations
        'register': '5 per minute',     # strict auth operations
        'refresh': '10 per minute',     # auth operations
        'me': '60 per minute'           # api operations
    },
    'api': {
        'default': '60 per minute',     # standard API operations
        'search': '30 per minute',      # search operations
        'upload': '10 per minute',      # file upload operations
        'quiz_submit': '20 per minute'  # quiz submission operations
    },
    'public': {
        'default': '30 per minute',     # public access
        'quiz_access': '20 per minute'  # quiz access operations
    },
    'admin': {
        'default': '100 per minute',    # admin operations
        'bulk_operations': '20 per minute'  # bulk operations
    }
}


def apply_rate_limits(app):
    if not hasattr(app, 'limiter') or not app.limiter:
        return

    from app.api.auth import RegisterResource, LoginResource, MeResource
    from app.api.public import PublicProfileResource
    app.limiter.limit("5 per minute")(RegisterResource.post)
    app.limiter.limit("5 per minute")(LoginResource.post)
    app.limiter.limit("60 per minute")(MeResource.get)
    app.limiter.limit("30 per minute")(PublicProfileResource.get)


def get_rate_limit_for_endpoint(endpoint_type, operation='default'):
    return RATE_LIMITS.get(endpoint_type, {}).get(operation, '60 per minute')
