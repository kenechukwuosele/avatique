import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///waitlist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Init DB
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    email = request.form.get('email')
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required.'}), 400

    new_subscriber = Subscriber(email=email)
    
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        print(f"New subscriber: {email}") # Action: Print to console
        return jsonify({'status': 'success', 'message': 'Thanks for joining!'})
    except Exception as e:
        db.session.rollback()
        # Check for unique constraint violation (though generic Exception catches it too)
        if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
             return jsonify({'status': 'error', 'message': 'You are already on the list!'}), 400
        
        # Simpler check for now since SQLAlchemy raises IntegrityError but we want to be safe
        # Ideally we'd import IntegrityError from sqlalchemy.exc
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred (probably already joined).'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
