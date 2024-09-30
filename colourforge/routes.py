from flask import (
    Flask, flash, render_template, 
    request, redirect, url_for)
from colourforge import app, db, cloudinary, cloudinary_url
from colourforge.models import Recipes, RecipeStages, RecipeImages


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")


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

        # initialise variables
        instructions = request.form.getlist('instructions[]')
        image_files = request.files.getlist('images[]')
        alt_texts = request.form.getlist('image_desc[]')
        stage_num = 1

        # loop through instructions index
        i = 0
        for instruction in instructions: 
            # check if the current instruction has an image
            image = image_files[i] if i < len(image_files) else None
            # check if the current image/instruction has an alt text. 
            alt_text = alt_texts[i] if i < len(alt_texts) else "No description provided"

            # Add to cloudinary
            image_url = None
            thumbnail_url = None
            if image and image.filename != '':
                upload_result = cloudinary.uploader.upload(image) 
                image_url = upload_result.get('secure_url')
                thumbnail_url, options = cloudinary_url(
                    upload_result['public_id'], format="jpg", crop="fill", width=100, height=100)


            # Determine if this is the last stage
            is_final_stage = (instruction == instructions[-1])

            # Create Recipe Stage entry in Database
            recipe_stage = RecipeStages (
                recipe=recipe,
                stage_num=stage_num,
                instructions=instruction,
                is_final_stage=is_final_stage

            )
            db.session.add(recipe_stage)
            db.session.flush() 
        
            # If an image was added, create the entry in the DB
            if image_url: 
                recipe_image = RecipeImages(
                    stage_id=recipe_stage.stage_id,
                    image_url=image_url,
                    thumbnail_url = thumbnail_url,
                    alt_text = alt_text
                )
                db.session.add(recipe_image)

            stage_num += 1
            i += 1

        db.session.commit()

        print("Recipe Name:", request.form.get('recipe_name'))
        print("Recipe Description:", request.form.get('recipe_desc'))
        print(stage_num-1)
        instructions = request.form.getlist('instructions[]')
        print("Instructions List:", instructions)
        print("Is Final Stage?:", request.form.get('is_final_stage'))
        print("Image names:", [image.filename for image in image_files])
        print("alt text:", alt_texts)

        return redirect("recipes")
    return render_template("add_recipe.html")
