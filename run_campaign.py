from app import app
from send_campaign import send_campaign

if __name__ == '__main__':
    # IMPORTANT: Run the entire function inside the application context
    with app.app_context():
        print("Starting scheduled campaign...")
        results = send_campaign()
        # Output results to stdout so they appear in scheduler logs
        for line in results:
            print(line)
        print("Scheduled campaign finished.")
