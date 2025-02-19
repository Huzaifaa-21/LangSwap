# app.py
from db import create_app, create_db, test_db_connection, create_tables  # Import create_app
from routes import main  # Ensure this matches the name of your blueprint
import os

app = create_app()  # Create the Flask app

app.secret_key = 'your_unique_secret_key'  # Set your secret key here

# Initialize the database
create_db(app)  # Pass the app instance to create_db
create_tables(app)  # Pass the app instance to create_tables
test_db_connection(app)  # Pass the app instance to test_db_connection

# Register the blueprint
app.register_blueprint(main)  # Use the correct blueprint name

print(os.urandom(24))  # This will generate a random 24-byte string

if __name__ == '__main__':
    app.run(debug=True)