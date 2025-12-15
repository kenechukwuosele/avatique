import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.message import EmailMessage
import ssl
import smtplib
from avatique.password import password

# -------------------------
# 1. Google Sheets Setup
# -------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("C:/Users/Alex/Music/python Projects/.venv/avatique/waitlissst.json", scope)
client = gspread.authorize(creds)

# Open the sheet and tab
sheet = client.open("Waitlist").worksheet("Form Responses 1")

# Get all emails from column B, skip header
emails = sheet.col_values(2)[1:]
print(f"Found {len(emails)} emails.")

# -------------------------
# 2. Email Setup
# -------------------------
# Sender info (use her app password for security)
email_sender = "oselekenny@gmail.com"  # Replace with her Gmail
email_password = password  # Set this in her system

# Email content
subject = "Your Early Access to Avatique is Here 🚀"
body = """Hi there,

Avatique is live! You’re on the exclusive early access waitlist.
Click the link below to get started:

Link: https://avatique.com

Thank you for joining the waitlist!
You rock!
"""

# Secure SSL context
context = ssl.create_default_context()

# -------------------------
# 3. Send Emails
# -------------------------
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    
    for email_receiver in emails:
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        
        smtp.send_message(em)
        print(f"Email sent to {email_receiver}")

print("All emails sent successfully!")