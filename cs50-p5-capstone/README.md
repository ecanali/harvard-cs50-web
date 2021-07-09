<h1 align="center">
    <img alt="RecipeLab logo" src="./capstone/static/capstone/assets/recipelib-logo.png" width="150px" />
</h1>

<h1 align="center">RecipeLib Web App</h1>

This is my final project for [Harvard University - CS50's Web Programming with Python and JavaScript](https://cs50.harvard.edu/web/2020/) course. It is an open library of food recipes for all tastes! Everyone can create an account and post their favorite recipes.

- Link to the video on Youtube presenting this project

<a href="https://www.youtube.com/watch?v=PgfqDH_EGBc" target="_blank">
 <img src="https://img.youtube.com/vi/PgfqDH_EGBc/hqdefault.jpg" alt="Watch the video" width="240" height="180"/>
</a>

---

Table of contents
=================
<!--ts-->
   * [Why this project?](#-why-this-project)
   * [What's in the files?](#-whats-in-files)
   * [How to run it?](#-how-run)
   * [Additional information](#-additional-info)
<!--te-->

---

## Why this project? <a name="-why-this-project" style="text-decoration:none"></a>

This application uses the concepts of back-end with Django and front-end with HTML, CSS and JavaScript learned in the course and goes further.
This project satisfies the distinctiveness and complexity requirements because it explores image handling with upload and storage of the files into the database, interactive visual effects when uploading and displaying images and texts (excluding the images uploaded and hiding/showing the description text of the recipes by JavaScript), pagination and search filter in the recipe library. This application also includes an admin section of the page (different from the built-in Django's admin page) to manage the recipes.

---

## What's in the files? <a name="-whats-in-files" style="text-decoration:none"></a>
- **views.py**: all the back-end logic to query database and display the recipes accordingly to user's search and functions to manage user's own recipes, creating, editing and deleting contents. I wrote 10 additional routes/functions in order to achieve the project's goal, they are: index, about, recipes, recipe, filter, myrecipes, myrecipe, create_view, edit_view and delete;
- **models.py**: my 3 models of User, Recipe and File and their relationship, including logic to save the uploaded files to local storage;
- **static/styles.css**: more than 1,000 lines of CSS code for standard and mobile-responsive design;
- **static/site.js & admin.js**: all the JavaScript code to dynamic change the pages, including code to open the correct recipe details, hide/show informations, show on the nav bar which page the user is, all the logic to switch images in the gallery preview and to handle the user's uploaded image files;
- **static/assets/**: the immutable images files;
- **static/images/**: the recipes mutable images files;
- **templates/**: all the HTML view pages accessed by all users;
- **templates/admin/**: all the HTML view pages accessed only by logged in users to manage their recipes.

---

## How to run it? <a name="-how-run" style="text-decoration:none"></a>

```bash

# In a terminal/cmd window, clone this repository
$ git clone <this repo link>

# Access the project folder
$ cd capstone

# Execute the application/server
$ python manage.py runserver

# The server will start on port 8000 - access the web app by http://127.0.0.1:8000

```
---

## Additional information <a name="-additional-info" style="text-decoration:none"></a>
- I'm sorry guys but I kept all the pages content in Brazilian Portuguese in the hope of really deploying it in the near future;
- Thanks very much to all cs50 staff for creating such amazing content and delivering it worldwide for free! Special thanks for master Brian Yu for putting his heart on it.

---

Made with ♥ by Erick Canali
