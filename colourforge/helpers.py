from flask import request
from colourforge import app, db, cloudinary, cloudinary_url
from colourforge.models import (Recipe, 
                                RecipeStage, 
                                RecipeImage, 
                                RecipeTag, 
                                EntityTag
                                )


def recipe_handler(form_data):
    recipe = Recipe(
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
        recipe_stage = RecipeStage (
            recipe = recipe,
            stage_num = stage_num,
            instructions = instruction,
            is_final_stage = is_final_stage

        )
        db.session.add(recipe_stage)
        db.session.flush() 
        
        recipe_image = RecipeImage(
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
    existing_stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).all()

    # Delete existing stages and images
    for stage in existing_stages:
        images = RecipeImage.query.filter_by(stage_id=stage.stage_id).all()
        for image in images:
            if image.public_id:
                cloudinary.uploader.destroy(image.public_id)
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
                tag = RecipeTag.query.filter_by(tag_name=tag_name).first()

                if not tag:
                    tag = RecipeTag(tag_name=tag_name)
                    db.session.add(tag)
                    # Do not commit here to batch transactions

                # Check if the tag is already associated with this recipe
                existing_tag = EntityTag.query.filter_by(
                    recipe_id=recipe.recipe_id, 
                    tag_id=tag.tag_id
                ).first()
                
                if not existing_tag and tag:
                    # Associate the tag with the recipe
                    entity_tag = EntityTag(
                        recipe_id=recipe.recipe_id, 
                        tag_id=tag.tag_id, 
                        entity_type='recipe'
                    )
                    db.session.add(entity_tag)

    db.session.commit()

def edit_tag_handler(recipe, tag_names):
    if tag_names is not None:
        # Remove existing tags
        EntityTag.query.filter_by(recipe_id=recipe.recipe_id).delete()
        db.session.commit()

        # Add new tags using existing tag_handler
        tag_handler(recipe, tag_names)