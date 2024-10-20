from .models import db, Recipe, RecipeStage, RecipeImage, RecipeTag, EntityTag


def create_default_recipe(user):

    # Create a default recipe
    demo_recipe = Recipe(
        user=user,  # Automatically sets user_id
        recipe_name="Demo Recipe",
        recipe_desc="""
        This is a demonstration recipe, to show a rough idea of possible uses.

        Images can be clicked on to see a larger copy, this will also allow you
        to open the full sized version of the image in a new window
        """
    )
    db.session.add(demo_recipe)
    db.session.flush()  # Get recipe_id

    # Create recipe stages
    stage1 = RecipeStage(
        stage_num=1,
        instructions="""
        Your basic instructions should go here.

        These will honour line breaks via the enter key.

        Images and descriptions are optional, though a placeholder will be
        added if no image is provided.

        Such as with this stage.
        """,
        is_final_stage=False
    )

    stage2 = RecipeStage(
        stage_num=2,
        instructions="""
        This stage has a user uploaded image with the image description being
        used as the images alt text.
        """,
        is_final_stage=False
    )

    stage3 = RecipeStage(
        stage_num=3,
        instructions="""
        This is the final stage, as such its image will function as the
        placeholder for the recipe - ideally showing what the end results of
        the recipe should look like.

        Recipes can have a nearly infinite number of stages to allow for some
        very complex recipes to be created.
        """,
        is_final_stage=True
    )

    demo_recipe.stages.extend([stage1, stage2, stage3])
    db.session.flush()  # Get stage_ids

    # Create recipe images
    image1 = RecipeImage(
        stage=stage1,
        image_url='https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728052910/placeholder.png',
        thumbnail_url='https://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/placeholder.png',
        alt_text='Default Image',
        public_id=None
    )

    image2 = RecipeImage(
        stage=stage2,
        image_url='https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728736766/srth5pc5nisq66mph7ng.jpg',
        thumbnail_url='http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/srth5pc5nisq66mph7ng.jpg',
        alt_text='Fafnir Ran Conversion',
        public_id='srth5pc5nisq66mph7ng'
    )

    image3 = RecipeImage(
        stage=stage3,
        image_url='https://res.cloudinary.com/dlmbpbtfx/image/upload/v1728736767/woumsfwwkgycjjqooe3g.jpg',
        thumbnail_url='http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_200,w_200/woumsfwwkgycjjqooe3g.jpg',
        alt_text=None,
        public_id='woumsfwwkgycjjqooe3g'
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
