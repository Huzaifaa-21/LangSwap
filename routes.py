from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from db import db, ContactSubmission, UserRegistration
import re  # Import regular expressions for email validation
from werkzeug.security import check_password_hash

# Create a Blueprint for routing
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')  # Render your home page

@main.route('/about')
def about():
    return render_template('about.html')  # Render your about page

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Simple email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address. Please try again.', 'danger')
            return redirect(url_for('main.contact'))

        try:
            new_contact = ContactSubmission(
                name=name,
                email=email,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error submitting your message. Please try again.', 'danger')
            print(f"Database error: {str(e)}")
        
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')  # Render the contact form page

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')  # Capture gender from the form
        age = request.form.get('age')
        password = request.form.get('password')  # You should hash this password before storing it
        
        # Debugging: Print the received data
        print(f"Received data: Full Name: {full_name}, Email: {email}, Phone: {phone_number}, Gender: {gender}, Age: {age}")

        # Check for existing email or phone number
        existing_user = UserRegistration.query.filter(
            (UserRegistration.email == email) | (UserRegistration.phone_number == phone_number)
        ).first()
        
        if existing_user:
            flash('A user with this email or phone number already exists. Please use a different one.', 'danger')
            print("Flash message for duplicate user set.")
            return redirect(url_for('main.register'))

        # Validate that gender is selected
        if not gender:
            flash('Please select a gender.', 'danger')
            return redirect(url_for('main.register'))  # Redirect back to the registration page

        try:
            new_user = UserRegistration(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                gender=gender,  # Ensure gender is not None
                age=age,
                password=password  # Store hashed password in production
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            print("Flash message for successful registration set.")
            return redirect(url_for('main.register'))  # Redirect back to the registration page
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")  # Print the error message for debugging
        
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Attempting login with email: {email} and password: {password}")  # Debugging line

        # Fetch user from the database
        user = UserRegistration.query.filter_by(email=email).first()
        print(f"User found: {user}")  # Debugging line

        if user and check_password_hash(user.password, password):  # Check if user exists and password matches
            session['user_id'] = user.id  # Store user ID in session
            session['user_name'] = user.full_name  # Store user name in session
            flash('Login successful! Welcome, ' + user.full_name + '!', 'success')  # Flash success message
            return redirect(url_for('main.home'))  # Redirect to home page
        else:
            flash('Invalid email or password. Please try again.', 'danger')  # Flash error message
            print("Invalid login attempt.")  # Debugging line

    return render_template('register.html')  # Render the registration page if GET request
