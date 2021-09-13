from dotenv import load_dotenv
load_dotenv()

import os

from app import app

if __name__ == "__main__":
    import gunicorn, psycopg2, pypugjs, pretty_errors, png, flask_script
    app.run(debug=True)
