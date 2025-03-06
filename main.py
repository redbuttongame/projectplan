from app import app
import os

if __name__ == "__main__":
    # Check if running in production environment
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host="0.0.0.0", port=5000, ssl_context='adhoc')
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
