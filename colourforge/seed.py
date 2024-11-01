"""
Module: default_recipe.py

Description:
------------
This module provides functionality to create a default recipe for new users
of the Colourforge application. The `create_default_recipe` function creates a
demo recipe complete with predefined stages, images, and tags to guide users
through the application's features. This setup ensures that new users have a
reference point and can easily understand how to interact with recipes, stages
and associated media.

Key Functionalities:
--------------------
- **Default Recipe Creation:** Initializes a sample recipe with multiple stages
to demonstrate the application's capabilities.

- **Stage Management:** Creates recipe stages with instructions, images
(including placeholders), and designates the final stage.

- **Image Handling:** Associates images with each stage, utilizing placeholder
images where user-uploaded images are not provided.

- **Tagging System:** Assigns predefined tags to the demo recipe to illustrate
the tagging and search functionalities.
"""


from .models import db, Recipe, RecipeStage, RecipeImage, RecipeTag, EntityTag


# Common variables.
# I have been advise by my mentor that URLs can be longer than 79 chars.
PLACEHOLDER_IMAGE_URL = (
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder-1.jpg')
PLACEHOLDER_THUMBNAIL_URL = (
    'https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder-1.jpg')


def create_default_recipe(user):
    """
    Initialize a Default Recipe for a New User.

    This function creates a default "Demo Recipe" for a newly registered user.
    The demo recipe includes three stages with predefined instructions and
    images to demonstrate the application's features. Additionally, it assigns
    a set of predefined tags to the recipe to showcase the tagging and search
    functionalities.

    Args:
        user (User): The user object for whom the default recipe is being
        created. This user will be associated with the recipe.

    Returns:
        None
    """

    # Create a default recipe
    demo_recipe = Recipe(
        user=user,  # Automatically sets user_id
        recipe_name="Demo Recipe",
        recipe_desc=f"""
This is a demonstration recipe, to show a rough idea of possible uses.

Feel free to delete or edit this when you're done with it.

Images can be clicked on to see a larger copy, this will also allow you
to open the full sized version of the image in a new window.
        """
    )
    db.session.add(demo_recipe)
    db.session.flush()  # Get recipe_id

    # Create recipe stages
    stage1 = RecipeStage(
        stage_num=1,
        instructions=f"""
Your basic instructions should go here.

These will honour line breaks via the enter key.

Images and descriptions are optional, though a placeholder will be added if no
image is provided. Such as with this stage, where we see a black and white
image of our Mascot, Rummy Nate, the procrastinating Painter.
        """,
        is_final_stage=False
    )

    stage2 = RecipeStage(
        stage_num=2,
        instructions=f"""
This stage has a user-uploaded image with the image description being
used as the image's alt text.

Image descriptions are optional, but can help describe the image to those who
use assistive devices to access the internet, as well as being useful to help
describe the image to people who are following your recipe, so they should be
fairly descriptive where possible.
        """,
        is_final_stage=False
    )

    stage3 = RecipeStage(
        stage_num=3,
        instructions=f"""
This is the final stage, as such its image will function as the placeholder
for the recipe - ideally showing what the end results of the recipe should look
like.

Recipes can have a nearly infinite number of stages to allow for some very
complex recipes to be created, to add a stage simply click the 'add stage'
button below. To remove a stage, click the remove stage button - be aware that
this will remove anything you have entered in the stage to be removed so only
use this if you're happy to lose this content.
        """,
        is_final_stage=True
    )

    demo_recipe.stages.extend([stage1, stage2, stage3])
    db.session.flush()  # Get stage_ids

    # Create recipe images
    # I have been advise by my mentor that URLs can be longer than 79 chars.
    image1 = RecipeImage(
        stage=stage1,
        image_url=PLACEHOLDER_IMAGE_URL,
        thumbnail_url=PLACEHOLDER_THUMBNAIL_URL,
        alt_text='Default Image',
        public_id='placeholder'
    )

    image2 = RecipeImage(
        stage=stage2,
        image_url=PLACEHOLDER_IMAGE_URL,
        thumbnail_url=PLACEHOLDER_THUMBNAIL_URL,
        alt_text='A model of a frog, in red samurai armour.',
        public_id='demo-image-1'
    )

    image3 = RecipeImage(
        stage=stage3,
        image_url=PLACEHOLDER_IMAGE_URL,
        thumbnail_url=PLACEHOLDER_THUMBNAIL_URL,
        alt_text='Rummy Nate in glorious full colour.',
        public_id='demo-image-2'
    )

    # Add images to the session
    db.session.add_all([image1, image2, image3])

    # Associate images with stages
    demo_recipe.stages[0].recipe_images.append(image1)
    demo_recipe.stages[1].recipe_images.append(image2)
    demo_recipe.stages[2].recipe_images.append(image3)

    # Create or retrieve tags
    tags = ['These', 'Are', 'Tags', "They're", 'Used', 'For', 'Searching']
    tag_objects = []
    for tag_name in tags:
        tag = RecipeTag.query.filter_by(tag_name=tag_name).first()
        if not tag:
            tag = RecipeTag(tag_name=tag_name)
            db.session.add(tag)
            db.session.flush()  # Get tag_id
        tag_objects.append(tag)

    # Associate tags with the recipe
    for tag in tag_objects:
        entity_tag = EntityTag(
            recipe=demo_recipe,
            recipe_tag=tag,
            entity_type='recipe'
        )
        db.session.add(entity_tag)

    # Commit all changes
    db.session.commit()
