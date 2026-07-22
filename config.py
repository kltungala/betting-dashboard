import os


class Config:
    """Application configuration shared by development and production."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-key")
