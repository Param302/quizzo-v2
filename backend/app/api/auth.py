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
        """User registration"""
        args = self.parser.parse_args()

        # Check if user already exists
        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already exists'}, 400

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        # Create new user
        user = User(
            name=args['name'],
            username=args['username'],
            email=args['email'],
            password=hash_password(args['password']),
            role=args['role']
        )

        db.session.add(user)
        db.session.commit()

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
        self.parser.add_argument('username', type=str,
                                 required=True, help='Username is required')
        self.parser.add_argument('password', type=str,
                                 required=True, help='Password is required')

    def post(self):
        """User login - returns JWT token"""
        args = self.parser.parse_args()

        # Find user by username or email
        user = User.query.filter(
            (User.username == args['username']) |
            (User.email == args['username'])
        ).first()

        if not user or not verify_password(args['password'], user.password):
            return {'message': 'Invalid credentials'}, 401

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
        """Get logged-in user's profile"""
        user = get_current_user()

        if not user:
            return {'message': 'User not found'}, 404

        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, 200


def register_auth_api(api):
    api.add_resource(RegisterResource, '/auth/register')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(MeResource, '/auth/me')
