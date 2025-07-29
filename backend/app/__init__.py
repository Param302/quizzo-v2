from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from app.config import Config
from app.models import db
from app.cache import RedisCache
from app.rate_limiter import create_limiter, apply_rate_limits


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)
    api = Api(app)

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
    from app.api.export import register_export_api
    from app.api.health import register_health_api
    from app.api.cache_admin import register_cache_api
    from app.error_handlers import register_error_handlers

    register_auth_api(api)
    register_admin_api(api)
    register_user_api(api)
    register_quiz_api(api)
    register_public_api(api)
    register_export_api(api)
    register_cache_api(api)
    register_health_api(api)
    register_error_handlers(app)

    apply_rate_limits(app)

    with app.app_context():
        db.create_all()

    return app
