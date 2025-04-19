from flask import Blueprint, request, current_app, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
import os
from models import db, Service

# Define Blueprint
services_bp = Blueprint('services', __name__)
api = Api(services_bp)

# Request parsers
service_parser = reqparse.RequestParser()
service_parser.add_argument('name', type=str, required=True, help="Name is required")
service_parser.add_argument('description', type=str)
service_parser.add_argument('price', type=float, required=True, help="Price is required")
service_parser.add_argument('category_name', type=str, required=True, help="Category name is required")
service_parser.add_argument('subcategory_name', type=str, required=True, help="Subcategory name is required")
service_parser.add_argument('service_image', type=str)  # For URL-based images


# Helper function for saving uploaded files
def save_uploaded_file(file, folder='uploads'):
    """
    Saves an uploaded file to the specified folder.
    Returns the file path or raises an exception if saving fails.
    """
    upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', folder))
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    try:
        file.save(file_path)
        return file_path
    except Exception as e:
        raise ValueError(f"Failed to save file: {str(e)}")


class ServiceListResource(Resource):
    def get(self):
        """
        Retrieve a list of all services.
        """
        try:
            services = Service.query.all()
            return [service.to_dict() for service in services], 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def post(self):
        """
        Create a new service.
        """
        args = service_parser.parse_args()
        _uploaded_file = request.files.get('service_image')

        try:
            # Handle file upload
            service_image = save_uploaded_file(_uploaded_file, 'uploads') if _uploaded_file else args.get('service_image')

            # Create new service
            service = Service(
                name=args['name'],
                description=args.get('description'),
                price=args['price'],
                category_name=args['category_name'],
                subcategory_name=args['subcategory_name'],
                service_image=service_image,
            )
            db.session.add(service)
            db.session.commit()
            return service.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Service with this name already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


class ServiceResource(Resource):
    def get(self, id):
        """
        Retrieve a specific service by ID.
        """
        try:
            service = Service.query.get_or_404(id)
            return service.to_dict(), 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing service.
        """
        args = service_parser.parse_args()
        _uploaded_file = request.files.get('service_image')

        try:
            service = Service.query.get_or_404(id)

            # Handle file upload
            service_image = save_uploaded_file(_uploaded_file, 'uploads') if _uploaded_file else args.get('service_image', service.service_image)

            # Update service attributes
            service.name = args['name']
            service.description = args.get('description')
            service.price = args['price']
            service.category_name = args['category_name']
            service.subcategory_name = args['subcategory_name']
            service.service_image = service_image

            db.session.commit()
            return service.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {"error": "Service with this name already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a service by ID.
        """
        try:
            service = Service.query.get_or_404(id)
            db.session.delete(service)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


# Add Resources to the API
api.add_resource(ServiceListResource, '/services')
api.add_resource(ServiceResource, '/services/<int:id>')