from app import create_app

# Entry point used by Gunicorn in production.
app = create_app('production')
