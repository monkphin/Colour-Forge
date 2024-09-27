import os
from colourforge import app, db

"""
# Create the tables in the database
with app.app_context():
    db.create_all()
"""


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=os.environ.get("DEBUG")
    )