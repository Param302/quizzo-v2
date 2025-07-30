import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "I-wont-tell-you-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Redis Cache configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = "quizzo:"

    # JWT configuration
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days
    JWT_IDENTITY_CLAIM = "sub"

    # Rate Limiting configuration
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")
    # Increased default limit for better admin experience
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_ENABLED = True

    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_EMAIL = os.getenv("MAIL_EMAIL", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "noreply@quizzo.com")
    MAIL_SENDER_NAME = os.getenv("MAIL_SENDER_NAME", "Quizzo Team")

    # Certificate configuration
    CERTIFICATE_OUTPUT_DIR = os.getenv(
        "CERTIFICATE_OUTPUT_DIR", "/tmp/certificates")

    # Frontend URLs
    FRONTEND_DASHBOARD_URL = os.getenv(
        "FRONTEND_DASHBOARD_URL", "http://localhost:3000/dashboard")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
