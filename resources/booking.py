from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import db, Service, Booking
from datetime import datetime

# Define Blueprint for Booking
booking_bp = Blueprint('booking', __name__)
api = Api(booking_bp)

# Initialize the request parsers
service_booking_parser = reqparse.RequestParser()

# Add arguments for service booking
service_booking_parser.add_argument('service_id', type=int, required=True, help="Service ID is required")
service_booking_parser.add_argument('name', type=str, required=True, help="Name is required")
service_booking_parser.add_argument('email', type=str)
service_booking_parser.add_argument('phone', type=str, required=True, help="Phone number is required")
service_booking_parser.add_argument('message', type=str)
service_booking_parser.add_argument('meeting_date', type=str)  # Appointment date
service_booking_parser.add_argument('meeting_link', type=str)
service_booking_parser.add_argument('status', type=str, choices=['pending', 'confirmed', 'cancelled'], default='pending')
service_booking_parser.add_argument('payment_status', type=str)
service_booking_parser.add_argument('payment_method', type=str)
service_booking_parser.add_argument('amount_paid', type=float)
service_booking_parser.add_argument('notes', type=str)


class ServiceBookingsResource(Resource):
    def get(self):
        """
        Retrieve all bookings with associated service names.
        """
        try:
            # Query Booking records where service_id is not None
            bookings = Booking.query.filter(Booking.service_id.isnot(None)).all()

            # Fetch service names for all relevant service IDs
            service_ids = {booking.service_id for booking in bookings if isinstance(booking.service_id, int)}
            services = Service.query.filter(Service.id.in_(service_ids)).all()
            service_dict = {service.id: service.name for service in services}

            # Format the booking data as a list of dictionaries
            formatted_bookings = []
            for booking in bookings:
                service_name = service_dict.get(booking.service_id, "Unknown Service") if isinstance(booking.service_id, int) else "Unknown Service"

                formatted_bookings.append({
                    "id": booking.id,
                    "service_id": booking.service_id,
                    "service_name": service_name,
                    "name": booking.name,
                    "email": booking.email,
                    "phone": booking.phone,
                    "message": booking.message,
                    "timestamp": booking.timestamp.strftime('%Y-%m-%d %H:%M:%S') if booking.timestamp else None,
                    "updated_at": booking.updated_at.strftime('%Y-%m-%d %H:%M:%S') if booking.updated_at else None,
                    "meeting_date": booking.meeting_date,
                    "meeting_link": booking.meeting_link,
                    "status": booking.status,
                    "payment_status": booking.payment_status,
                    "payment_method": booking.payment_method,
                    "amount_paid": booking.amount_paid,
                    "notes": booking.notes,
                })

            return {"service_bookings": formatted_bookings}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def post(self):
        """
        Create a new booking.
        """
        try:
            # Parse and validate request data
            args = service_booking_parser.parse_args()

            # Create a new Booking record
            booking = Booking(
                service_id=args['service_id'],
                name=args['name'],
                email=args.get('email'),
                phone=args['phone'],
                message=args.get('message'),
                meeting_date=args.get('meeting_date'),
                meeting_link=args.get('meeting_link'),
                status=args['status'],
                payment_status=args.get('payment_status'),
                payment_method=args.get('payment_method'),
                amount_paid=args.get('amount_paid'),
                notes=args.get('notes'),
                timestamp=datetime.utcnow(),
            )

            # Add the new booking to the database session
            db.session.add(booking)
            db.session.commit()

            return {"message": "Booking created successfully", "booking_id": booking.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Invalid service ID or duplicate booking."}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


class ServiceBookingDeleteResource(Resource):
    def delete(self, booking_id):
        """
        Delete a specific booking by ID.
        """
        try:
            # Retrieve the booking by ID
            booking = Booking.query.get_or_404(booking_id)

            # Delete the booking
            db.session.delete(booking)
            db.session.commit()

            return {"message": "Booking deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500

    def put(self, booking_id):
        """
        Update a specific booking by ID.
        """
        try:
            # Retrieve the booking by ID
            booking = Booking.query.get_or_404(booking_id)

            # Parse and validate request data
            data = request.get_json()

            # Update fields if provided
            if 'meeting_date' in data:
                booking.meeting_date = data['meeting_date']
            if 'meeting_link' in data:
                booking.meeting_link = data['meeting_link']
            if 'status' in data:
                booking.status = data['status']
            if 'payment_status' in data:
                booking.payment_status = data['payment_status']
            if 'payment_method' in data:
                booking.payment_method = data['payment_method']
            if 'amount_paid' in data:
                booking.amount_paid = data['amount_paid']
            if 'notes' in data:
                booking.notes = data['notes']

            # Commit changes to the database
            db.session.commit()

            return {"message": "Booking updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


# Add Resources to the API
api.add_resource(ServiceBookingsResource, '/services/bookings', endpoint='service_bookings')
api.add_resource(ServiceBookingDeleteResource, '/services/bookings/<int:booking_id>', endpoint='delete_service_booking')
