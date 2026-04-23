from flask import Flask, jsonify
from werkzeug.routing import UUIDConverter

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register UUID converter
    app.url_map.converters['uuid'] = UUIDConverter

    # Initialize extensions
    from app.extensions import db, migrate, limiter
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Setup structured logging
    from app.utils.logger import setup_logging
    setup_logging(app)

    # Register blueprints
    from app.api.profiles import bp as profiles_bp
    from app.api.queries import bp as queries_bp
    app.register_blueprint(profiles_bp, url_prefix='/api/v1')
    app.register_blueprint(queries_bp, url_prefix='/api/v1')

    # Error handling for unexpected 500s or 404s
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

    return app
