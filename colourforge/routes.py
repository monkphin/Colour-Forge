from flask import (
    Flask, flash, render_template, 
    request, redirect, url_for)
from colourforge import app, db, cloudinary, cloudinary_url
from colourforge.models import (Recipes, 
                                RecipeStages, 
                                RecipeImages, 
                                RecipeTags, 
                                EntityTags
                                )


# Helper functions


def recipe_handler(form_data):
    recipe = Recipes(
        recipe_name=request.form.get('recipe_name'),
        recipe_desc=request.form.get('recipe_desc'),
    )
    db.session.add(recipe)
    db.session.commit()    
    return recipe


def upload_image(image):
    if image and image.filename != '':
        upload_result = cloudinary.uploader.upload(image) 
        image_url = upload_result.get('secure_url')
        public_id = upload_result.get('public_id')
        thumbnail_url, options = cloudinary_url(
            public_id, 
            format="jpg", 
            crop="fill", 
            width=200, 
            height=200
            )
        return image_url, thumbnail_url, public_id
    else:
        return None, None, None


def instruction_handler(recipe, instructions, image_files, alt_texts):
    i = 0
    stage_num = 1
    for instruction in instructions: 
        # check if the current instruction has an image
        image = image_files[i] if i < len(image_files) else None
        # check if the current image/instruction has an alt text. 
        alt_text = alt_texts[i] if i < len(
            alt_texts) else "No description provided"
        
        #upload to cloudinary if present
        image_url, thumbnail_url, public_id  = upload_image(image)

                    # If an image was added, create the entry in the DB
        if not image_url:
            image_url = (
                'https://res.cloudinary.com/dlmbpbtfx/image/upload/'
                'v1728052910/placeholder.png'
                ),
            thumbnail_url = (
                'https://res.cloudinary.com/dlmbpbtfx/image/upload/'
                'c_fill,h_200,w_200/placeholder.png'
                ),
            alt_text = 'Placeholder Image'   
            public_id = None           
    
        # Determine if this is the last stage
        is_final_stage = (instruction == instructions[-1])

        # Create Recipe Stage entry in Database
        recipe_stage = RecipeStages (
            recipe = recipe,
            stage_num = stage_num,
            instructions = instruction,
            is_final_stage = is_final_stage

        )
        db.session.add(recipe_stage)
        db.session.flush() 
        
        recipe_image = RecipeImages(
            stage_id = recipe_stage.stage_id,
            image_url = image_url,
            thumbnail_url = thumbnail_url,
            alt_text = alt_text,
            public_id = public_id
            )
        db.session.add(recipe_image)

        i += 1
        stage_num += 1


def edit_instruction_handler(recipe, instructions, image_files, alt_texts):
    # fetch existing stages/images
    existing_stages = RecipeStages.query.filter_by(recipe_id=recipe.recipe_id).all()

    # Delete existing stages and images
    for stage in existing_stages:
        images = RecipeImages.query.filter_by(stage_id=stage.stage_id).all()
        for image in images:
            if image.public_id:
                try:
                    cloudinary.uploader.destroy(image.public_id)
                except cloudinary.exceptions.Error as e:
                    print(f"Error deleting image {image.public_id} {str(e)}")
            db.session.delete(image)        
        db.session.delete(stage)
    db.session.commit()

    # Add new stages and images using the existing instruction_handler
    instruction_handler(recipe, instructions, image_files, alt_texts)


def tag_handler(recipe, tag_names):
    if tag_names:
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = RecipeTags.query.filter_by(
                    tag_name=tag_name).first()

                if not tag:
                    tag = RecipeTags(tag_name=tag_name)
                    db.session.add(tag)
                    db.session.commit()

                # Check if the tag is already associated with this recipe
                existing_tag = EntityTags.query.filter_by(
                    recipe_id=recipe.recipe_id, 
                    tag_id=tag.tag_id
                    ).first()
                
                if not existing_tag:
                    # Associate the tag with the recipe
                    entity_tag = EntityTags(
                        recipe_id=recipe.recipe_id, 
                        tag_id=tag.tag_id, 
                        entity_type='recipe'
                        )
                    db.session.add(entity_tag)

    db.session.commit()


