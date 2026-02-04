from flask import Flask
from .routes.main import main_bp
from .routes.category_routes import category_bp # <--- Importar o novo blueprint

def create_app():
    app = Flask(__name__)
    
    # Carrega as configurações da classe Config
    app.config.from_object('config.Config')
    
    # Registro de Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp) # <--- Registrar o novo blueprint
    
    return app
