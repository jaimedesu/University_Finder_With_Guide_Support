import json
from app import app, db, University, User
from werkzeug.security import generate_password_hash

def run_seed():
    with app.app_context():
        print("Cleaning up database...")
        db.drop_all()
        db.create_all()

        # 1. Create an Admin User
        print("Creating admin user...")
        admin = User(
            username="admin",
            email="admin@example.com",
            age=20,
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)

        # 2. Load Universities from the newly formatted JSON
        print("Seeding universities from final_seed_data.json...")
        try:
            with open('final_seed_data.json', 'r', encoding='utf-8') as file:
                universities_data = json.load(file)
            
            for data in universities_data:
                uni = University(
                    name=data.get('name'),
                    location=data.get('location'),
                    tuition=data.get('tuition'),
                    acceptance_rate=data.get('acceptance_rate'),
                    programs=data.get('programs'),
                    image_url=data.get('image_url'),
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude')
                )
                db.session.add(uni)
            
            db.session.commit()
            print(f"Success. Seeded {len(universities_data)} universities.")
            
        except FileNotFoundError:
            print("Error. final_seed_data.json not found. Please ensure the file is in the current directory.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during database commit: {e}")

if __name__ == '__main__':
    run_seed()