def edit_tag_handler(recipe, tag_names):
    # Remove existing tags
    EntityTags.query.filter_by(recipe_id=recipe.recipe_id).delete()
    db.session.commit()

    # Add new tags using existing tag_handler
    tag_handler(recipe, tag_names)


# App routes for flask functionality 

# Routes that only render content
@app.route("/")
def home():
    recipes = list(Recipes.query.order_by(Recipes.recipe_name).all())
    return render_template("home.html", recipes=recipes, tag_dict={})


@app.route("/recipes")
def recipes():
    recipes = list(Recipes.query.order_by(Recipes.recipe_name).all())

    return render_template("recipes.html", recipes=recipes, tag_dict={})


@app.route("/recipe_page/<int:recipe_id>")
def recipe_page(recipe_id):
    recipe=Recipes.query.get_or_404(recipe_id)
    referrer = request.referrer # changed because I was working off documentation 
    # I found where referer was misspelled for legacy reasons and this annoyed me. 
    # Found other, less irritating documentation which pointed to using this 
    # approach instead. 

    return render_template(
        'recipe_page.html', 
        recipe=recipe, 
        referrer=referrer, 
        tag_dict={}
        )

# Routes that render and write content 
@app.route("/add_recipe", methods=["GET", "POST"])
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

        # Used to check whats being output. Delete before Prod
        print("Image names:", [image.filename for image in image_files])
        print("alt text:", alt_texts)  
        print(f"Full form content {request.form}")

        return redirect("recipes")

    else:
        # Get collection of existing tags as a variable and iterate through
        # to create a dictionary to match how materialize is handling chips/tags.     
        all_tags = RecipeTags.query.all()
        tag_dict = {tag.tag_name: None for tag in all_tags}

        return render_template("add_recipe.html", tag_dict=tag_dict)


@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe=Recipes.query.get_or_404(recipe_id)
    recipes=list(Recipes.query.order_by(Recipes.recipe_id).all())

    if request.method == "POST":
        recipe.recipe_name=request.form.get('recipe_name')
        recipe.recipe_desc=request.form.get('recipe_desc')

        # init variables from form data
        instructions = request.form.getlist('instructions[]')
        images = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        tag_names_str = request.form.get('tags', '')
        tag_names = tag_names_str.split(',')

        # Update stages and images
        edit_instruction_handler(recipe, instructions, images, alt_texts)

        print("these are the pulled Instructions: ", instructions)
        print("Image names:", [image.filename for image in images])

        #update_tags
        edit_tag_handler(recipe, tag_names)

        db.session.commit()

    return render_template(
        'edit_recipe.html', 
        recipe=recipe, 
        recipes=recipes, 
        tag_dict={}
        )

@app.route("/delete_recipe/<int:recipe_id>")
def delete_recipe(recipe_id):
    recipe = Recipes.query.get_or_404(recipe_id)

    # Delete associated stages and images
    stages = RecipeStages.query.filter_by(recipe_id=recipe.recipe_id).all()
    for stage in stages:
        images = RecipeImages.query.filter_by(stage_id=stage.stage_id).all()
        for image in images:
            if image.public_id:
                try:
                    # Delete the image from Cloudinary using public_id
                    cloudinary.uploader.destroy(image.public_id)
                except cloudinary.exceptions.Error as e:
                    print(f"Error deleting image {image.public_id}: {str(e)}")
            db.session.delete(image)  # Delete image record from the database
        db.session.delete(stage)  # Delete stage record from the database

    # Delete associated tags
    EntityTags.query.filter_by(recipe_id=recipe.recipe_id).delete()

    # Delete the recipe itself
    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for('recipes'))