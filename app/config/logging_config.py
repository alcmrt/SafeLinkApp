import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    
    # Remove any existing handlers from the app logger
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # Basic configuration
    logging.basicConfig(
        level=logging.INFO,  # Log messages with level INFO
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
