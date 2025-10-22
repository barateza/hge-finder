from flask import Flask


def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__)

    # Import and register routes
    from .routes import bp
    app.register_blueprint(bp)

    return app
