import smtplib
import ssl
import os
from email.message import EmailMessage
from dotenv import load_dotenv
from app import app, db, Subscriber

# Load environment variables
load_dotenv()

# -------------------------
# Configuration
# -------------------------
DATABASE = 'waitlist.db' # Keeping for legacy reference if needed, but not used for query
EMAIL_SENDER = "favzieokon@gmail.com"
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

if not EMAIL_PASSWORD:
    # Fallback to local file if env var not set (for backward compatibility during dev)
    try:
        from avatique.password import password as EMAIL_PASSWORD
    except ImportError:
        print("Warning: EMAIL_PASSWORD not in env and 'avatique/password.py' not found.")


SUBJECT = "Your Early Access to Avatique is Here 🚀"
# You can customize this body content
BODY = """Hi there,

Avatique is live! You asked to be notified, and here we are.

Click the link below to verify your spot:

Link: https://avatique.com

Thank you for your patience!
"""

def get_subscribers():
    try:
        with app.app_context():
            subscribers = Subscriber.query.all()
            return [s.email for s in subscribers]
    except Exception as e:
        print(f"Error reading database: {e}")
        return []

def send_campaign():
    logs = []
    receivers = get_subscribers()
    
    if not receivers:
        logs.append("No subscribers found in database.")
        return logs

    logs.append(f"Found {len(receivers)} subscribers. Starting email campaign...")

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            
            for email_receiver in receivers:
                try:
                    msg = EmailMessage()
                    msg['From'] = EMAIL_SENDER
                    msg['To'] = email_receiver
                    msg['Subject'] = SUBJECT
                    msg.set_content(BODY)
                    
                    smtp.send_message(msg)
                    logs.append(f"✅ Sent to: {email_receiver}")
                    print(f"✅ Sent to: {email_receiver}")
                except Exception as e:
                    logs.append(f"❌ Failed to send to {email_receiver}: {e}")
                    print(f"❌ Failed to send to {email_receiver}: {e}")
                    
        logs.append("Campaign finished!")
        
    except smtplib.SMTPAuthenticationError:
        logs.append("Authentication Failed. Please check your email and app password.")
    except Exception as e:
        logs.append(f"An error occurred: {e}")
    
    return logs

if __name__ == '__main__':
    confirmation = input(f"You are about to send emails to {len(get_subscribers())} people. Type 'YES' to proceed: ")
    if confirmation == 'YES':
        results = send_campaign()
        for line in results:
            print(line)
    else:
        print("Campaign cancelled.")
