from sqlalchemy import Column, String, Integer, Float, Text, MetaData, DateTime
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# MetaData for naming conventions
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)

class Mechanic(db.Model, SerializerMixin):
    __tablename__ = 'mechanics'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(10), nullable=False, unique=True)
    profile_picture = Column(Text, nullable=True)  # renamed for consistency
    expertise = Column(String(300), nullable=False)
    bio = Column(Text)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=db.func.current_timestamp())
    updated_at = Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    serialize_rules = ('-password_hash',)

    # Set hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')

    # Verify password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Dictionary output
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "profile_picture": self.profile_picture,
            "expertise": self.expertise,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Mechanic(id={self.id}, username={self.username}, email={self.email})>"

# class Admin(db.Model, SerializerMixin):
#     __tablename__ = 'admins'

#     id = db.Column(Integer, primary_key=True)
#     name = db.Column(String(100), nullable=False, unique=True)
#     email = db.Column(String(120), unique=True, nullable=False)
#     password_hash = db.Column(String(255), nullable=False)
#     profile_image = db.Column(Text, nullable=True)
#     serialize_rules = ('-password_hash',)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password, method='sha256')

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f"<Admin(id={self.id}, name={self.name}, email={self.email}, profile_image={self.profile_image})>"

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             'profile_image': self._image,
#         }


class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)
    description = db.Column(String(500), nullable=True)
    price = db.Column(Float, nullable=False)
    category_name = db.Column(String(100), nullable=False)
    subcategory_name = db.Column(String(100), nullable=False)
    service_image = db.Column(Text, nullable=True)
    clicks = db.Column(Integer, default=0)

    serialize_rules = ('-clicks',)

    def __repr__(self):
        return f"<Service(id={self.id}, name={self.name}, price={self.price}, category={self.category_name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_name': self.category_name,
            'subcategory_name': self.subcategory_name,
            'service_image': self.service_image,
            'clicks': self.clicks,
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(Integer, primary_key=True)
    service_id = db.Column(Integer, db.ForeignKey('services.id'), nullable=True)
    name = db.Column(String(255), nullable=True)
    email = db.Column(String(255), nullable=True)
    phone = db.Column(String(20), nullable=True)
    message = db.Column(Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    meeting_date = db.Column(String(25), nullable=True)
    meeting_link = db.Column(String(255), nullable=True)
    status = db.Column(String(255), nullable=True)
    payment_status = db.Column(String(50), nullable=True)
    payment_method = db.Column(String(50), nullable=True)
    amount_paid = db.Column(String(255), nullable=True)
    notes = db.Column(Text, nullable=True)

    # Relationship
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'meeting_date': self.meeting_date,
            'meeting_link': self.meeting_link,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'amount_paid': self.amount_paid,
            'notes': self.notes,
            
        }

    def __repr__(self):
        return (
            f"<Booking(id={self.id}, service_id={self.service_id}, name={self.name}, "
            f"email={self.email}, phone={self.phone}, meeting_date={self.meeting_date}, "
            f"status={self.status}, amount_paid={self.amount_paid})>"
        )


class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
