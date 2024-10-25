from flask import request, render_template
from colourforge import app, db, cloudinary, cloudinary_url
from flask_login import current_user
from colourforge.models import (
    Recipe,
    RecipeStage,
    RecipeImage,
    RecipeTag,
    EntityTag
)

# Common variables. 
# I have been advise by my mentor that URLs can be longer than 79 chars. 
PLACEHOLDER_IMAGE_URL = (
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder.png')
PLACEHOLDER_THUMBNAIL_URL = (
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder.png')


def recipe_handler(form_data):
    """
    Handles creating a new recipe object in the database.

    Args:
        form_data (dict): Data from the form to create a new recipe, including
        recipe name and description.

    Returns:
        Recipe: The newly created recipe object.
    """
    recipe = Recipe(
        user_id=current_user.id,
        recipe_name=request.form.get('recipe_name'),
        recipe_desc=request.form.get('recipe_desc'),
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe


def handle_recipe_edit_post(recipe):
    """
    Handles updating recipe details, tags, and stages based on submitted
    form data.

    Args:
        recipe (Recipe): The recipe object being edited.
    """
    # Get form fields and store as variables.
    recipe.recipe_name = request.form.get('recipe_name')
    recipe.recipe_desc = request.form.get('recipe_desc')

    # Initialize variables from form data.
    instructions = request.form.getlist('instructions[]')
    images = request.files.getlist('images[]')
    alt_texts = request.form.getlist('image_desc[]')
    tag_names_str = request.form.get('tags', '')
    tag_names = [
        tag.strip() for tag in tag_names_str.split(',') if tag.strip()
    ]
    stage_ids = request.form.getlist('stage_ids[]')

    delete_image_flags = collect_delete_image_flags(stage_ids)

    # Process tags
    edit_tag_handler(recipe, tag_names)

    # Process stages and images
    process_stages_and_images(
        recipe,
        instructions,
        images,
        alt_texts,
        stage_ids,
        delete_image_flags
        )

    db.session.commit()


def tag_handler(recipe, tag_names):
    """
    Handles adding tags to a recipe. If the tag does not exist, it creates it.

    Args:
        recipe (Recipe): The recipe object to which tags are being added.
        tag_names (list): A list of tag names to be associated with the recipe.
    """
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
    """
    Handles editing tags for a recipe by adding new tags and removing those
    that are not in the updated tag list.

    Args:
        recipe (Recipe): The recipe object whose tags are being edited.
        tag_names (list): A list of new tag names to be associated with
        the recipe.
    """
    # Retrieve current tags associated with the recipe
    current_tags = EntityTag.query.filter_by(
        recipe_id=recipe.recipe_id).all()
    current_tag_names = {
        tag.recipe_tag.tag_name for tag in current_tags if tag.recipe_tag}

    # Determine tags to be added and removed
    new_tag_names = set(tag_names)
    tags_to_remove = current_tag_names - new_tag_names
    tags_to_add = new_tag_names - current_tag_names

    # Remove tags that are no longer needed
    for tag_name in tags_to_remove:
        tag = RecipeTag.query.filter_by(tag_name=tag_name).first()
        if tag:
            entity_tag = EntityTag.query.filter_by(
                recipe_id=recipe.recipe_id, tag_id=tag.tag_id).first()
            if entity_tag:
                db.session.delete(entity_tag)

    # Add new tags
    for tag_name in tags_to_add:
        tag = RecipeTag.query.filter_by(tag_name=tag_name).first()
        if not tag:
            tag = RecipeTag(tag_name=tag_name)
            db.session.add(tag)
            db.session.flush()  # Ensure tag ID is available immediately

        # Create the association between the recipe and the tag
        entity_tag = EntityTag(
            recipe_id=recipe.recipe_id,
            tag_id=tag.tag_id,
            entity_type='recipe'
            )
        db.session.add(entity_tag)

    db.session.commit()


def upload_image(image):
    """
    Uploads an image to Cloudinary and retrieves URLs for full and thumbnail
    versions.

    Args:
        image (FileStorage): The image file to be uploaded.

    Returns:
        tuple: A tuple containing (image_url, thumbnail_url, public_id).
        Returns None for all if no image is provided.
    """
    if image and image.filename != '':
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result.get('secure_url')
        public_id = upload_result.get('public_id')
        thumbnail_url, _ = cloudinary_url(
            public_id,
            format="jpg",
            crop="fill",
            width=200,
            height=200
        )
        return image_url, thumbnail_url, public_id
    return None, None, None


def delete_image(image):
    """
    Deletes an image from Cloudinary and removes it from the database.

    Args:
        image (RecipeImage): The image object to be deleted.
    """
    if image.public_id and image.public_id.startswith('placeholder'):
        cloudinary.uploader.destroy(image.public_id)
    db.session.delete(image)


def assign_placeholder_image(stage):
    """
    Assigns a placeholder image to a recipe stage in the database.

    Args:
        stage (RecipeStage): The stage object to assign the placeholder image.
    """
    placeholder_url = PLACEHOLDER_IMAGE_URL
    placeholder_thumbnail = PLACEHOLDER_THUMBNAIL_URL
    recipe_image = RecipeImage(
        stage_id=stage.stage_id,
        image_url=placeholder_url,
        thumbnail_url=placeholder_thumbnail,
        alt_text='No description provided',
        public_id=None
    )
    db.session.add(recipe_image)


def instruction_handler(
    recipe,
    instructions,
    image_files,
    alt_texts
):
    """
    Handles creating recipe stages and associated images in the database.

    Args:
        recipe (Recipe): The recipe object to which stages are being added.
        instructions (list): A list of instructions for each recipe stage.
        image_files (list): A list of image files associated with each stage.
        alt_texts (list): A list of alt texts for each image.
    """
    i = 0
    stage_num = 1
    for instruction in instructions:
        # Check if the current instruction has an image
        image = image_files[i] if i < len(image_files) else None
        # Check if the current image/instruction has an alt text.
        if i < len(alt_texts):
            alt_text = alt_texts[i]
        else:
            alt_text = "No description provided"

        # Upload to Cloudinary if present
        image_url, thumbnail_url, public_id = upload_image(image)

        # If an image was not added, use a placeholder
        if not image_url:
            image_url = PLACEHOLDER_IMAGE_URL
            thumbnail_url = PLACEHOLDER_THUMBNAIL_URL
            alt_text = 'Default Image'
            public_id = None

        # Determine if this is the last stage
        is_final_stage = (instruction == instructions[-1])

        # Create Recipe Stage entry in the database
        recipe_stage = RecipeStage(
            recipe=recipe,
            stage_num=stage_num,
            instructions=instruction,
            is_final_stage=is_final_stage
        )
        db.session.add(recipe_stage)
        db.session.flush()

        # Create Recipe Image entry in the database
        recipe_image = RecipeImage(
            stage_id=recipe_stage.stage_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            alt_text=alt_text,
            public_id=public_id
        )
        db.session.add(recipe_image)

        i += 1
        stage_num += 1


def edit_instruction_handler(recipe, instructions, image_files, alt_texts):
    """
    Handles editing recipe stages and images by deleting existing stages and
    adding new ones.

    Args:
        recipe (Recipe): The recipe object whose stages are being edited.
        instructions (list): A list of new instructions for each recipe stage.
        image_files (list): A list of new image files associated with each
        stage.
        alt_texts (list): A list of new alt texts for each image.
    """
    # Fetch existing stages/images
    existing_stages = (RecipeStage.query
                       .filter_by(recipe_id=recipe.recipe_id)
                       .all())

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


def collect_delete_image_flags(stage_ids):
    """
    Collects flags for whether images should be deleted for each stage.

    Args:
        stage_ids (list): A list of stage IDs to check for deletion flags.

    Returns:
        dict: A dictionary mapping stage IDs to deletion flags.
    """
    i = 0
    delete_image_flags = {}
    for stage_id in stage_ids:
        flag = request.form.get(f'delete_image_{i + 1}', 'false')
        delete_image_flags[stage_id] = flag.lower() == 'true'
        i += 1
    return delete_image_flags


def process_stages_and_images(
        recipe,
        instructions,
        images,
        alt_texts,
        stage_ids,
        delete_image_flags
        ):
    """
    Processes stages and images for a recipe during editing, including adding,
    deleting, or updating stages.

    Args:
        recipe (Recipe): The recipe object being edited.
        instructions (list): A list of instructions for each stage.
        images (list): A list of images for each stage.
        alt_texts (list): A list of alt texts for each image.
        stage_ids (list): A list of existing stage IDs.
        delete_image_flags (dict): Flags indicating whether an image should be
        deleted.
    """
    existing_stage_ids = set(stage_ids)
    current_stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).all()

    # Delete stages that are no longer in the updated list
    for stage in current_stages:
        if str(stage.stage_id) not in existing_stage_ids:
            for image in stage.recipe_images:
                delete_image(image)
            db.session.delete(stage)

    db.session.flush()

    # Update or create stages
    i = 0
    for instruction in instructions:
        if i < len(stage_ids) and stage_ids[i]:
            update_existing_stage(
                stage_ids[i],
                instruction,
                images,
                i,
                delete_image_flags,
                alt_texts
                )
        else:
            create_new_stage(recipe, i, instruction, images, alt_texts)
        i += 1

    # **Re-sort stages after updates**
    all_stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).order_by(RecipeStage.stage_num).all()
    
    # Assign stage_num values and set the final stage flag
    stage_num = 1
    for stage in all_stages:
        stage.stage_num = stage_num
        stage.is_final_stage = (stage_num == len(all_stages))  # Last stage flag
        stage_num += 1

    db.session.commit()


def update_existing_stage(
        stage_id,
        instruction,
        images,
        index,
        delete_image_flags,
        alt_texts
        ):
    """
    Updates an existing stage with new instructions and optionally updates its
    image.

    Args:
        stage_id (int): The ID of the stage to update.
        instruction (str): The updated instruction for the stage.
        images (list): A list of images for each stage.
        index (int): The index of the current stage being updated.
        delete_image_flags (dict): Flags indicating whether an image should be
        deleted.
        alt_texts (list): A list of alt texts for each image.
    """
    stage = RecipeStage.query.get(stage_id)
    if stage:
        stage.instructions = instruction
        new_image = images[index] if index < len(images) else None
        is_new_image_uploaded = new_image and new_image.filename != ''

        if stage.recipe_images:
            handle_existing_image(
                stage,
                new_image,
                delete_image_flags,
                alt_texts,
                index
                )
        else:
            handle_missing_image(
                stage,
                new_image,
                delete_image_flags,
                alt_texts,
                index
                )

        if is_new_image_uploaded:
            handle_new_image_upload(stage, new_image, alt_texts, index)


def handle_existing_image(
        stage,
        new_image,
        delete_image_flags,
        alt_texts,
        index
        ):
    """
    Handles updating or deleting an existing image for a stage.

    Args:
        stage (RecipeStage): The stage object to update.
        new_image (FileStorage): The new image file.
        delete_image_flags (dict): Flags indicating whether an image should be
        deleted.
        alt_texts (list): A list of alt texts for each image.
        index (int): The index of the current stage being processed.
    """
    image = stage.recipe_images[0]  # Assuming one image per stage
    if delete_image_flags.get(stage.stage_num, False):
        delete_image(image)
        if not (new_image and new_image.filename != ''):
            assign_placeholder_image(stage)


def handle_missing_image(
        stage,
        new_image,
        delete_image_flags,
        alt_texts,
        index
        ):
    """
    Handles the case where a stage is missing an image and no new image is
    provided.

    Args:
        stage (RecipeStage): The stage object to update.
        new_image (FileStorage): The new image file.
        delete_image_flags (dict): Flags indicating whether an image should be
        deleted.
        alt_texts (list): A list of alt texts for each image.
        index (int): The index of the current stage being processed.
    """
    if not delete_image_flags.get(stage.stage_num, False):
        assign_placeholder_image(stage)


def handle_new_image_upload(stage, new_image, alt_texts, index):
    """
    Handles uploading a new image for a stage and updating the database.

    Args:
        stage (RecipeStage): The stage object to update.
        new_image (FileStorage): The new image file to upload.
        alt_texts (list): A list of alt texts for each image.
        index (int): The index of the current stage being processed.
    """
    image_url, thumbnail_url, public_id = upload_image(new_image)
    if image_url:
        if stage.recipe_images:
            old_image = stage.recipe_images[0]
            delete_image(old_image)
        add_new_image(
            stage,
            image_url,
            thumbnail_url,
            alt_texts,
            index,
            public_id
            )


def create_new_stage(recipe, index, instruction, images, alt_texts):
    """
    Creates a new recipe stage and associates it with the recipe.

    Args:
        recipe (Recipe): The recipe object to which the new stage is
        being added.
        index (int): The index of the new stage being created.
        instruction (str): The instruction for the new stage.
        images (list): A list of images for each stage.
        alt_texts (list): A list of alt texts for each image.
    """
    new_stage = RecipeStage(
        recipe=recipe,
        stage_num=index + 1,
        instructions=instruction
    )
    db.session.add(new_stage)
    db.session.flush()

    handle_new_stage_image(images, index, new_stage, alt_texts)


def handle_new_stage_image(images, index, new_stage, alt_texts):
    """
    Handles assigning an image to a newly created recipe stage.

    Args:
        images (list): A list of images for each stage.
        index (int): The index of the current stage being processed.
        new_stage (RecipeStage): The new stage object to update.
        alt_texts (list): A list of alt texts for each image.
    """
    if index < len(images):
        new_image = images[index]
        if new_image and new_image.filename != '':
            image_url, thumbnail_url, public_id = upload_image(new_image)
            if image_url:
                add_new_image(
                    new_stage,
                    image_url,
                    thumbnail_url,
                    alt_texts,
                    index,
                    public_id
                    )
        else:
            assign_placeholder_image(new_stage)


def add_new_image(
    stage,
    image_url,
    thumbnail_url,
    alt_texts,
    index,
    public_id
):
    """
    Adds a new image to a recipe stage in the database.

    Args:
        stage (RecipeStage): The stage object to associate with the image.
        image_url (str): The URL of the uploaded image.
        thumbnail_url (str): The thumbnail URL of the uploaded image.
        alt_texts (list): A list of alt texts for each image.
        index (int): The index of the current stage being processed.
        public_id (str): The public ID of the uploaded image.
    """
    recipe_image = RecipeImage(
        stage_id=stage.stage_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        alt_text=alt_texts[index] or 'No description provided',
        public_id=public_id
    )
    db.session.add(recipe_image)
