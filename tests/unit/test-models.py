from colourforge models import User, Recipe, RecipeStage, RecipeImage, RecipeTags, EntityTag

# using https://testdriven.io/blog/flask-pytest/


def test_user_create():
    """
    GIVEN a User model
    When a new User is created
    THEN check the username, email, password and is_admin fields are defined correctly
    """
    user = User('test_user', 'email@domain.com', 'hashedpassword', False)
    assert user.username == 'test_user'
    assert user.email == 'email@domain.com'
    assert user.password == 'hashedpassword'
    assert user.is_admin is False