"""
Module: routes.py

Description:
------------
This module defines the main recipe handling routes for the Colourforge
application. It contains routes for displaying recipes, adding new recipes,
editing existing ones, deleting recipes, searching by tags, and handling user
contact forms. The routes leverage SQLAlchemy for database interactions,
Flask-Login for user session management, and Cloudinary for image handling. The
module ensures that only authenticated users can perform certain actions,
maintains data integrity through relationship management, and provides a
pagination and search functionalities.

Key Functionalities:
--------------------
- **Home Page (`/`):** Displays a paginated list of all recipes available in
the application.

- **User Recipes (`/recipes`):** Shows a paginated list of recipes created by
the currently logged-in user.

- **Recipe Page (`/recipe_page/<int:recipe_id>`):** Displays detailed
information about a specific recipe, accessible to all users for sharing with
the wider community and over the internet.

- **Add Recipe (`/add_recipe`):** Provides a form for authenticated users to
create new recipes, including stages, images, and tags.

- **Edit Recipe (`/edit_recipe/<int:recipe_id>`):** Allows authenticated users
to modify existing recipes that they own or, if they are admins, any recipe
within the application.

- **Autocomplete Tags (`/tags/autocomplete`):** Supplies a list of existing
tags to support autocomplete functionality in the recipe forms.

- **Search (`/search`):** Enables users to search for recipes based on tags,
returning relevant results.

- **Delete Recipe (`/delete_recipe/<int:recipe_id>`):** Allows users to delete
their own recipes, ensuring that only authorized deletions occur.

- **Contact Form (`/contact`):** Handles user submissions from the contact
form, sending messages to the site owner.
"""


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
from math import ceil
from sqlalchemy import or_

# Local Imports
from colourforge import db, cloudinary
from colourforge.models import (
    Recipe,
    RecipeTag,
    EntityTag
    )
from colourforge.helpers import (
    recipe_handler,
    instruction_handler,
    tag_handler,
    handle_recipe_edit_post,
    remove_recipe
)
from colourforge.mail import contact_form

routes = Blueprint('routes', __name__)


@routes.route("/", methods=['GET', 'POST'])
def home():
    """
    Handles GET requests to display a paginated list of all recipes available
    in the application, excluding 'Demo Recipe' unless it belongs to the
    current user. The page number is retrieved from query parameters and
    defaults to 1 if not provided.

    Returns:
        Response: The rendered 'home.html' template populated with paginated
        recipes, current page, total pages, and the current user context.
    """
    # Check if user is authed and display appropriate cards, stripping Demos
    if current_user.is_authenticated:
        recipes = (Recipe.query
                   .filter(or_(Recipe.recipe_name != "Demo Recipe",
                               Recipe.user_id == current_user.id
                               )
                           ).order_by(Recipe.recipe_name).all())
    else:
        recipes = (Recipe.query
                   .filter(Recipe.recipe_name != "Demo Recipe")
                   .order_by(Recipe.recipe_name)
                   .all())

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Recipes per page
    total = len(recipes)
    total_pages = ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_recipes = recipes[start:end]

    return render_template(
        "home.html",
        recipes=paginated_recipes,
        page=page,
        total_pages=total_pages,
        user=current_user
    )


@routes.route("/recipes")
@login_required
def recipes():
    """
    Render the Recipes Page with a List of Recipes Created by the Current User.

    Handles GET requests to display a paginated list of recipes that belong to
    the currently authenticated user. Ensures that only the user's own recipes
    are displayed.

    Returns:
        Response: The rendered 'recipes.html' template populated with paginated
        recipes, current page, total pages, and the current user context.
    """
    recipes = Recipe.query.filter_by(
        user_id=current_user.id).order_by(Recipe.recipe_name).all()

    page = request.args.get('page', 1, type=int)
    per_page = 6  # Recipes per page
    total = len(recipes)
    total_pages = ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_recipes = recipes[start:end]

    return render_template(
        "recipes.html",
        recipes=paginated_recipes,
        page=page,
        total_pages=total_pages,
        user=current_user
    )


@routes.route("/recipe_page/<int:recipe_id>")
def recipe_page(recipe_id):
    """
    Accessible to all users, this route displays detailed information about a
    specific recipe, including its stages and associated images. Recipes
    do not require a user to be logged in to view, enabling them to be
    shared publicly.

    Args:
        recipe_id (int): The unique identifier of the recipe to display.

    Returns:
        Response: The rendered 'recipe_page.html' template populated with the
        specified recipe, referrer URL, and the current user context.
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    referrer = request.referrer

    return render_template(
        'recipe_page.html',
        recipe=recipe,
        referrer=referrer,
        user=current_user
    )


@routes.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    """
    Handles both GET and POST requests. On GET requests, renders the form for
    adding a new recipe. On POST requests, processes the submitted form data to
    create a new recipe, including its stages, images, and tags. Utilises
    helper functions to manage database interactions and ensures that the
    recipe is properly associated with the current user.

    Returns:
        Response:
            - On GET: The rendered 'add_recipe.html' template displaying the
            recipe creation form.
            - On POST: Redirects to the 'recipes' page with a success flash
            message upon successful recipe creation. If form validation fails,
            redirects back with error messages.
    """
    if request.method == "POST":

        # Create recipe in DB
        recipe = recipe_handler(request.form)

        # Init Variables
        instructions = request.form.getlist('instructions[]')
        image_files = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        # collect tags and convert to a string
        tag_names_str = request.form.get('tags', '')
        # split string at the comma to add one at a time to the db
        tag_names = tag_names_str.split(',')
        stage_num = 1

        # Process instructions and images
        instruction_handler(recipe, instructions, image_files, alt_texts)

        # process tags
        tag_handler(recipe, tag_names)

        flash('Paint Recipe successfully added!', category='success')

        return redirect("recipes")

    return render_template('add_recipe.html')


@routes.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    """
    Handles both GET and POST requests for editing a recipe. On GET requests,
    renders the form populated with the existing recipe data. On POST requests,
    processes the submitted form data to update the recipe's details, including
    its stages, images, and tags. Ensures that only the recipe's owner or an
    admin can perform edits.

    Args:
        recipe_id (int): The unique identifier of the recipe to edit.

    Returns:
        Response:
            - On GET: The rendered 'edit_recipe.html' template with the
            recipe's current data.
            - On POST: Redirects to the 'recipe_page' with a success flash
            message upon successful editing. If validation fails, redirects
            back with error messages.
    """
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure user owns the recipe
    if recipe.user_id != current_user.id and not current_user.is_admin:
        flash(
            "This recipe isn't yours, you can only edit your own recipes.",
            category="info"
            )
        return redirect(url_for('routes.home'))

    # Handle POST request
    if request.method == "POST":
        handle_recipe_edit_post(recipe)
        flash("Recipe has been updated", category='success')
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
    Serves a JSON response containing all existing tag names in the database.
    This endpoint is used to support autocomplete features in forms where users
    can add tags to recipes.

    Returns:
        Response: A JSON array of tag names.
    """
    tags = RecipeTag.query.all()
    tag_names = [tag.tag_name for tag in tags]
    return jsonify(tag_names)


