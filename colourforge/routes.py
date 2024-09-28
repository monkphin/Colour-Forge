from flask import render_template
from colourforge import app, db
from colourforge.models import User, Recipes, RecipeStages, RecipeImages, RecipeTags, EntityTags


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add_recipe")
def add_recipe():
    return render_template("add_recipe.html")