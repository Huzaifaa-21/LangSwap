from db import db, ContactSubmission
from db import app  # Import the Flask app

def test_insert():
    with app.app_context():  # Use application context
        try:
            new_contact = ContactSubmission(
                name='Test User',
                email='test@example.com',
                message='This is a test message.'
            )
            db.session.add(new_contact)
            db.session.commit()
            print("Data inserted successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting data: {str(e)}")

if __name__ == '__main__':
    test_insert() 