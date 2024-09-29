from flask import (
    Flask, flash, render_template, 
    request, redirect, url_for)
from colourforge import app, db
from colourforge.models import Recipes, RecipeStages


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":

        print("Recipe Name:", request.form.get('recipe_name'))
        print("Recipe Description:", request.form.get('recipe_desc'))
        print("Stage Number:", request.form.get('stage_num'))
        print("Stage Instructions:", request.form.get('instructions'))
        print("Is Final Stage?:", request.form.get('is_final_stage'))

        # Create the Recipe entry in the Database
        recipe = Recipes(
            recipe_name=request.form.get('recipe_name'),
            recipe_desc=request.form.get('recipe_desc'),
        )
        db.session.add(recipe)
        
        # Create the Recipe Stage entry in the Database. 
        recipe_stage = RecipeStages (
            recipe=recipe,
            stage_num=request.form.get('stage_num'),
            instructions=request.form.get('instructions'),
            is_final_stage=bool(True if request.form.get('is_final_stage') else False)
        )
        db.session.add(recipe_stage)
        db.session.commit()

        return redirect("recipes")
    return render_template("add_recipe.html")
