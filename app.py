from flask import Flask, jsonify, send_from_directory, request
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models import db
from resources.services import services_bp
from resources.booking import booking_bp
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from whitenoise import WhiteNoise
import os
from resources.admin import mechanic_auth_bp, jwt, bcrypt
from resources.useradmin import mechanic_bpp
# from openai import OpenAI
import re
from flask import Flask, request, jsonify
from difflib import get_close_matches
import requests

# OpenAI Chatbot-related imports
# from dotenv import load_dotenv
# import openai

# Load and parse FAQ into a dict
def load_knowledge_base():
    with open("data/faq.txt", "r") as f:
        raw = f.read()
    qa_pairs = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", raw, re.DOTALL)
    return {q.strip(): a.strip() for q, a in qa_pairs}

faq_data = load_knowledge_base()


# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the app
CORS(app, origins=['https://finishers.vercel.app', 'http://localhost:3000'])


# Upload folder config
UPLOAD_FOLDER = 'uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://emur_tech_user:pQ6RvnmnfRC66n4E2j04WsEI0Xbtz0jY@dpg-d01ujgvgi27c73f1vog0-a.oregon-postgres.render.com/emur_tech'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
app.config['UPLOAD_FOLDER_AFTER'] = 'uploads/after'
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2000000 per day", "50000 per hour"],
)

# Initialize Flask-Talisman for security headers
talisman = Talisman(app)

# Register Blueprints
app.register_blueprint(services_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(mechanic_auth_bp)
app.register_blueprint(mechanic_bpp)

# Create API instance
api = Api(app)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def hello():
    return jsonify(message="Hello from Flask! Welcome to solo beauty services!")

# News api
@app.route('/api/news')
def get_news():
    try:
        data = {
    'articles': [
        {
            'title': 'AI revolution is here',
            'description': 'AI is taking over the world.',
            'url': 'https://www.youtube.com/watch?v=brQLpTnDwyg',
            'videoUrl': 'https://www.youtube.com/watch?v=brQLpTnDwyg'
        },
        {
            'title': 'New VR headset released',
            'description': 'The latest VR tech has arrived.',
            'url': 'https://www.youtube.com/watch?v=uBB9k5sK8KE',
            'videoUrl': 'https://www.youtube.com/watch?v=uBB9k5sK8KE'
        },
        {
            'title': 'Quantum computing breakthrough',
            'description': 'A new quantum processor is now faster than classical supercomputers.',
            'url': 'https://www.youtube.com/watch?v=B3U1NDUiwSA',
            'videoUrl': 'https://www.youtube.com/watch?v=B3U1NDUiwSA'
        },
        {
            'title': 'Apple unveils M4 chip',
            'description': 'Apple announces their next-generation chip for MacBooks.',
            'url': 'https://www.youtube.com/watch?v=VT5s_sPimhU',
            'videoUrl': 'https://www.youtube.com/watch?v=VT5s_sPimhU'
        },
        {
            'title': 'Tesla launches humanoid robot',
            'description': 'Tesla introduces a home assistant robot powered by AI.',
            'url': 'https://www.youtube.com/watch?v=Mu-eK72ioDk',
            'videoUrl': 'https://www.youtube.com/watch?v=Mu-eK72ioDk'
        },
        {
            'title': 'Google I/O 2025 Recap',
            'description': 'All the big announcements from Google I/O 2025 in one place.',
            'url': 'https://www.youtube.com/watch?v=2OpHbyN4vEM',
            'videoUrl': 'https://www.youtube.com/watch?v=2OpHbyN4vEM'
        },
        {
            'title': 'NVIDIA unveils RTX 5090',
            'description': 'Next-gen graphics card pushes the boundaries of gaming and AI.',
            'url': 'https://www.youtube.com/watch?v=ceIvN7fcoo0',
            'videoUrl': 'https://www.youtube.com/watch?v=ceIvN7fcoo0'
        },
        {
            'title': 'Microsoft launches Copilot+',
            'description': 'Microsoft expands its AI assistant features across all platforms.',
            'url': 'https://www.youtube.com/watch?v=dg2C2Sv4zig',
            'videoUrl': 'https://www.youtube.com/watch?v=dg2C2Sv4zig'
        }
    ]
}

            
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🚀 Chatbot Endpoint (OpenAI)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Try to match user message to the closest FAQ question
        questions = list(faq_data.keys())
        match = get_close_matches(user_message, questions, n=1, cutoff=0.4)

        if match:
            reply = faq_data[match[0]]
        else:
            reply = "Sorry, I couldn't find an answer for that. Try asking something else from our services."

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run locally
if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