@routes.route('/search', methods=['GET'])
def search():
    """
    Handle Recipe Search Functionality Based on Tags.

    Allows users to search for recipes by specifying tag names. Retrieves tags
    that match the search query and returns all recipes associated with those
    tags. Results are displayed on a separate search results page.

    Returns:
        Response:
            - If search query is empty: Redirects to the home page with an
            error flash message.
            - If no matching tags are found: Displays an informational flash
            message.
            - Otherwise: Renders the 'tag_search_results.html' template with
            the list of matching recipes.
    """
    search = request.args.get('search')
    if not search:
        flash("Please enter a search term.", category="error")
        return redirect(url_for('routes.home'))

    # Find all tags that match the query
    matching_tags = (
        RecipeTag.query
        .filter(RecipeTag.tag_name.ilike(f"%{search}%"))
        .all()
        )

    if not matching_tags:
        flash(
            f"No recipes found that match your search: { search }",
            category="info"
        )

    # Find all recipes that match the tags.
    matching_recipes = []
    for tag in matching_tags:
        entity_tags = EntityTag.query.filter_by(tag_id=tag.tag_id).all()
        for entity_tag in entity_tags:
            recipe = Recipe.query.get(entity_tag.recipe_id)
            if (
                recipe
                and recipe not in matching_recipes
            ):
                matching_recipes.append(recipe)

    return render_template(
        'tag_search_results.html',
        recipes=matching_recipes,
        search=search
    )


@routes.route("/delete_recipe/<int:recipe_id>", methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    """
    Allows users to delete their own recipes, including all associated stages,
    images, and tags. Ensures that only the recipe owner can perform deletions.
    Utilizes helper functions to manage the deletion process and maintains
    data integrity by cascading deletions appropriately.

    Args:
        recipe_id (int): The unique identifier of the recipe to delete.

    Returns:
        Response:
            - On Successful Deletion: Redirects to the user's recipes page with
            an informational flash message.
            - On Unauthorized Access: Redirects to the home page with an error
            flash message.

    Raises:
        404 Error: If no recipe with the given `recipe_id` exists.
    """
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure user owns the recipe
    if recipe.user_id != current_user.id:
        flash(
            "You do not have permission to delete this recipe.",
            category="error"
        )
        return redirect(url_for('routes.home'))

    # Use helper to delete recipe
    remove_recipe(recipe)
    flash("Recipe has been deleted", category='info')
    return redirect(url_for('routes.recipes'))


@routes.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handles both GET and POST requests. On GET requests, renders the contact
    form.
    On POST requests, validates the submitted data and sends the content of the
    form to the site administrator via email. Provides appropriate feedback to
    the user based on the success or failure of the submission.

    Returns:
        Response:
            - On GET: The rendered 'contact.html' template displaying the
            contact form.
            - On POST:
                - If validation fails: Redirects back to the contact form with
                error flash messages.
                - If submission is successful: Redirects to the contact form
                with a success flash message.
    """
    if request.method == "POST":
        sender_email = request.form.get('sender_email')
        sender_name = request.form.get('sender_name')
        subject = request.form.get('subject')
        message_content = request.form.get('message_content')

        if not message_content:
            flash('Please fill in the message content.', category='error')
            return redirect(url_for('routes.contact'))
        elif not subject:
            flash('Please fill in the subject field', category='error')
            return redirect(url_for('routes.contact'))
        elif not sender_name:
            flash('Please provide a name.', 'error')
            return redirect(url_for('routes.contact'))
        elif not sender_email:
            flash('Please provide your email address.', category='error')
            return redirect(url_for('routes.contact'))
        else:
            contact_form(sender_email, sender_name, subject, message_content)
            flash("""
                  Your message has been sent successfully!,
                  someone will be in touch soon.""", category='success')
            return redirect(url_for('routes.contact'))

    return render_template('contact.html')


@routes.route("/about")
def about():
    """
    Accessible to logged out users, this route displays a brief about section
    designed to help inform new users as to what the site is and what its
    intended uses are.

    Returns:
        Response: The rendered 'about.html' template.
    """

    return render_template('about.html')
