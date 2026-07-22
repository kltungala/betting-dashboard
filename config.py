import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration shared by development and production."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'betting_dashboard.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
