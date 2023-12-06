from app import app, db

def drop_all_tables():
    with app.app_context():
        db.drop_all()

def create_all_tables():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    drop_all_tables()
    create_all_tables()

