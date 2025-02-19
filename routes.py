from flask import Blueprint, render_template, redirect, url_for, request, flash
from db import db, ContactSubmission
import re  # Import regular expressions for email validation

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

@main.route('/register')
def register():
    return render_template('register.html')  # Render your registration page

@main.route('/login')
def login():
    return render_template('login.html')  # Render your login page

