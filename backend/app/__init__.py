from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from app.config import Config
from app.models import db
from app.cache import RedisCache
from app.rate_limiter import create_limiter, apply_rate_limits
from app.celery_app import make_celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Celery
    app.celery = make_celery(app)

    db.init_app(app)
    CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'])
    jwt = JWTManager(app)
    api = Api(app, prefix='/api')

    # Initialize Redis cache
    redis_cache = RedisCache(app)
    app.cache = redis_cache
    app.logger.info("Using Redis cache")

    # Initialize rate limiter
    limiter = create_limiter(app)
    app.limiter = limiter
    app.logger.info("Rate limiting enabled")

    from app.api.auth import register_auth_api
    from app.api.user import register_user_api
    from app.api.quiz import register_quiz_api
    from app.api.admin import register_admin_api
    from app.api.public import register_public_api
    from app.api.export import register_export_api, register_certificate_routes
    from app.api.health import register_health_api
    from app.api.cache_admin import register_cache_api
    from app.api.email import register_email_api
    from app.api.email_tasks import register_email_tasks_api
    from app.error_handlers import register_error_handlers

    register_auth_api(api)
    register_admin_api(api)
    register_user_api(api)
    register_quiz_api(api)
    register_public_api(api)
    register_export_api(api)
    register_cache_api(api)
    register_health_api(api)
    register_email_api(api)
    register_email_tasks_api(api)
    register_error_handlers(app)

    # Register certificate routes (Flask routes, not API resources)
    register_certificate_routes(app)

    apply_rate_limits(app)

    with app.app_context():
        db.create_all()

    return app
