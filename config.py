import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///lite_ugx_earn.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
