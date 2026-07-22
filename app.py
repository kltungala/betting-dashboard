from flask import Flask, render_template

from config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
