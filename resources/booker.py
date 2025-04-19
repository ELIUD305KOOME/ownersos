from flask import Blueprint, request, jsonify, redirect
from flask_restful import Api, Resource
from models import db, Service,Booking

# Define Blueprint
clicks_bp = Blueprint('clicks', __name__)
api = Api(clicks_bp)




# Click Tracker for Service Booking
# @limiter.exempt
class ServiceClickResource(Resource):
    def post(self, service_id):
        # Fetch service by ID
        service = Service.query.get_or_404(service_id)
        service.clicks += 1
        db.session.commit()

        # Fetch customer information from the request
        name = request.json.get('name')
        phone = request.json.get('phone')
        message = request.json.get('message')

        # Check if all required fields are provided
        if not name or not phone or not message:
            return jsonify({"error": "Missing required information. Name, phone, and message are required."}), 400

        # Store booking details in the database
        booking = Booking(service_id=service.id, name=name, phone=phone, message=message)
        db.session.add(booking)
        db.session.commit()

        # Construct the WhatsApp URL including the service details and customer information
        whatsapp_url = f"https://wa.me/+254792182559?text=I%20am%20interested%20in%20the%20service%20'{service.name}'%20priced%20at%20{service.price}%0AName:%20{name}%0APhone:%20{phone}%0AMessage:%20{message}"

        return jsonify({"whatsapp_url": whatsapp_url, "message": "Booking details stored successfully."})


# @limiter.exempt
class AllServiceClicksResource(Resource):
    def get(self):
        services = Service.query.all()
        service_clicks = [{"service_id": service.id, "name": service.name, "clicks": service.clicks} for service in services]
        return {"services": service_clicks}, 200



# Add Resources to the API

api.add_resource(ServiceClickResource, '/services/<int:service_id>/clicks')
api.add_resource(AllServiceClicksResource, '/services/clicks')
