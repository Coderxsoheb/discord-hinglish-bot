from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    """
    Defines the home route for the web server.
    When Render pings this URL, it gets this response,
    keeping the service active.
    """
    return "Bot is alive, bhai!"

def run_flask_app():
    """
    Runs the Flask application.
    It binds to 0.0.0.0 and port 8080, which are standard for Render.
    """
    # Get port from environment variable if available, otherwise default to 8080
    # Render often sets a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Starting Flask keep-alive server on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")

def keep_alive():
    """
    Starts the Flask web server in a separate daemon thread.
    A daemon thread runs in the background and exits automatically
    when the main program (your Discord bot) exits.
    """
    t = Thread(target=run_flask_app)
    t.daemon = True  # Set the thread as a daemon thread
    t.start()
    print("✅ Keep-alive thread started.")

