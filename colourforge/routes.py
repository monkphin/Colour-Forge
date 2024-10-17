# Third-Party Library Imports
from flask import (
    flash,
    render_template, 
    request, 
    redirect, 
    url_for,
    Blueprint,
    jsonify
)

from flask_login import login_required, current_user

# Local Imports
from colourforge import db, cloudinary
from colourforge.models import (
    Recipe, 
    RecipeStage, 
    RecipeImage, 
    RecipeTag, 
    EntityTag
    )
from colourforge.helpers import (
    recipe_handler,
    instruction_handler,
    tag_handler,
    handle_recipe_edit_post,
)

routes = Blueprint('routes', __name__)

# Content rendering only routes
@routes.route("/", methods=['GET', 'POST'])
def home():
    """
    Renders the home page with a list of recipes if the user is logged in.

    Returns:
        Response: The rendered home page.
    """
    if current_user.is_authenticated:
        recipes = Recipe.query.filter_by(
            user_id=current_user.id).order_by(Recipe.recipe_name).all()
    else:
        recipes = None
    return render_template("home.html", recipes=recipes, user=current_user)


@routes.route("/recipes")
@login_required
def recipes():
    """
    Renders the recipes page with a list of recipes for the current user.

    Returns:
        Response : The rendered recipes page.
    """
    recipes = Recipe.query.filter_by(
        user_id=current_user.id).order_by(Recipe.recipe_name).all()
    return render_template("recipes.html", recipes=recipes, user=current_user)


@routes.route("/recipe_page/<int:recipe_id>")
def recipe_page(recipe_id):
    """
    Renders the recipe page for the specified recipe.

    Args:
        recipe_id (int): The ID of the recipe to display.

    Returns:
        Response: The rendered recipe page.
    """
    recipe=Recipe.query.get_or_404(recipe_id)
    referrer = request.referrer 

    return render_template(
        'recipe_page.html',
         recipe=recipe, 
         referrer=referrer, 
         user=current_user
         )


# Routes that render and write content 
@routes.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    """
    Renders the add recipe page and handles the creation of a new recipe.
    Handles the addition of new recipes, stages, and images to the DB when a POST
    request is made. Otherwise, renders the form.

    Returns:
        Response: The rendered add recipe form page.
    """
    if request.method == "POST":    

        # Create recipe in DB
        recipe = recipe_handler(request.form)    

        # Init Variables 
        instructions = request.form.getlist('instructions[]')
        image_files = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        #collect tags and convert to a string
        tag_names_str = request.form.get('tags', '')
        # split string at the comma to add one at a time to the db
        tag_names = tag_names_str.split(',') 
        stage_num = 1

        #Process instructions and images
        instruction_handler(recipe, instructions, image_files, alt_texts)

        #process tags
        tag_handler(recipe, tag_names)

        flash('Paint Recipe successfully added!', category='success')

        return redirect("recipes")   
    
    return render_template('add_recipe.html')


@routes.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    """
    Handles the editing of an existing recipe.
    POST request types will update the recipe, stages, and images in the DB.
    Otherwise this renders the form.

    Args:
        recipe_id (int): The ID of the recipe to edit.

    Returns:
        Response: The rendered edit recipe form page or a redirect response 
        after successful editing.
    """
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure user owns the recipe
    if recipe.user_id != current_user.id:
        flash(
            "You do not have permission to edit this recipe.", category="error")
        return redirect(url_for('routes.home'))

    # Handle POST request
    if request.method == "POST":
        handle_recipe_edit_post(recipe)
        flash("Recipe has been updated")
        return redirect(url_for(
            'routes.recipe_page', 
            recipe_id=recipe.recipe_id)
            )

    # Handle GET request
    recipes = list(Recipe.query.order_by(Recipe.recipe_id).all())
    return render_template(
        "edit_recipe.html", 
        recipe=recipe, 
        recipes=recipes, 
        user=current_user
        )


@routes.route("/tags/autocomplete", methods=["GET"])
@login_required
def autocomplete_tags():
    """
    Provides a list of all available tags for autocomplete purposes.
    """
    tags = RecipeTag.query.all()
    tag_names = [tag.tag_name for tag in tags]
    return jsonify(tag_names)

@routes.route('/search', methods=['GET'])
def search():
    pass

@routes.route("/delete_recipe/<int:recipe_id>")
@login_required
def delete_recipe(recipe_id):
    """
    Handles recipe deletion. 
    This route will delete the recipe, stages, images, and tags associated with 
    the recipe.

    Args:
        recipe_id (int): The ID of the recipe to delete.

    Returns:
        Response: Redirects to the recipes page after deletion.
    """
    recipe = Recipe.query.get_or_404(recipe_id)

    # ensure user owns the recipe
    if recipe.user_id != current_user.id:
        flash("You do not have permission to edit this recipe.", category="error")
        return redirect(url_for('routes.home'))

    # Delete associated stages and images
    stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).all()
    for stage in stages:
        images = RecipeImage.query.filter_by(stage_id=stage.stage_id).all()
        for image in images:
            if image.public_id:
                # Delete the image from Cloudinary using public_id
                cloudinary.uploader.destroy(image.public_id)
            db.session.delete(image)  # Delete image record from the database
        db.session.delete(stage)  # Delete stage record from the database

    # Delete associated tags
    EntityTag.query.filter_by(recipe_id=recipe.recipe_id).delete()

    # Delete the recipe itself
    db.session.delete(recipe)
    db.session.commit()

    flash("Recipe has been deleted")

    return redirect(url_for('routes.recipes'))