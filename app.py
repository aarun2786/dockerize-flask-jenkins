from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Define a single route for the home/root URL
@app.route('/')
def home():
    return "Hello, World! Your Flask app is running successfully."

@app.route("/profile")
def profile()
    return "Thsi is from profile path"

# Run the application if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
