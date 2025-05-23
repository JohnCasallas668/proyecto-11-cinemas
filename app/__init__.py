from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cineapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.tarjetas import tarjetas_bp
    from app.routes.reservas import reservas_bp
    from app.routes.pagos import pagos_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(tarjetas_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(pagos_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        from app.models import initialize_cinema_seats
        initialize_cinema_seats()
    
    # Context processor to make current date/time available in all templates
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.now()
        return dict(now=now)
    
    return app
