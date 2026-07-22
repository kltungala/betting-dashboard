from flask import Flask, render_template

from config import Config
from extensions import db, migrate


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Bettor, Fight
    from routes.bettors import bettors_bp
    from routes.fights import fights_bp

    app.register_blueprint(bettors_bp)
    app.register_blueprint(fights_bp)

    @app.get("/")
    def dashboard():
        stats = {
            "total_fights": Fight.query.count(),
            "active_fights": Fight.query.filter_by(status="open").count(),
            "total_bettors": Bettor.query.count(),
        }
        return render_template("dashboard.html", stats=stats)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
