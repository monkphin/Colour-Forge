from colourforge import db, app
from sqlalchemy import text


def reset_database():
    """Drop all tables and recreate them."""
    with app.app_context():
        # Drop the tables using raw SQL execution
        db.session.execute(
            text(
                'DROP TABLE IF EXISTS entity_tags, recipe_tags, recipe_images,'
                'recipe_stages, recipes, users CASCADE;'
                 )
            )
        db.session.commit()

        print("Dropped all tables with CASCADE.")

        # Recreate the tables
        db.create_all()
        print("Database reset complete.")


if __name__ == "__main__":
    reset_database()
