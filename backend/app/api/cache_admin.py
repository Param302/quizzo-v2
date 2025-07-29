from flask import current_app
from app.utils import admin_required
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.cache import invalidate_user_cache, invalidate_quiz_cache


class CacheStatsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get cache statistics"""
        stats = current_app.cache.get_cache_stats()
        return {"cache_stats": stats}


class CacheClearResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Clear cache entries"""
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True, 
                          choices=['all', 'user', 'quiz', 'admin'],
                          help='Type of cache to clear')
        parser.add_argument('user_id', type=int, help='User ID for user-specific cache clear')
        parser.add_argument('quiz_id', type=int, help='Quiz ID for quiz-specific cache clear')
        args = parser.parse_args()
        
        cleared = 0
        
        if args['type'] == 'all':
            # Clear all cache
            try:
                current_app.cache.redis_client.flushdb()
                cleared = "all"
            except Exception as e:
                return {'message': f'Error clearing cache: {e}'}, 500
        
        elif args['type'] == 'user':
            if args['user_id']:
                cleared = current_app.cache.clear_user_cache(args['user_id'])
            else:
                return {'message': 'user_id required for user cache clear'}, 400
        
        elif args['type'] == 'quiz':
            if args['quiz_id']:
                cleared = current_app.cache.clear_quiz_cache(args['quiz_id'])
            else:
                return {'message': 'quiz_id required for quiz cache clear'}, 400
        
        elif args['type'] == 'admin':
            cleared = current_app.cache.clear_admin_cache()
        
        return {
            'message': f'Cache cleared successfully',
            'type': args['type'],
            'entries_cleared': cleared
        }


def register_cache_api(api):
    api.add_resource(CacheStatsResource, '/admin/cache/stats')
    api.add_resource(CacheClearResource, '/admin/cache/clear')
