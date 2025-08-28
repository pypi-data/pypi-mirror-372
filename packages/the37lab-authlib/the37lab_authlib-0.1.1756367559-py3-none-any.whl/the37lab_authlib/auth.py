import inspect
from flask import Blueprint, request, jsonify, current_app, url_for, redirect, g
import jwt
from datetime import datetime, timedelta
from .db import Database
from .models import User, Role, ApiToken
from .exceptions import AuthError
import uuid
import requests
import bcrypt
import logging
import os
from functools import wraps
from isodate import parse_duration

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, app=None, db_dsn=None, jwt_secret=None, oauth_config=None, id_type='integer', environment_prefix=None, api_tokens=None):
        self.user_override = None
        if environment_prefix:
            prefix = environment_prefix.upper() + '_'
            db_dsn = os.getenv(f'{prefix}DATABASE_URL')
            jwt_secret = os.getenv(f'{prefix}JWT_SECRET')
            google_client_id = os.getenv(f'{prefix}GOOGLE_CLIENT_ID')
            google_client_secret = os.getenv(f'{prefix}GOOGLE_CLIENT_SECRET')
            oauth_config = {}
            if google_client_id and google_client_secret:
                oauth_config['google'] = {
                    'client_id': google_client_id,
                    'client_secret': google_client_secret
                }
            api_tokens_env = os.getenv(f'{prefix}API_TOKENS')
            if api_tokens_env:
                api_tokens = {}
                for entry in api_tokens_env.split(','):
                    if ':' in entry:
                        key, user = entry.split(':', 1)
                        api_tokens[key.strip()] = user.strip()
            user_override_env = os.getenv(f'{prefix}USER_OVERRIDE')
            if user_override_env:
                self.user_override = user_override_env
        else:
            prefix = ''
            
        self.expiry_time = parse_duration(os.getenv(f'{prefix}JWT_TOKEN_EXPIRY_TIME', 'PT1H'))
        if self.user_override and (api_tokens or db_dsn):
            raise ValueError('Cannot set user_override together with api_tokens or db_dsn')
        if api_tokens and db_dsn:
            raise ValueError('Cannot set both api_tokens and db_dsn')
        self.api_tokens = api_tokens or None
        self.db = Database(db_dsn, id_type=id_type) if db_dsn else None
        self.jwt_secret = jwt_secret
        self.oauth_config = oauth_config or {}
        self.public_endpoints = {
            'auth.login',
            'auth.oauth_login',
            'auth.oauth_callback',
            'auth.refresh_token',
            'auth.register',
            'auth.get_roles'
        }
        self.bp = None
        
        if app:
            self.init_app(app)

    def _extract_token_from_header(self):
        auth = request.authorization
        if not auth or not auth.token:
            raise AuthError('No authorization header or token', 401)

        if auth.type.lower() != 'bearer':
            raise AuthError('Invalid authorization scheme', 401)

        return auth.token

    def get_redirect_uri(self):
        redirect_uri = os.getenv('REDIRECT_URL') or url_for('auth.oauth_callback', _external=True).replace("http://", "https://")
        logger.info(f"REDIRECT URI..: {redirect_uri}")
        return redirect_uri

    def _validate_api_token(self, api_token):
        if self.api_tokens is not None:
            username = self.api_tokens.get(api_token)
            if not username:
                raise AuthError('Invalid API token')
            # Return a minimal user dict
            return {
                'id': username,
                'username': username,
                'email': '',
                'real_name': username,
                'roles': []
            }
        try:
            parsed = ApiToken.parse_token(api_token)
            with self.db.get_cursor() as cur:
                # First get the API token record
                cur.execute("""
                    SELECT t.*, u.* FROM api_tokens t
                    JOIN users u ON t.user_id = u.id
                    WHERE t.id = %s
                """, (parsed['id'],))
                result = cur.fetchone()
                if not result:
                    raise AuthError('Invalid API token')

                # Verify the nonce
                if not bcrypt.checkpw(parsed['nonce'].encode('utf-8'), result['token'].encode('utf-8')):
                    raise AuthError('Invalid API token')

                # Check if token is expired
                if result['expires_at'] and result['expires_at'] < datetime.utcnow():
                    raise AuthError('API token has expired')

                # Update last used timestamp
                cur.execute("""
                    UPDATE api_tokens 
                    SET last_used_at = %s
                    WHERE id = %s
                """, (datetime.utcnow(), parsed['id']))

                # Fetch roles
                cur.execute("""
                    SELECT r.name FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    WHERE ur.user_id = %s
                """, (result['user_id'],))
                roles = [row['name'] for row in cur.fetchall()]

                # Construct user object
                return {
                    'id': result['user_id'],
                    'username': result['username'],
                    'email': result['email'],
                    'real_name': result['real_name'],
                    'roles': roles
                }
        except ValueError:
            raise AuthError('Invalid token format')

    def _authenticate_request(self):
        if self.user_override:
            return {
                'id': self.user_override,
                'username': self.user_override,
                'email': '',
                'real_name': self.user_override,
                'roles': []
            }
        auth_header = request.headers.get('Authorization')
        api_token = request.headers.get('X-API-Token')

        if auth_header and auth_header.startswith('Bearer '):
            # JWT authentication
            token = self._extract_token_from_header()
            return self.validate_token(token)
        elif api_token:
            # API token authentication
            return self._validate_api_token(api_token)
        else:
            raise AuthError('No authentication provided', 401)

    def require_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = self._authenticate_request()
            sig = inspect.signature(f)
            if 'requesting_user' in sig.parameters:
                kwargs['requesting_user'] = user

            return f(*args, **kwargs)
        return decorated

    def add_public_endpoint(self, endpoint):
        """Mark an endpoint as public so it bypasses authentication."""
        self.public_endpoints.add(endpoint)

    def public_endpoint(self, f):
        """Decorator to mark a view function as public."""
        # Always register the bare function name so application level routes
        # are exempt from authentication checks.
        self.add_public_endpoint(f.__name__)

        # If a blueprint is active, also register the blueprint-prefixed name
        # used by Flask for endpoint identification.
        if self.bp:
            endpoint = f"{self.bp.name}.{f.__name__}"
            self.add_public_endpoint(endpoint)
        return f
    
    def init_app(self, app):
        app.auth_manager = self
        app.register_blueprint(self.create_blueprint())
        @app.errorhandler(AuthError)
        def handle_auth_error(e):
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response

    def create_blueprint(self):
        bp = Blueprint('auth', __name__, url_prefix='/api/v1/users')
        self.bp = bp
        bp.public_endpoint = self.public_endpoint

        @bp.errorhandler(AuthError)
        def handle_auth_error(err):
            response = jsonify(err.to_dict())
            response.status_code = err.status_code
            return response

        @bp.before_request
        def load_user():
            if request.method == 'OPTIONS':
                return  # Skip authentication for OPTIONS
            if request.endpoint not in self.public_endpoints:
                g.requesting_user = self._authenticate_request()

        @bp.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                raise AuthError('Username and password required', 400)
            
            with self.db.get_cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                
                if not user or not self._verify_password(password, user['password_hash']):
                    raise AuthError('Invalid username or password', 401)
                
                # Fetch roles
                cur.execute("""
                    SELECT r.name FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    WHERE ur.user_id = %s
                """, (user['id'],))
                roles = [row['name'] for row in cur.fetchall()]
                user['roles'] = roles
                
                token = self._create_token(user)
                refresh_token = self._create_refresh_token(user)
                
                return jsonify({
                    'token': token,
                    'refresh_token': refresh_token,
                    'user': user
                })

        @bp.route('/login/oauth', methods=['POST'])
        def oauth_login():
            provider = request.json.get('provider')
            if provider not in self.oauth_config:
                raise AuthError('Invalid OAuth provider', 400)

            redirect_uri = self.get_redirect_uri()
            return jsonify({
                'redirect_url': self._get_oauth_url(provider, redirect_uri)
            })

        @bp.route('/login/oauth2callback')
        def oauth_callback():
            code = request.args.get('code')
            provider = request.args.get('state')
            
            if not code or not provider:
                raise AuthError('Invalid OAuth callback', 400)

            user_info = self._get_oauth_user_info(provider, code)
            token = self._create_token(user_info)
            refresh_token = self._create_refresh_token(user_info)
            
            # Redirect to frontend with tokens
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            return redirect(f"{frontend_url}/oauth-callback?token={token}&refresh_token={refresh_token}")

        @bp.route('/login/profile')
        def profile():
            user = g.requesting_user
            return jsonify(user)

        @bp.route('/api-tokens', methods=['GET'])
        def get_tokens():
            tokens = self.get_user_api_tokens(g.requesting_user['id'])
            return jsonify(tokens)

        @bp.route('/api-tokens', methods=['POST'])
        def create_token():
            name = request.json.get('name')
            expires_in_days = request.json.get('expires_in_days')
            if not name:
                raise AuthError('Token name is required', 400)
            api_token = self.create_api_token(g.requesting_user['id'], name, expires_in_days)
            return jsonify({
                'id': api_token.id,
                'name': api_token.name,
                'token': api_token.get_full_token(),
                'created_at': api_token.created_at,
                'expires_at': api_token.expires_at
            })

        @bp.route('/token-refresh', methods=['POST'])
        def refresh_token():
            refresh_token = request.json.get('refresh_token')
            if not refresh_token:
                raise AuthError('No refresh token provided', 400)

            try:
                payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=['HS256'])
                user_id = payload['sub']
                
                with self.db.get_cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    user = cur.fetchone()

                if not user:
                    raise AuthError('User not found', 404)

                return jsonify({
                    'token': self._create_token(user),
                    'refresh_token': self._create_refresh_token(user)
                })
            except jwt.InvalidTokenError:
                raise AuthError('Invalid refresh token', 401)

        @bp.route('/api-tokens', methods=['POST'])
        def create_api_token():
            name = request.json.get('name')
            if not name:
                raise AuthError('Token name required', 400)

            token = self.create_api_token(g.requesting_user['id'], name)
            return jsonify({'token': token.token})

        @bp.route('/api-tokens/validate', methods=['GET'])
        def validate_api_token():
            token = request.json.get('token')
            if not token:
                raise AuthError('No API token provided', 401)
            token = ApiToken.parse_token_id(token)

            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT * FROM api_tokens 
                    WHERE user_id = %s AND id = %s
                """, (g.requesting_user['id'], token))
                api_token = cur.fetchone()

            if not api_token:
                raise AuthError('Invalid API token', 401)

            # Check if token is expired
            if api_token['expires_at'] and api_token['expires_at'] < datetime.utcnow():
                raise AuthError('API token has expired', 401)

            # Update last used timestamp
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE api_tokens 
                    SET last_used_at = %s
                    WHERE id = %s
                """, (datetime.utcnow(), api_token['id']))

            return jsonify({'valid': True})

        @bp.route('/api-tokens', methods=['DELETE'])
        def delete_api_token():
            token = request.json.get('token')
            if not token:
                raise AuthError('Token required', 400)
            token = ApiToken.parse_token_id(token)

            with self.db.get_cursor() as cur:
                cur.execute("""
                    DELETE FROM api_tokens 
                    WHERE user_id = %s AND id = %s
                    RETURNING id
                """, (g.requesting_user['id'], token))
                deleted_id = cur.fetchone()
                if not deleted_id:
                    raise ValueError('Token not found or already deleted')

            return jsonify({'deleted': True})

        @bp.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            
            # Hash the password
            password = data.get('password')
            if not password:
                raise AuthError('Password is required', 400)
            
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            user = User(
                username=data['username'],
                email=data['email'],
                real_name=data['real_name'],
                roles=data.get('roles', []),
                id_generator=self.db.get_id_generator()
            )

            with self.db.get_cursor() as cur:
                if user.id is None:
                    cur.execute("""
                        INSERT INTO users (username, email, real_name, password_hash, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user.username, user.email, user.real_name, password_hash.decode('utf-8'),
                          user.created_at, user.updated_at))
                    user.id = cur.fetchone()['id']
                else:
                    cur.execute("""
                        INSERT INTO users (id, username, email, real_name, password_hash, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user.id, user.username, user.email, user.real_name, password_hash.decode('utf-8'),
                          user.created_at, user.updated_at))

            return jsonify({'id': user.id}), 201

        @bp.route('/roles', methods=['GET'])
        def get_roles():
            with self.db.get_cursor() as cur:
                cur.execute("SELECT * FROM roles")
                roles = cur.fetchall()
            return jsonify(roles)

        return bp

    def validate_token(self, token):
        try:
            logger.debug(f"Validating token: {token}")
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            logger.debug(f"Token payload: {payload}")
            user_id = int(payload['sub'])  # Convert string ID back to integer
            
            with self.db.get_cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if not user:
                    logger.error(f"User not found for ID: {user_id}")
                    raise AuthError('User not found', 404)
                # Fetch roles
                cur.execute("""
                    SELECT r.name FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    WHERE ur.user_id = %s
                """, (user_id,))
                roles = [row['name'] for row in cur.fetchall()]
                user['roles'] = roles

            return user
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {str(e)}")
            raise AuthError('Invalid token', 401)
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            raise AuthError(str(e), 500)

    def get_current_user(self):
        return self._authenticate_request()

    def get_user_api_tokens(self, user_id):
        """Get all API tokens for a user."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT id, name, created_at, expires_at, last_used_at
                FROM api_tokens 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            return cur.fetchall()

    def create_api_token(self, user_id, name, expires_in_days=None):
        """Create a new API token for a user."""
        token = ApiToken(user_id, name, expires_in_days)
        
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO api_tokens (id, user_id, name, token, created_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (token.id, token.user_id, token.name, token.token, token.created_at, token.expires_at))
            return token

    def _create_token(self, user):
        payload = {
            'sub': str(user['id']),
            'exp': datetime.utcnow() + self.expiry_time,
            'iat': datetime.utcnow()
        }
        logger.debug(f"Creating token with payload: {payload}")
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        logger.info(f"Created token: {token}")
        return token

    def _create_refresh_token(self, user):
        payload = {
            'sub': str(user['id']),
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def _verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def _get_oauth_url(self, provider, redirect_uri):
        if provider == 'google':
            client_id = self.oauth_config['google']['client_id']
            scope = 'openid email profile'
            state = provider  # Pass provider as state for callback
            return f'https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}'
        raise AuthError('Invalid OAuth provider')

    def _get_oauth_user_info(self, provider, code):
        if provider == 'google':
            client_id = self.oauth_config['google']['client_id']
            client_secret = self.oauth_config['google']['client_secret']
            redirect_uri = self.get_redirect_uri()

            # Exchange code for tokens
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            token_response = requests.post(token_url, data=token_data)
            logger.info("TOKEN RESPONSE: {} {} {} [[[{}]]]".format(token_response.text, token_response.status_code, token_response.headers, token_data))
            token_response.raise_for_status()
            tokens = token_response.json()

            # Get user info
            userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
            userinfo_response = requests.get(
                userinfo_url,
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()

            # Create or update user
            with self.db.get_cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (userinfo['email'],))
                user = cur.fetchone()

                if not user:
                    # Create new user
                    user = User(
                        username=userinfo['email'],
                        email=userinfo['email'],
                        real_name=userinfo.get('name', userinfo['email']),
                        id_generator=self.db.get_id_generator()
                    )
                    cur.execute("""
                        INSERT INTO users (username, email, real_name, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user.username, user.email, user.real_name, 
                          user.created_at, user.updated_at))
                    user.id = cur.fetchone()['id']
                    user = {'id': user.id, 'username': user.username, 'email': user.email, 
                           'real_name': user.real_name, 'roles': []}
                else:
                    # Update existing user
                    cur.execute("""
                        UPDATE users 
                        SET real_name = %s, updated_at = %s
                        WHERE email = %s
                    """, (userinfo.get('name', userinfo['email']), datetime.utcnow(), userinfo['email']))
                    user['real_name'] = userinfo.get('name', userinfo['email'])

            return user
        raise AuthError('Invalid OAuth provider') 