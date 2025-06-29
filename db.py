from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from sqlalchemy.exc import OperationalError
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from sqlalchemy import text  # Import text from SQLAlchemy

# Create a single instance of SQLAlchemy
db = SQLAlchemy()

from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Huzaifa%4021@localhost:3308/LangSwap'  # Update with your credentials
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Show SQL queries for debugging

    # Initialize the SQLAlchemy instance with the app
    db.init_app(app)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'huzaifahabib8562@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vnjbtqulrvzyyqli'  # <-- No spaces, use your actual app password
    mail.init_app(app)

    return app

class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactSubmission {self.name}>'

class UserRegistration(db.Model):
    __tablename__ = 'registrations'  # Table name for storing registration data
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), nullable=False)  # Adjust length as needed
    gender = db.Column(db.String(10), nullable=False)  # e.g., 'Male', 'Female', 'Other'
    age = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserRegistration {self.full_name}>'

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Huzaifa@21',
            port=3308
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Create the database if it does not exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS LangSwap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("Database 'LangSwap' checked/created.")
            
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_tables(app):  # Accept app as an argument
    with app.app_context():
        db.create_all()  # This will create all tables, including the new UserRegistration table
        print("Tables created successfully")

def submit_contact_form(app, name, email, message):
    try:
        with app.app_context():
            new_submission = ContactSubmission(
                name=name,
                email=email,
                message=message
            )
            db.session.add(new_submission)
            db.session.commit()
            print("Submission successful.")
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting contact form: {str(e)}")

def create_db(app):
    with app.app_context():  # Use application context
        db.create_all()  # Create the database tables

def test_db_connection(app):  # Accept app as an argument
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))  # Use text() for raw SQL
            print("Database connection successful.")
    except Exception as e:
        print(f"Database connection error: {str(e)}")

def verify_user_login(email, password):
    user = UserRegistration.query.filter_by(email=email).first()
    if user and user.password == password:  # For plain text password
        return user
    return None

def change_user_password(user_id, new_password):
    user = UserRegistration.query.get(user_id)
    if user:
        user.password = new_password  # In production, hash the password!
        db.session.commit()
        return True
    return False

if __name__ == "__main__":
    create_database()
    app = create_app()
    create_tables(app)
    create_db(app)