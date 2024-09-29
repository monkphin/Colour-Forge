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

        # Create the Recipe entry in the Database
        recipe = Recipes(
            recipe_name=request.form.get('recipe_name'),
            recipe_desc=request.form.get('recipe_desc'),
        )
        db.session.add(recipe)
        db.session.commit()

        # initialise variables
        instructions = request.form.getlist('instructions[]')
        stage_num = 1

        # loop through list to add each as a stage in the DB
        for instruction in instructions:

            is_final_stage = (instruction == instructions[-1])
            recipe_stage = RecipeStages (
                recipe=recipe,
                stage_num=stage_num,
                instructions=instruction,
                is_final_stage=is_final_stage

            )
            db.session.add(recipe_stage)
            
            stage_num += 1

        db.session.commit()

        print("Recipe Name:", request.form.get('recipe_name'))
        print("Recipe Description:", request.form.get('recipe_desc'))
        print(stage_num)
        instructions = request.form.getlist('instructions[]')
        print("Instructions List:", instructions)
        print("Is Final Stage?:", request.form.get('is_final_stage'))

        return redirect("recipes")
    return render_template("add_recipe.html")
