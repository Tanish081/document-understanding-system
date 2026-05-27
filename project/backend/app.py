"""Flask application entrypoint for the document understanding backend."""

from flask import Flask, jsonify
from flask_cors import CORS

from routes.upload_routes import upload_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(upload_bp)

    @app.get("/health")
    def health_check():
        """Return a basic status response so the frontend can verify the backend is running."""
        return jsonify({"status": "ok", "message": "Document understanding backend is running."})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)