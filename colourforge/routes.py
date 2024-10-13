# Third-Party Library Imports
from flask import (
    flash,
    render_template, 
    request, 
    redirect, 
    url_for,
    Blueprint
)

from flask_login import login_required, current_user

# Local Imports
from colourforge import app, db, cloudinary, cloudinary_url
from colourforge.models import (User, 
                                Recipe, 
                                RecipeStage, 
                                RecipeImage, 
                                RecipeTag, 
                                EntityTag)
from colourforge.helpers import (
    recipe_handler,
    instruction_handler,
    upload_image,
    tag_handler,
    edit_tag_handler
)


routes = Blueprint('routes', __name__)

# Content rendering only routes
@routes.route("/", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.recipe_name).all()
    else:
        recipes = None
    return render_template("home.html", recipes=recipes, tag_dict={}, user=current_user)


@routes.route("/recipes")
@login_required
def recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.recipe_name).all()
    return render_template("recipes.html", recipes=recipes, tag_dict={}, user=current_user)


@routes.route("/recipe_page/<int:recipe_id>")
def recipe_page(recipe_id):
    recipe=Recipe.query.get_or_404(recipe_id)
    referrer = request.referrer 

    return render_template(
        'recipe_page.html', 
        recipe=recipe, 
        referrer=referrer, 
        tag_dict={},
        user=current_user
        )


# Routes that render and write content 
@routes.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
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

    else:
        # Get collection of existing tags as a variable and iterate through
        # to create a dictionary to match how materialize is handling chips/tags.     
        all_tags = RecipeTag.query.all()
        tag_dict = {tag.tag_name: None for tag in all_tags}

        return render_template("add_recipe.html", tag_dict=tag_dict, user=current_user)


@routes.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # ensure user owns the recipe
    if recipe.user_id != current_user.id:
        flash("You do not have permission to edit this recipe.", category="error")
        return redirect(url_for('routes.home'))

    recipes = list(Recipe.query.order_by(Recipe.recipe_id).all())

    if request.method == "POST":
        recipe.recipe_name = request.form.get('recipe_name')
        recipe.recipe_desc = request.form.get('recipe_desc')

        # Initialize variables from form data
        instructions = request.form.getlist('instructions[]')
        images = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        tag_names_str = request.form.get('tags', '')
        tag_names = [tag.strip() for tag in tag_names_str.split(',') if tag.strip()]
        stage_ids = request.form.getlist('stage_ids[]')

        # Collect all delete_image flags
        delete_image_flags = {}
        for idx, stage_id in enumerate(stage_ids):
            stage_num = idx + 1
            flag = request.form.get(f'delete_image_{stage_num}', 'false')
            delete_image_flags[stage_num] = flag.lower() == 'true'

        # Process tags
        edit_tag_handler(recipe, tag_names)

        # Process stages and images
        for index, instruction in enumerate(instructions):
            # Determine if this is an existing stage or a new one
            if index < len(stage_ids) and stage_ids[index]:
                # Existing stage
                stage_id = stage_ids[index]
                stage = RecipeStage.query.get(stage_id)
                if stage:
                    stage.instructions = instruction

                    # Check if a new image is uploaded for this stage
                    new_image = images[index] if index < len(images) else None
                    is_new_image_uploaded = new_image and new_image.filename != ''

                    if stage.recipe_images:
                        image = stage.recipe_images[0]  # Assuming one image per stage
                        if delete_image_flags.get(stage.stage_num, False):
                            # Delete the existing image
                            if image.public_id:
                                cloudinary.uploader.destroy(image.public_id)
                            db.session.delete(image)

                            if not is_new_image_uploaded:
                                # Assign placeholder only if no new image is uploaded
                                placeholder_url = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder.png'
                                placeholder_thumbnail = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder.png'
                                recipe_image = RecipeImage(
                                    stage_id=stage.stage_id,
                                    image_url=placeholder_url,
                                    thumbnail_url=placeholder_thumbnail,
                                    alt_text='No description provided',
                                    public_id=None
                                )
                                db.session.add(recipe_image)
                    else:
                        if not delete_image_flags.get(stage.stage_num, False):
                            # No existing image and not marked for deletion, assign placeholder
                            placeholder_url = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder.png'
                            placeholder_thumbnail = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder.png'
                            recipe_image = RecipeImage(
                                stage_id=stage.stage_id,
                                image_url=placeholder_url,
                                thumbnail_url=placeholder_thumbnail,
                                alt_text='No description provided',
                                public_id=None
                            )
                            db.session.add(recipe_image)

                    # Handle new image upload if provided
                    if is_new_image_uploaded:
                        # Upload new image
                        image_url, thumbnail_url, public_id = upload_image(new_image)
                        if image_url:
                            # Delete the old image if exists (already handled above if delete_image_flag is true)
                            if stage.recipe_images:
                                old_image = stage.recipe_images[0]
                                if old_image.public_id:
                                    cloudinary.uploader.destroy(old_image.public_id)
                                db.session.delete(old_image)
                            # Add the new image
                            recipe_image = RecipeImage(
                                stage_id=stage.stage_id,
                                image_url=image_url,
                                thumbnail_url=thumbnail_url,
                                alt_text=alt_texts[index] or 'No description provided',
                                public_id=public_id
                            )
                            db.session.add(recipe_image)
            else:
                # New stage
                new_stage = RecipeStage(
                    recipe=recipe,
                    stage_num=index + 1,  # Temporary assignment; will be corrected below
                    instructions=instruction
                )
                db.session.add(new_stage)
                db.session.flush()  # To get the stage_id

                # Handle image
                if index < len(images):
                    new_image = images[index]
                    if new_image and new_image.filename != '':
                        image_url, thumbnail_url, public_id = upload_image(new_image)
                        if image_url:
                            recipe_image = RecipeImage(
                                stage_id=new_stage.stage_id,
                                image_url=image_url,
                                thumbnail_url=thumbnail_url,
                                alt_text=alt_texts[index] or 'No description provided',
                                public_id=public_id
                            )
                            db.session.add(recipe_image)
                    else:
                        # Assign placeholder
                        placeholder_url = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder.png'
                        placeholder_thumbnail = 'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder.png'
                        recipe_image = RecipeImage(
                            stage_id=new_stage.stage_id,
                            image_url=placeholder_url,
                            thumbnail_url=placeholder_thumbnail,
                            alt_text='No description provided',
                            public_id=None
                        )
                        db.session.add(recipe_image)

        # After processing all stages, reassign stage_num to ensure sequential order
        all_stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).order_by(RecipeStage.stage_num).all()
        for idx, stage in enumerate(all_stages, start=1):
            stage.stage_num = idx

        # Update the is_last_stage flag based on the updated stage_num
        total_stages = len(all_stages)
        for idx, stage in enumerate(all_stages, start=1):
            stage.is_final_stage = (idx == total_stages)

        db.session.commit()

        flash("Recipe has been updated")
        return redirect(url_for('recipe_page', recipe_id=recipe.recipe_id))

    else:
        # GET request: Render the edit form
        all_tags = RecipeTag.query.all()
        tag_dict = {tag.tag_name: None for tag in all_tags}

        return render_template("edit_recipe.html", recipe=recipe, recipes=recipes, tag_dict=tag_dict, user=current_user)


@routes.route("/delete_recipe/<int:recipe_id>")
@login_required
def delete_recipe(recipe_id):
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

    return redirect(url_for('recipes'), user=current_user)