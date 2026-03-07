import logging
import os

from flask import Flask, jsonify


def create_app():
    """Application factory for creating the Flask app."""
    application = Flask(__name__)

    # Configure logging
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    if log_level not in valid_levels:
        log_level = "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Application starting with log level: %s", log_level)

    @application.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    @application.route("/")
    def home():
        return "CI/CD is working"

    @application.route("/health")
    def health():
        return jsonify(status="UP")

    @application.errorhandler(404)
    def not_found(error):
        logger.warning("404 Not Found: %s", error)
        return jsonify(error="Not Found"), 404

    @application.errorhandler(500)
    def internal_error(error):
        logger.error("500 Internal Server Error: %s", error)
        return jsonify(error="Internal Server Error"), 500

    return application


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
