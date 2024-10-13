from colourforge import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    # Explicitly set the table name
    __tablename__ = 'users'
    
    # schema for the users model
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relationship to the Recipes table (one-to-many relationship)
    recipes = db.relationship("Recipe", backref="user", cascade="all, delete", lazy=True)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return f"<User {self.user_name}>"


class Recipe(db.Model):
    # Explicitly set the table name
    __tablename__ = 'recipes'

    # Schema for the recipes model
    recipe_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    recipe_name = db.Column(db.String(55), nullable=False)
    recipe_desc = db.Column(db.Text, nullable=False)

    # Relationship to other models
    stages = db.relationship(
        'RecipeStage', 
        backref='recipe', 
        lazy=True, 
        cascade="all, delete-orphan"
        )
    entity_tags = db.relationship(
        'EntityTag', 
        backref='recipe', 
        lazy=True,  
        cascade="all, delete-orphan"
        )

    def __repr__(self):
        return f"<Recipe {self.recipe_name}: {self.recipe_desc[:50]}...>" 


class RecipeStage(db.Model):
    # Explicitly set the table name
    __tablename__ = 'recipe_stages'

    # schema for the recipe_stages model
    stage_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "recipes.recipe_id", 
            ondelete='CASCADE'), 
            nullable=False
        )
    stage_num = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    is_final_stage = db.Column(db.Boolean, default=False)

    recipe_images = db.relationship(
        'RecipeImage', 
        backref='stage', 
        lazy=True,  
        cascade="all, delete-orphan"
        )

    def __repr__(self):
        return f"<Stage {self.stage_num}: {self.instructions[:50]}...>"


class RecipeImage(db.Model):
    # Explicitly set the table name
    __tablename__ = 'recipe_images'

    # schema for the recipe_images model
    image_id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "recipe_stages.stage_id", 
            ondelete='CASCADE'
            ), 
        nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    alt_text = db.Column(db.String(255), nullable=True)
    public_id = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Image {self.image_url}>"


class RecipeTag(db.Model):
    # Explicitly set the table name
    __tablename__ = 'recipe_tags'

    # schema for the recipe_tags model
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), unique=True, nullable=True)

    def __repr__(self):
        return f"<Tag {self.tag_name}>"


class EntityTag(db.Model):
    # Explicitly set the table name
    __tablename__ = 'entity_tags'

    # schema for the entity_tags model
    recipe_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "recipes.recipe_id", 
            ondelete='CASCADE'
            ), 
        primary_key=True
        )
    tag_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "recipe_tags.tag_id", 
            ), 
        primary_key=True
        )
    entity_type = db.Column(db.String(50), nullable=False)
    
    recipe_tag = db.relationship("RecipeTag", backref="entity_tags")

    def __repr__(self):
        return (
            f"<EntityTag recipe_id={self.recipe_id} "
            f"tag_id={self.tag_id} "
            f"entity_type={self.entity_type}>"
            )