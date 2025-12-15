from app import app, db
try:
    with app.app_context():
        db.create_all()
        print("DB Init Success")
except Exception as e:
    print(f"DB Init Failed: {e}")
