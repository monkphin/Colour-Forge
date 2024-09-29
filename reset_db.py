from colourforge import db
from colourforge import app
from sqlalchemy import text

def reset_database():
    """Drop all tables and recreate them."""
    with app.app_context():
        # Drop the tables using text() for raw SQL execution
        db.session.execute(text('DROP TABLE IF EXISTS recipes, recipe_stages, entity_tags, recipe_images, recipe_tags CASCADE;'))
        db.session.commit()

        # Drop the recipes table last
        db.session.execute(text('DROP TABLE IF EXISTS recipes CASCADE;'))
        db.session.commit()
        
        print("Dropped all tables with CASCADE.")
        
        # Recreate the tables
        db.create_all()
        print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
