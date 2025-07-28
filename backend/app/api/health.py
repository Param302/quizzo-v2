from app.models import db
from flask import current_app
from flask_restful import Resource


class HealthCheckResource(Resource):
    def get(self):
        """Health check endpoint"""
        health_status = {
            "status": "healthy",
            "service": "Quizzo API",
            "version": "1.0.0",
            "components": {}
        }
        
        # Check database connection
        try:
            db.session.execute("SELECT 1")
            health_status["components"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Check Redis cache
        try:
            current_app.cache.redis_client.ping()
            health_status["components"]["redis_cache"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["redis_cache"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            # Cache failure is not critical for basic operations
        
        # Determine overall status
        if any(comp.get("status") == "unhealthy" for comp in health_status["components"].values()):
            health_status["status"] = "degraded"
        
        status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
        return health_status, status_code


def register_health_routes(api):
    """Register health check routes"""
    api.add_resource(HealthCheckResource, '/health')
