from app.models import User, db
from flask import request, current_app
from flask_restful import Resource, reqparse
from app.utils import hash_password, verify_password, get_current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


class RegisterResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'name', type=str, required=True, help='Name is required')
        self.parser.add_argument('username', type=str,
                                 required=True, help='Username is required')
        self.parser.add_argument(
            'email', type=str, required=True, help='Email is required')
        self.parser.add_argument('password', type=str,
                                 required=True, help='Password is required')
        self.parser.add_argument(
            'role', type=str, default='user', choices=['user', 'admin'])

    def post(self):
        args = self.parser.parse_args()

        print(
            f"Registration attempt with email: {args['email']}, username: {args['username']}")

        # Check if user already exists
        if User.query.filter_by(username=args['username']).first():
            print(f"Username {args['username']} already exists")
            return {'message': 'Username already exists'}, 400

        if User.query.filter_by(email=args['email']).first():
            print(f"Email {args['email']} already exists")
            return {'message': 'Email already exists'}, 400

        # Create new user
        hashed_password = hash_password(args['password'])
        print(f"Created hashed password for user")

        user = User(
            name=args['name'],
            username=args['username'],
            email=args['email'],
            password=hashed_password,
            role=args['role']
        )

        db.session.add(user)
        db.session.commit()

        print(f"User {user.email} registered successfully with ID: {user.id}")

        # Schedule email tasks for the new user (daily reminders and monthly reports)
        try:
            # Only schedule for regular users, not admins
            if user.role == 'user':
                # Import here to avoid circular imports
                from app.services.celery_tasks import schedule_user_emails_task
                schedule_user_emails_task.delay(user.id)
                print(f"Email tasks scheduled for user {user.id}")
        except Exception as e:
            # Don't fail registration if email scheduling fails
            print(
                f"Failed to schedule email tasks for user {user.id}: {str(e)}")
            current_app.logger.warning(
                f"Email scheduling failed for user {user.id}: {str(e)}")

        return {
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, 201


class LoginResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str,
                                 required=True, help='Email is required')
        self.parser.add_argument('password', type=str,
                                 required=True, help='Password is required')

    def post(self):
        args = self.parser.parse_args()

        print(f"Login attempt with email: {args['email']}")

        # Find user by email
        user = User.query.filter_by(email=args['email']).first()

        if not user:
            print(f"No user found with email: {args['email']}")
            return {'message': 'Invalid credentials'}, 403

        print(f"User found: {user.email}, checking password...")

        if not verify_password(args['password'], user.password):
            print("Password verification failed")
            return {'message': 'Invalid credentials'}, 403

        print("Login successful, creating token...")

        # Create access token with string identity
        access_token = create_access_token(identity=str(user.id))

        return {
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, 200


class MeResource(Resource):
    @jwt_required()
    def get(self):
        try:
            print("Getting current user info...")
            user_identity = get_jwt_identity()
            print(
                f"JWT identity: {user_identity} (type: {type(user_identity)})")

            user = get_current_user()
            print(f"User from get_current_user(): {user}")

            if not user:
                print("User not found")
                return {'message': 'User not found'}, 404

            print(f"Returning user info for: {user.email}")
            return {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, 200
        except Exception as e:
            print(f"Error in MeResource: {str(e)}")
            return {'message': 'Authentication failed'}, 401


def register_auth_api(api):
    api.add_resource(RegisterResource, '/auth/register')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(MeResource, '/auth/me')
