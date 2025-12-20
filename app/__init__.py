from flask import Flask
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Security Plugins
    CSRFProtect(app)
    # Enable Security Headers, but disable CSP (to allow inline scripts/styles) and HTTPS redirect (for local/proxy compatibility)
    Talisman(app, content_security_policy=None, force_https=False) 

    config_class.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
