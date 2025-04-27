from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from functools import wraps
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr
from deep_translator import GoogleTranslator
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from langdetect import detect, LangDetectException
import re
import random
from flask_mail import Message
from db import db, UserRegistration, mail, verify_user_login, ContactSubmission
from db import change_user_password  # Make sure this is imported

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
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        age = request.form.get('age')
        password = request.form.get('password')

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Store registration data and OTP in session
        session['pending_registration'] = {
            'full_name': full_name,
            'email': email,
            'phone_number': phone_number,
            'gender': gender,
            'age': age,
            'password': password,
            'otp': otp
        }

        # Send OTP email
        msg = Message(
            subject='LangSwap Email Verification OTP',
            sender='huzaifahabib8562@gmail.com',
            recipients=[email]
        )
        msg.body = f'Your OTP for LangSwap registration is: {otp}'
        mail.send(msg)

        flash('An OTP has been sent to your email. Please verify to complete registration.', 'info')
        return redirect(url_for('main.verify_otp'))

    return render_template('register.html')

@main.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_registration' not in session:
        flash('No registration in progress.', 'danger')
        return redirect(url_for('main.register'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        reg_data = session['pending_registration']
        if user_otp == reg_data['otp']:
            # Save user to database
            new_user = UserRegistration(
                full_name=reg_data['full_name'],
                email=reg_data['email'],
                phone_number=reg_data['phone_number'],
                gender=reg_data['gender'],
                age=reg_data['age'],
                password=reg_data['password']  # Hash in production!
            )
            db.session.add(new_user)
            db.session.commit()
            session.pop('pending_registration')
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.register'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('verify_otp.html')

@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = verify_user_login(email, password)
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

        # Handle audio input
        if input_audio and input_audio.filename != '':
            filename = secure_filename(input_audio.filename)
            temp_audio_path = os.path.join(tempfile.gettempdir(), filename)
            input_audio.save(temp_audio_path)

            # Convert to WAV if not already WAV
            wav_audio_path = temp_audio_path
            if not filename.lower().endswith('.wav'):
                wav_audio_path = temp_audio_path + '.wav'
                try:
                    audio = AudioSegment.from_file(temp_audio_path)
                    audio.export(wav_audio_path, format="wav")
                except Exception as e:
                    flash(f"Audio conversion failed: {e}. Please upload a valid audio file.", "danger")
                    os.remove(temp_audio_path)
                    return render_template(
                        'translate.html',
                        detected_lang=detected_lang,
                        translated_text=translated_text,
                        translated_audio_url=translated_audio_url
                    )

            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(wav_audio_path) as source:
                    audio_data = recognizer.record(source)
                    speech_text = recognizer.recognize_google(audio_data)
                    detected_lang = "auto"
                    input_text = speech_text
            except Exception as e:
                flash(f"Speech recognition failed: {e}", "danger")

            # Clean up temp files
            os.remove(temp_audio_path)
            if wav_audio_path != temp_audio_path and os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

        # Handle text input (either from textarea or recognized from audio)
        if input_text:
            # Use langdetect for language detection
            try:
                detected_lang_code = detect(input_text)
                # Optionally, map code to language name for display
                lang_map = {
                    "en": "English", "hi": "Hindi", "bn": "Bengali", "es": "Spanish",
                    "zh-cn": "Chinese (Simplified)", "ru": "Russian", "ja": "Japanese",
                    "ko": "Korean", "de": "German", "fr": "French", "ta": "Tamil",
                    "te": "Telugu", "kn": "Kannada", "gu": "Gujarati", "pa": "Punjabi"
                }
                detected_lang = lang_map.get(detected_lang_code.lower(), detected_lang_code)
            except LangDetectException:
                detected_lang = "unknown"

            try:
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(input_text)
            except Exception:
                translated_text = "Translation failed."

            try:
                tts = gTTS(translated_text, lang=target_lang)
                temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(temp_audio_file.name)
                translated_audio_url = url_for('main.translated_audio', filename=os.path.basename(temp_audio_file.name))
            except Exception:
                translated_audio_url = None

        if not input_text and not (input_audio and input_audio.filename != ''):
            flash("Please provide text or record/upload audio for translation.", "warning")

    return render_template(
        'translate.html',
        detected_lang=detected_lang,
        translated_text=translated_text,
        translated_audio_url=translated_audio_url
    )

@main.route('/translated_audio/<filename>')
@login_required
def translated_audio(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(file_path, mimetype='audio/mp3', as_attachment=False)


@main.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('main.register'))
    user = UserRegistration.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@main.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please log in to change your password.', 'danger')
        return redirect(url_for('main.register'))

    user = UserRegistration.query.get(session['user_id'])
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Check current password
    if user.password != current_password:
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.profile'))

    # Check new password match
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.profile'))

    # Update password
    if change_user_password(user.id, new_password):
        flash('Password changed successfully!', 'success')
    else:
        flash('Failed to change password. Please try again.', 'danger')

    return redirect(url_for('main.profile'))
