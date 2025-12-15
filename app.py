import os
import csv
from io import StringIO
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///waitlist.db').replace("postgres://", "postgresql://")
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

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/send_emails', methods=['POST'])
def trigger_campaign():
    password = request.form.get('password')
    # Simple security check: match the EMAIL_PASSWORD
    # (In a real app we'd use a separate ADMIN_PASSWORD and hash it, but this is a quick minimal solution)
    correct_password = os.getenv('EMAIL_PASSWORD')
    
    # Fallback for local dev if env not set
    if not correct_password:
         try:
            from avatique.password import password as local_password
            correct_password = local_password
         except:
             pass

    if not correct_password or password != correct_password:
        return render_template('admin.html', error="Invalid Password")

    # Import here to avoid circular dependency (app -> send_campaign -> app)
    from send_campaign import send_campaign
    
    # Run the campaign
    logs = send_campaign()
    
    return render_template('admin.html', logs=logs)

@app.route('/export', methods=['POST'])
def export_subscribers():
    password = request.form.get('password')
    correct_password = os.getenv('EMAIL_PASSWORD')
    
    # Fallback for local dev
    if not correct_password:
         try:
            from avatique.password import password as local_password
            correct_password = local_password
         except:
             pass

    if not correct_password or password != correct_password:
        return render_template('admin.html', error="Invalid Password")

    subscribers = Subscriber.query.all()
    
    # Generate CSV
    def generate():
        data = StringIO()
        w = csv.writer(data)
        w.writerow(('ID', 'Email'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        for sub in subscribers:
            w.writerow((sub.id, sub.email))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # Stream the response
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=subscribers.csv"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
