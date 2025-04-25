from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from db import db, verify_user_login, create_app

main = Blueprint('main', __name__)
@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
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

@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    app = create_app()  # Or get your app context appropriately

    user = verify_user_login(app, email, password)
    if user:
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        flash('Login successful!', 'success')
        return redirect(url_for('main.home'))
    else:
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('main.register'))

    return render_template('register.html')  # Render the registration page if GET request


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the translate page.', 'danger')
            return redirect(url_for('main.register'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/translate', methods=['GET', 'POST'])
@login_required
def translate():
    detected_lang = None
    translated_text = None
    translated_audio_url = None

    if request.method == 'POST':
        input_text = request.form.get('input_text')
        input_audio = request.files.get('input_audio')
        target_lang = request.form.get('target_lang')

        # --- AI Logic Placeholder ---
        # 1. Detect language (from text or audio)
        # 2. Translate to target_lang
        # 3. Generate translated audio

        # For demonstration, use dummy values:
        if input_text:
            detected_lang = "English"  # Replace with AI detection
            translated_text = f"Translated ({target_lang}): {input_text[::-1]}"  # Dummy translation
            translated_audio_url = "/static/sample_audio.mp3"  # Replace with generated audio file path
        elif input_audio:
            detected_lang = "Detected from Audio"  # Replace with AI detection
            translated_text = f"Audio translated to {target_lang}"  # Dummy translation
            translated_audio_url = "/static/sample_audio.mp3"  # Replace with generated audio file path

    return render_template(
        'translate.html',
        detected_lang=detected_lang,
        translated_text=translated_text,
        translated_audio_url=translated_audio_url
    )
