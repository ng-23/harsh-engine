from flask import Flask
from harsh_engine.app import create_app

app = create_app()

if __name__ == "__main__":
    # executed when running module directly
    # this will use the basic (insecure) Flask WSGI server
    app.run(debug=True)
else:
    # executed when not running module directly
    # e.g. through a proper third-party WSGI server
    pass