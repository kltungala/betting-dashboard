from flask import Flask, render_template
from sqlalchemy import func, select

from config import Config
from extensions import db, migrate


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Bet, Bettor, Fight, LedgerEntry
    from routes.bettors import bettors_bp
    from routes.bets import bets_bp
    from routes.fights import fights_bp
    from routes.ledger import ledger_bp
    from routes.payments import payments_bp
    from routes.reports import reports_bp

    app.register_blueprint(bettors_bp)
    app.register_blueprint(bets_bp)
    app.register_blueprint(fights_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(reports_bp)

    @app.get("/")
    def dashboard():
        bettors = Bettor.query.all()
        stats = {
            "total_fights": Fight.query.count(),
            "active_fights": Fight.query.filter_by(status="open").count(),
            "total_bettors": len(bettors),
            "total_bets": Bet.query.count(),
            "total_bet_amount": db.session.scalar(
                select(func.coalesce(func.sum(Bet.amount), 0))
            ),
            "outstanding_credits": sum((max(bettor.balance, 0) for bettor in bettors), 0),
            "house_commission": db.session.scalar(
                select(func.coalesce(func.sum(Bet.commission_amount), 0)).where(Bet.status == "won")
            ),
        }
        return render_template("dashboard.html", stats=stats)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
