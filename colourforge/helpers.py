"""
Module: helpers.py

Description:
------------
This module provides functions to handle recipe creation, editing, and deletion
within the Colourforge application. It manages interactions with the database,
handles image uploads via Cloudinary, and ensures data integrity through proper
tagging and association of recipe components. The module includes helper
functions to streamline the management of recipe stages, images, and tags,
allowing for both creation and modification workflows.

Functions:
--------------------
- **Recipe Creation:** Handles the creation of new recipes, including
initializing default stages and uploading associated images.

- **Recipe Editing:** Manages the updating of existing recipes, allowing for
modifications
to instructions, images, and tags. Ensures that changes are accurately
reflected in the database and associated services.

- **Recipe Deletion:** Facilitates the removal of recipes and all related data,
ensuring that no orphaned records remain in the database.

- **Image Handling:** Uploads images to Cloudinary, retrieves secure URLs and
thumbnails, and manages the deletion of images from both the database and
Cloudinary.

- **Tag Management:** Adds, edits, and removes tags associated with recipes,
ensuring a consistent tagging system for efficient categorization and
searching.
"""

import os
from flask import request, flash, render_template
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
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder-1.jpg')  # noqa
PLACEHOLDER_THUMBNAIL_URL = (
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder-1.jpg')  # noqa


def recipe_handler(form_data):
    """
    Processes form data to create a new recipe associated with the current
    user.
    Extracts the recipe name and description from the form, saves the recipe to
    the database, and returns the newly created recipe object.

    Args:
        form_data (dict): A dictionary containing form data with keys
        'recipe_name' and 'recipe_desc'.

    Returns:
        Recipe: The newly created Recipe object persisted in the database.
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
    Updates the details of an existing recipe, including its name, description,
    instructions, images, and tags. Processes form data to reflect the changes
    in the database, ensuring that all associations are correctly maintained.

    Args:
        recipe (Recipe): The Recipe object to be updated with new data.
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
    Iterates through a list of tag names, adding each tag to the database if it
    does not already exist. Associates each tag with the specified recipe,
    ensuring that duplication is avoided.

    Args:
        recipe (Recipe): The Recipe object to which tags are being added.
        tag_names (list): A list of tag names to be associated with the recipe.
    """
    MAX_TAG_LENGTH = 20

    if tag_names:
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                if len(tag_name) > MAX_TAG_LENGTH:
                    flash(
                        f"""Tag {tag_name} is too long. Tags must be
                        {MAX_TAG_LENGTH} characters or less.""",
                        category='error'
                    )
                    """
                    Skip over this tag and continue iterating through the
                    rest
                    """

                # Check if tag exists
                tag = RecipeTag.query.filter_by(tag_name=tag_name).first()

                if not tag:
                    tag = RecipeTag(tag_name=tag_name)
                    db.session.add(tag)

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
    Compares the current tags associated with the recipe to the new list of
    tags provided. Adds any new tags that are not already stored by calling
    tag_handler and removes tags that are no longer included in the updated
    list.

    Args:
        recipe (Recipe): The Recipe object whose tags are being edited.
        tag_names (list): A list of new tag names to be associated with the
        recipe.
    """
    # Ensure tag_names is a list and process it
    if tag_names:
        # Strip whitespace and filter out empty tags
        tag_names = [
            tag_name.strip() for tag_name in tag_names if tag_name.strip()
        ]

    # Retrieve current tags associated with the recipe
    current_tags = EntityTag.query.filter_by(recipe_id=recipe.recipe_id).all()
    current_tag_names = {
        tag.recipe_tag.tag_name for tag in current_tags if tag.recipe_tag
    }

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
    db.session.commit()

    # Use tag_handler to add new tags
    if tags_to_add:
        tag_handler(recipe, list(tags_to_add))


def upload_image(image):
    """
    Handles the uploading of an image file to Cloudinary. Retrieves the secure
    URL, thumbnail URL, and public ID of the uploaded image. If no image is
    provided, or validation checks fail returns None for all values.

    Args:
        image (FileStorage): The image file to be uploaded.

    Returns:
        tuple: A tuple containing (image_url, thumbnail_url, public_id).
               Returns (None, None, None) if no image is provided.
    """
    if image.filename == '':
        flash("Your image needs a filename", category='error')
        return None, None, None

    # Find Filesize
    image.stream.seek(0, os.SEEK_END)
    size = image.stream.tell()
    image.stream.seek(0)

    if size >= 10 * 1024 * 1024:
        flash(
            """Your image filesize is too large, a placeholder has been
            used in its place""",
            category='error')
        return PLACEHOLDER_IMAGE_URL, PLACEHOLDER_THUMBNAIL_URL, None

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


def remove_recipe(recipe):
    """
    Removes the specified recipe from the DB, including all related stages,
    images, and tag associations. Ensures that no orphaned records remain by
    cascading deletions.

    Args:
        recipe (Recipe): The Recipe object to be deleted.
    """
    # Delete associated stages and images
    stages = RecipeStage.query.filter_by(recipe_id=recipe.recipe_id).all()
    for stage in stages:
        for image in stage.recipe_images:
            delete_image(image)  # Use the helper to handle image deletion
        db.session.delete(stage)  # Delete stage record

    # Delete associated tags
    EntityTag.query.filter_by(recipe_id=recipe.recipe_id).delete()

    # Finally, delete the recipe itself
    db.session.delete(recipe)
    db.session.commit()


def delete_image(image):
    """
    Deletes the image from Cloudinary using its public ID, unless it is a
    placeholder image. Once done this then removes the image record from the
    database to ensure we're not storing unneeded records.

    Args:
        image (RecipeImage): The RecipeImage object to be deleted.
    """
    if image.public_id is not None and not image.public_id.startswith(
        'placeholder'
         ):
        cloudinary.uploader.destroy(image.public_id)
    db.session.delete(image)


def assign_placeholder_image(stage):
    """
    Where no image is provided for a recipe stage, this function
    assigns a placeholder image to ensure that every stage has an associated
    image.

    Args:
        stage (RecipeStage): The RecipeStage object to which the placeholder
        image is assigned.
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
    Iterates through the provided instructions, uploads associated images, and
    creates corresponding RecipeStage and RecipeImage records in the database.
    Assigns placeholder images if no image is provided for a stage.

    Args:
        recipe (Recipe): The Recipe object to which stages are being added.
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
        if image and image.filename != '':
            image_url, thumbnail_url, public_id = upload_image(image)

        # If an image was not added, use a placeholder
        else:
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
    Deletes all existing stages and images associated with the recipe, then
    recreates them based on the updated instructions and images provided
    through the form data. Ensures that the recipe's structure remains
    consistent and up-to-date.

    Args:
        recipe (Recipe): The Recipe object whose stages are being edited.
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
            if image.public_id and not image.public_id.startswith(
                                                                  'placeholder'
                                                                  ):
                cloudinary.uploader.destroy(image.public_id)
            db.session.delete(image)
        db.session.delete(stage)
    db.session.commit()

    # Add new stages and images using the existing instruction_handler
    instruction_handler(recipe, instructions, image_files, alt_texts)


def collect_delete_image_flags(stage_ids):
    """
    Checks form data to determine which images associated with recipe stages
    should be deleted. Returns a dictionary mapping stage IDs to boolean flags
    indicating the deletion intent.

    Args:
        stage_ids (list): A list of stage IDs to check for deletion flags.

    Returns:
        dict: A dictionary mapping each stage ID to a boolean indicating
        whether its image should be deleted (`True`) or retained (`False`).
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
    Handles the processing of recipe stages and their associated images
    during the editing workflow. This includes deleting stages no longer
    present, updating existing stages with new instructions and images, and
    adding new stages as needed. Ensures that the recipe's stages are correctly
    ordered and that the final stage is appropriately flagged.

    Args:
        recipe (Recipe): The Recipe object being edited.
        instructions (list): A list of instructions for each stage.
        images (list): A list of image files for each stage.
        alt_texts (list): A list of alt texts for each image.
        stage_ids (list): A list of existing stage IDs.
        delete_image_flags (dict): Flags indicating whether an image should be
        deleted.
    """
    existing_stage_ids = set(stage_ids)
    current_stages = RecipeStage.query.filter_by(
        recipe_id=recipe.recipe_id
        ).all()

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
    all_stages = RecipeStage.query.filter_by(
        recipe_id=recipe.recipe_id
    ).order_by(
        RecipeStage.stage_num
    ).all()

    # Assign stage_num values and set the final stage flag
    stage_num = 1
    for stage in all_stages:
        stage.stage_num = stage_num
        stage.is_final_stage = (stage_num == len(all_stages))
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
    Modifies the instructions of an existing stage and handles the updating or
    deletion of its associated image based on user input. If a new image is
    provided, it replaces the old image; otherwise, it assigns a placeholder
    image if flagged for deletion.

    Args:
        stage_id (int): The unique identifier of the stage to be updated.
        instruction (str): The updated instruction text for the stage.
        image (FileStorage): The new image file to be associated with the
        stage.
        delete_image_flags (dict): A dictionary mapping stage IDs to boolean
        flags indicating whether their images should be deleted.
        alt_texts (list): A list of alt texts corresponding to each image.
        index (int): The index of the current stage being processed.
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
    Checks if the image associated with the stage should be deleted based on
    user input. If deletion is requested and no new image is provided, assigns
    a placeholder image. Otherwise, retains or updates the existing image as
    appropriate.

    Args:
        stage (RecipeStage): The stage object whose image is being handled.
        new_image (FileStorage): The new image file, if uploaded.
        delete_image_flags (dict): Flags indicating whether the current image
        should be deleted.
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
    If the user has not requested deletion of the image and no new image is
    provided, assigns a default placeholder image to the stage to maintain
    consistency.

    Args:
        stage (RecipeStage): The stage object to assign the placeholder image.
        new_image (FileStorage): The new image file, if uploaded.
        delete_image_flags (dict): Flags indicating whether the current image
        should be deleted.
        alt_texts (list): A list of alt texts for each image.
        index (int): The index of the current stage being processed.
    """
    if not delete_image_flags.get(stage.stage_num, False):
        assign_placeholder_image(stage)


def handle_new_image_upload(stage, new_image, alt_texts, index):
    """
    Handles the uploading of a new image to Cloudinary, deletes the old image
    if one exists, and associates the newly uploaded image with the recipe
    stage.

    Args:
        stage (RecipeStage): The stage object to associate with the new image.
        new_image (FileStorage): The new image file to be uploaded.
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
    Creates a new RecipeStage record with the provided instruction and
    associates it with an image. If no image is provided, assigns a placeholder
    image to the stage.

    Args:
        recipe (Recipe): The Recipe object to which the new stage is being
        added.
        index (int): The index of the new stage being created.
        instruction (str): The instruction text for the new stage.
        images (list): A list of image files for each stage.
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
    Determines whether an image has been uploaded for the new stage and handles
    its assignment. If no image is provided, assigns a placeholder image.

    Args:
        images (list): A list of image files for each stage.
        index (int): The index of the current stage being processed.
        new_stage (RecipeStage): The newly created stage object to update.
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
    Creates a new RecipeImage record linking the uploaded image to the
    specified recipe stage, including the image URL, thumbnail URL, alt text,
    and public
    ID.

    Args:
        stage (RecipeStage): The RecipeStage object to associate with the
        image.
        image_url (str): The secure URL of the uploaded image.
        thumbnail_url (str): The thumbnail URL of the uploaded image.
        alt_texts (list): A list of alt texts corresponding to each image.
        index (int): The index of the current stage being processed.
        public_id (str): The public ID of the uploaded image in Cloudinary.
    """
    recipe_image = RecipeImage(
        stage_id=stage.stage_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        alt_text=alt_texts[index] or 'No description provided',
        public_id=public_id
    )
    db.session.add(recipe_image)
