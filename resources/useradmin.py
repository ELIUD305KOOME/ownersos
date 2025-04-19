from flask import Blueprint, make_response, request
from flask_restful import Api, Resource
from models import db, Mechanic
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os


UPLOAD_FOLDER = 'uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


mechanic_bpp = Blueprint('mechanic_bp', __name__, url_prefix='/mechanics')
mechanic_api = Api(mechanic_bpp)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



class Mechanics(Resource):
    def get(self):
        search_query = request.args.get('search', '').lower()
        if search_query:
            mechanics = Mechanic.query.filter(
                (Mechanic.username.ilike(f"%{search_query}%")) |
                (Mechanic.email.ilike(f"%{search_query}%")) |
                (Mechanic.first_name.ilike(f"%{search_query}%")) |
                (Mechanic.last_name.ilike(f"%{search_query}%"))
            ).all()
        else:
            mechanics = Mechanic.query.all()
            
        mechanic_list = [mechanic.to_dict() for mechanic in mechanics]
        for mechanic in mechanic_list:
            if mechanic.get('profile_picture'):
                mechanic['profile_picture'] = f"http://127.0.0.1:5000/uploads/{mechanic['profile_picture']}"
        
        return make_response(mechanic_list, 200)
    
    def post(self):
        data = request.form.to_dict()
        file = request.files.get('profile_picture')

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username= data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        location = data.get('location')
        expertise = data.get('expertise')
        bio = data.get('bio')
        password = data.get('password')


        if not file:
            return {"message": "Profile picture is required"}, 400
        
        if file.filename == '':
            return {"message": "No selected file"}, 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        else:
            return {"message": "File type not allowed"}, 400
        

        if not all([first_name, last_name, email, username, phone_number, location, expertise, password]):
            return {"message": "Missing required fields"}, 400
        
        if Mechanic.query.filter_by(username=username).first():
            return {"message": "username already exists"}, 400
        
        if Mechanic.query.filter_by(email=email).first():
            return {"message": "Email already registered"}, 400
        
        if Mechanic.query.filter_by(phone_number=phone_number).first():
            return {"message": "Phone number already exists"}, 400

        hashed_password = generate_password_hash(password)

        new_mechanic = Mechanic(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            phone_number=phone_number,
            profile_picture=filename,
            expertise=expertise,
            bio=bio,
            password=hashed_password
        )

        try:
            db.session.add(new_mechanic)
            db.session.commit()
            mechanic_dict = new_mechanic.to_dict()
            mechanic_dict['profile_picture'] = f"http://127.0.0.1:5000/uploads/{mechanic_dict['profile_picture']}"
            response = make_response(mechanic_dict, 201)
            return response
        
        except Exception as e:
            db.session.rollback()
            return {"message": "Error creating Mechanic", "error": str(e)}, 500

mechanic_api.add_resource(Mechanics, '/', strict_slashes=False)



class MechanicById(Resource):
    def get(self, id):
        mechanic = Mechanic.query.filter(Mechanic.id == id).first()

        if not mechanic:
            return {"message": "Mechanic not found"}, 404
        
        mechanic_dict = mechanic.to_dict()
        if mechanic_dict['profile_picture']:
            mechanic_dict['profile_picture'] = f"http://127.0.0.1:5000/uploads/{mechanic_dict['profile_picture']}"
        return mechanic_dict, 200
    
    def patch(self, id):

        mechanic = Mechanic.query.get(id)
        if not mechanic:
            return {"message": "Mechanic not found"}, 404

        data = request.form.to_dict()

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                data['profile_picture'] = filename

        for key, value in data.items():
            setattr(mechanic, key, value)
        
        try:
            db.session.commit()
            mechanic_dict = mechanic.to_dict()
            if mechanic_dict['profile_picture']:
                mechanic_dict['profile_picture'] = f"http://127.0.0.1:5000/uploads/{mechanic_dict['profile_picture']}"
            return mechanic_dict, 200
        
        except Exception as e:
            db.session.rollback()
            return {"message": "Error updating Mechanic", "error": str(e)}, 500



    def delete(self, id):
        mechanic = Mechanic.query.filter_by(id=id).first()

        if not mechanic:
            return {"message": "Mechanic not found"}, 404
        
        try:
            db.session.delete(mechanic)
            db.session.commit()
            return {}, 204
        
        except Exception as e:
            db.session.rollback()
            return {"message": "Error deleting Mechanic", "error": str(e)}, 500

mechanic_api.add_resource(MechanicById, '/<int:id>')