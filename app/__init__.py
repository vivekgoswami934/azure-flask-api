from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger # type: ignore
from flask_cors import CORS # type: ignore
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    
    
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)
    Swagger(app)

    @app.route('/')
    def index():
        return '<h1>Welcome!</h1>'

    try:
        with app.app_context():
            
            from .routes import nex_score_routes, market_region
            app.register_blueprint(nex_score_routes.bp)
            app.register_blueprint(market_region.bp)
            
            db.create_all()  # Create tables that do not exist
    except Exception as e:
        print(f"Error during app initialization: {e}")
        # Handle the error (e.g., log it, display a message, etc.)

    return app

# def create_app():
#     app = Flask(__name__)
#     CORS(app)
#     app.config.from_object(Config) #config
#     db.init_app(app)  #init
#     Swagger(app)

#     with app.app_context():
#         from .routes import nex_score_routes,market_region  # Import routes    
#         app.register_blueprint(nex_score_routes.bp)
#         app.register_blueprint(market_region.bp)

#         # Create tables that do not exist
#         db.create_all()

#     return app
