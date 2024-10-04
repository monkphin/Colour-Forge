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


@app.route("/")
def home():
    recipes = list(Recipes.query.order_by(Recipes.recipe_name).all())
    return render_template("home.html", recipes=recipes, tag_dict={})


@app.route("/recipes")
def recipes():
    recipes = list(Recipes.query.order_by(Recipes.recipe_name).all())
    
    return render_template("recipes.html", recipes=recipes, tag_dict={})


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":        

        # Create the Recipe entry in the Database
        recipe = Recipes(
            recipe_name=request.form.get('recipe_name'),
            recipe_desc=request.form.get('recipe_desc'),
        )
        db.session.add(recipe)
        db.session.commit()

        # Used to check whats being output. Delete before Prod
        print("Recipe Name:", request.form.get('recipe_name'))
        print("Recipe Description:", request.form.get('recipe_desc'))

        # initialise variables
        instructions = request.form.getlist('instructions[]')
        image_files = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        recipe_tags = request.form.getlist('recipe_tags[]')
        tag_names_str = request.form.get('tags', '')
        tag_names = tag_names_str.split(',') 
        stage_num = 1

        # loop through instructions index
        i = 0
        for instruction in instructions: 
            # check if the current instruction has an image
            image = image_files[i] if i < len(image_files) else None
            # check if the current image/instruction has an alt text. 
            alt_text = alt_texts[i] if i < len(alt_texts) else "No description provided"

            # Add to cloudinary if image is present
            image_url = None
            thumbnail_url = None
            if image and image.filename != '':
                upload_result = cloudinary.uploader.upload(image) 
                image_url = upload_result.get('secure_url')
                thumbnail_url, options = cloudinary_url(
                    upload_result['public_id'], 
                    format="jpg", 
                    crop="fill", 
                    width=200, 
                    height=200
                    )

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

            # Used to check whats being output. Delete before Prod
            print(stage_num)
            instructions = request.form.getlist('instructions[]')
            print("Instructions List:", instructions)
            print("Is Final Stage?:", request.form.get('is_final_stage'))
        
            # If an image was added, create the entry in the DB
            if image_url: 
                recipe_image = RecipeImages(
                    stage_id = recipe_stage.stage_id,
                    image_url = image_url,
                    thumbnail_url = thumbnail_url,
                    alt_text = alt_text
                )
                db.session.add(recipe_image)

            # Used to check whats being output. Delete before Prod
            print("Image names:", [image.filename for image in image_files])
            print("alt text:", alt_texts)   

            # Tag handler
            # Process each submitted tag
            if tag_names:
                for tag_name in tag_names:
                    tag_name = tag_name.strip()
                    if tag_name:
                        tag = RecipeTags.query.filter_by(tag_name=tag_name).first()

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

            for tag_name in tag_names:
                tag = RecipeTags.query.filter_by(tag_name=tag_name).first()

                if not tag:
                    tag = RecipeTags(tag_name=tag_name)
                    db.session.add(tag)
                    db.session.flush()  # Make sure tag_id is generated before proceeding

                    # Associate the tag with the recipe only if it's not already associated
                    entity_tag = EntityTags(
                        recipe_id=recipe.recipe_id, 
                        tag_id=tag.tag_id, 
                        entity_type='recipe'
                        )
                    
                    db.session.add(entity_tag)

            stage_num += 1
            i += 1

            db.session.commit()

            print(f"Full form content {request.form}")

        return redirect("recipes")

    else:
        # Get collection of existing tags as a variable and iterate through
        # to create a dictionary to match how materialize is handling chips/tags.     
        all_tags = RecipeTags.query.all()
        tag_dict = {tag.tag_name: None for tag in all_tags}

        return render_template("add_recipe.html", tag_dict=tag_dict)
    return render_template("add_recipe.html")