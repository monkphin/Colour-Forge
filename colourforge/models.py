"""
Module: models.py

Description:
------------
This module defines the database models for the Colourforge application using
SQLAlchemy. It covers the primary entities involved in the application,
including users, recipes, stages, images, tags, and their associations.
The models establish relationships to facilitate efficient data retrieval and
manipulation, ensuring data integrity and consistency across the application.

Classes:
--------
- User:
    Represents a user within the application. Stores user credentials and
    administrative status.

- Recipe:
    Represents a painting recipe created by a user. Contains details like name
    and description.

- RecipeStage:
    Represents a single stage or step within a recipe, including instructions
    and associated images.

- RecipeImage:
    Represents an image associated with a specific stage of a recipe, storing
    URLs and metadata.

- RecipeTag:
    Represents a tag or category that can be associated with recipes for
    organizational purposes.

- EntityTag:
    Represents the association between recipes and tags, allowing for
    many-to-many relationships.

"""


from colourforge import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    Represents a user within the ColourForge application, storing essential
    credentials and administrative status. Users can create multiple recipes.

    Attributes:
        id (int): The primary key identifier for the user.
        username (str): The unique username chosen by the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
        is_admin (bool): Flag indicating if the user has administrative
        privileges.

    Relationships:
        recipes (Recipe): One-to-many relationship with the Recipe model. A
        user can have multiple recipes.
    """

    # Explicitly set the table name
    __tablename__ = 'users'

    # schema for the users model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship to the Recipes table (one-to-many relationship)
    recipes = db.relationship(
        "Recipe",
        backref="user",
        cascade="all, delete",
        lazy=True)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return f"<User {self.username}>"


class Recipe(db.Model):
    """
    Represents a painting recipe created by a user, containing details such as
    name and description.
    Each recipe can have multiple stages and tags associated with it.

    Attributes:
        recipe_id (int): The primary key identifier for the recipe.
        user_id (int): Foreign key linking the recipe to its creator (User).
        recipe_name (str): The name/title of the recipe.
        recipe_desc (str): A detailed description of the recipe.

    Relationships:
        stages (RecipeStage): One-to-many relationship with the RecipeStage
        model.
        entity_tags (EntityTag): One-to-many relationship with the EntityTag
        model.
    """

    # Explicitly set the table name
    __tablename__ = 'recipes'

    # Schema for the recipes model
    recipe_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(
            'users.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
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
    """
    RecipeStage Model

    Represents a single stage or step within a recipe, containing instructions
    and associated images.
    Each stage is part of a recipe.

    Attributes:
        stage_id (int): The primary key identifier for the recipe stage.
        recipe_id (int): Foreign key linking the stage to its parent recipe.
        stage_num (int): The numerical order of the stage within the recipe.
        instructions (str): Detailed instructions for the stage.
        is_final_stage (bool): Flag indicating if this stage is the final one
        in the recipe.

    Relationships:
        recipe_images (RecipeImage): One-to-many relationship with the
        RecipeImage model.
    """

    # Explicitly set the table name
    __tablename__ = 'recipe_stages'

    # schema for the recipe_stages model
    stage_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "recipes.recipe_id",
            ondelete='CASCADE'
        ),
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
    """
    RecipeImage Model

    Represents an image associated with a specific stage of a recipe, storing
    URLs and metadata.
    Images can be uploaded to external services like Cloudinary for storage and
    retrieval.

    Attributes:
        image_id (int): The primary key identifier for the recipe image.
        stage_id (int): Foreign key linking the image to its corresponding
        recipe stage.
        image_url (str): The URL of the full-sized image.
        thumbnail_url (str): The URL of the thumbnail version of the image.
        alt_text (str): Alternative text description for the image.
        public_id (str): The public identifier of the image in the external
        storage service.

    Relationships:
        stage (RecipeStage): Many-to-one relationship with the RecipeStage
        model.
    """

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
    """
    RecipeTag Model

    Represents a tag or category that can be associated with recipes for
    organizational and searching purposes.
    Tags help in categorizing and filtering recipes based on shared
    characteristics.

    Attributes:
        tag_id (int): The primary key identifier for the recipe tag.
        tag_name (str): The unique name of the tag.

    Relationships:
        entity_tags (EntityTag): One-to-many relationship with the EntityTag
        model.
    """

    # Explicitly set the table name
    __tablename__ = 'recipe_tags'

    # schema for the recipe_tags model
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20), unique=True, nullable=True)

    def __repr__(self):
        return f"<Tag {self.tag_name}>"


class EntityTag(db.Model):
    """
    EntityTag Model

    Represents the association between recipes and tags, allowing for a
    many-to-many relationship.
    This model links recipes to their respective tags, specifying the type of
    entity the tag is associated with.

    Attributes:
        recipe_id (int): Foreign key linking to the associated recipe.
        tag_id (int): Foreign key linking to the associated tag.
        entity_type (str): The type of entity the tag is associated with (e.g.,
        'recipe').

    Relationships:
        recipe (Recipe): Many-to-one relationship with the Recipe model.
        recipe_tag (RecipeTag): Many-to-one relationship with the RecipeTag
        model.
    """

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
