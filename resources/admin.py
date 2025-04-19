from flask_jwt_extended import (
    JWTManager, get_jwt, create_access_token,
    jwt_required, create_refresh_token, get_jwt_identity
)
from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, reqparse
from models import Mechanic, db, TokenBlocklist
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mechanic_auth_bp = Blueprint('mechanic_auth_bp', __name__, url_prefix='/mechanic_auth')
mechanic_auth_api = Api(mechanic_auth_bp)

bcrypt = Bcrypt()
jwt = JWTManager()


# JWT user lookup
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return Mechanic.query.filter_by(id=identity).first()


# JWT token blocklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None


# Registration arguments parser
register_args = reqparse.RequestParser()
register_args.add_argument('first_name', type=str, required=True, help='First name is required')
register_args.add_argument('last_name', type=str, required=True, help='Last name is required')
register_args.add_argument('username', type=str, required=True, help='Username is required')
register_args.add_argument('email', type=str, required=True, help='Email is required')
register_args.add_argument('phone_number', type=str, required=True, help='Phone number is required')
register_args.add_argument('expertise', type=str, required=True, help='Expertise is required')
register_args.add_argument('bio', type=str)
register_args.add_argument('password', type=str, required=True, help='Password is required')
register_args.add_argument('password2', type=str, required=True, help='Confirm password is required')

class Register(Resource):
    def post(self):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        if 'profile_picture' not in request.files:
            return {"msg": "No file part"}, 400

        file = request.files['profile_picture']
        
        if file.filename == '':
            return {"msg": "No selected file"}, 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        else:
            return {"msg": "File type not allowed"}, 400

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        expertise = request.form.get('expertise')
        bio = request.form.get('bio')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return {"msg": "Passwords don't match"}, 400
        
        if Mechanic.query.filter_by(username=username).first():
            return {"msg": "Mechanic already exists"}, 400

        if Mechanic.query.filter_by(email=email).first():
            return {"msg": "Email already registered"}, 400
        
        if Mechanic.query.filter_by(phone_number=phone_number).first():
            return {"msg": "Phone Number already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_mechanic = Mechanic(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            profile_picture=filename,
            expertise=expertise,
            bio=bio,
            password=hashed_password
        )

        try:
            db.session.add(new_mechanic)
            db.session.commit()
            return {'msg': "Mechanic registration successful"}, 201
        except Exception as e:
            db.session.rollback()
            return {"msg": "Error creating Mechanic", "error": str(e)}, 500

mechanic_auth_api.add_resource(Register, '/register')


login_args = reqparse.RequestParser()
login_args.add_argument('email', type=str, required=True, help='Email is required')
login_args.add_argument('password', type=str, required=True, help='Password is required')

class Login(Resource):
    def post(self):
        data = login_args.parse_args() 
        mechanic = Mechanic.query.filter_by(email=data.get('email')).first() 

        if not mechanic:
            return make_response({"msg": "Mechanic does not exist"}, 404) 

        if not bcrypt.check_password_hash(mechanic.password, data.get('password')): 
            return make_response({"msg": "Password does not match"}, 401)

        token = create_access_token(identity=mechanic.id)
        refresh_token = create_refresh_token(identity=mechanic.id)

        return make_response({
           "token": token,
           "refresh_token": refresh_token,
           "mechanic_id": mechanic.id,
           "first_name": mechanic.first_name,
           "last_name": mechanic.last_name,
           "profile_picture": mechanic.profile_picture
        }, 200)


    @jwt_required(refresh=True)
    def get(self):
        current_mechanic_id = get_jwt_identity()  
        token = create_access_token(identity=current_mechanic_id)  
        return make_response({"token": token}, 200)

mechanic_auth_api.add_resource(Login, '/login')

# Logout
class Logout(Resource):
    @jwt_required()
    def get(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return jsonify(msg="JWT revoked")
    
mechanic_auth_api.add_resource(Logout, '/logout')



class CurrentMechanic(Resource):
    @jwt_required()
    def get(self):
        current_mechanic_id = get_jwt_identity()
        mechanic = Mechanic.query.get(current_mechanic_id)

        if mechanic is None:
            return make_response({"message": "Mechanic not found"}, 404)

        return make_response({
            "id": mechanic.id,
            "first_name": mechanic.first_name,
            "last_name": mechanic.last_name,
            "email": mechanic.email,
            "profile_picture": mechanic.profile_picture
        }, 200)


mechanic_auth_api.add_resource(CurrentMechanic, '/current-mechanic')