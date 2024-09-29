from flask import (
    Flask, flash, render_template, 
    request, redirect, url_for)
from colourforge import app, db
from colourforge.models import Recipes


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

        recipe = Recipes(
            recipe_name=request.form.get('recipe_name'),
            recipe_desc=request.form.get('recipe_desc'),
        )
        db.session.add(recipe)
        db.session.commit()

        return redirect("recipes")
    return render_template("add_recipe.html")