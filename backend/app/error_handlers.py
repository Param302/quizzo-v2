from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server due to malformed syntax.',
            'status_code': 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.',
            'status_code': 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status_code': 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource could not be found on this server.',
            'status_code': 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL.',
            'status_code': 405
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.',
            'status_code': 500
        }), 500

    @app.errorhandler(501)
    def not_implemented(error):
        return jsonify({
            'error': 'Not Implemented',
            'message': 'The server does not support the functionality required to fulfill the request.',
            'status_code': 501
        }), 501

    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The server is currently unable to handle the request due to maintenance or capacity problems.',
            'status_code': 503
        }), 503


    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.error(f"Unhandled exception: {str(error)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500
