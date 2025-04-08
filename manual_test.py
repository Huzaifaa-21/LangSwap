from db import db, UserRegistration
from db import create_app

app = create_app()

def test_insert():
    with app.app_context():
        try:
            new_user = UserRegistration(
                full_name='Test User',
                email='test@example.com',
                phone_number='1234567890',
                gender='Male',
                age=25,
                password='testpassword'  # Store hashed password in production
            )
            db.session.add(new_user)
            db.session.commit()
            print("Data inserted successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting data: {str(e)}")

if __name__ == '__main__':
    test_insert() 