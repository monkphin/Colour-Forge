# **Colour Forge**

[Testing and Validation](#testing-and-validation)

 - [Usage Based Functionality Testing](#use-based-functionality-testing)
 - [# Bugs, Issues and challenges](#Bugs-issues-and-challenges) 
 - [Unresolved Bugs](#unresolved-bugs)
 - [HTML Validation](#html-validation)
 - [CSS Validation](#css-validation)
 - [Accessibility](#accessibility)
 - [Performance](#performance)
 - [User Testing](#user-testing)
 - [User Story Testing](#user-story-testing)
 - [Javascript Testing](#javascript-testing)
 - [Python Testing](#python-testing)
 - [Device and Browser Testing](#device-and-browser-testing)
 - [Responsiveness](#responsiveness)
 - [Automated testing](#automated-testing)

# Testing and Validation

## Use based functionality testing
While working on building basic functionality. It occurred to me that I would ideally need to test each specific function as I brought it online. As such, I commented out the majority of the models.py file and reduced it to just the recipes table with no relationships. I then created a new file called reset_db.py whose function was effectively purely to tear down and rebuild the db to save me having to do this manually each time I needed to online a new feature for testing. This way, I could keep my data clean and fresh each time a new feature was added. This idea came about because I dove in and created the entire DB schema with all relationships in place which when trying to test just adding a recipe name and description caused errors since I had nothing in place to ensure the foreign keys were being updated and that the data was fully linked and working, which caused Werkzueg errors to occur constantly. I also added some limited print output the function to ensure the data was being correctly captured before sending to the DB. 

This method of testing was moved on from after I started to get more to grips with accessing and writing data to the database, instead relying more on directly checking to see if data had updated on the website. Sadly, I neglected to record much, if any data from that point on, since I was more focused on getting functionality online and working as well as reacting to realisations about tweaks or changes that were needed. 

### add recipe
<details>
<summary>basic functionality to write to the recipes table</summary>
<img src="docs/add_recipe_test.png">

Output of writing to the recipes table<br>

Recipe Name: This is a test of the add recipe function<br>
Recipe Description: Testing the ability to add recipes. Nothing to see here. Once this works I will start to build the recipes page to show the stored data.<br>

127.0.0.1 - - [29/Sep/2024 16:46:15] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 16:46:15] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 16:46:15] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 16:46:15] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 16:46:15] "GET /static/js/script.js HTTP/1.1" 304 -<br>

Recipes table contents<br>
open_punch_bath_8981=> \dt<br>
           List of relations<br>
| Schema |  Name   | Type  |    Owner    |
|------- | ------- | ----- | ------------|
| public | recipes | table | urbqgoc5q8y |
(1 row)

open_punch_bath_8981=> select * from recipes;<br>

| recipe_id |                recipe_name                 |                                                                recipe_desc                                                               |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
|    1      | This is a test of the add recipe function  | Testing the ability to add recipes. Nothing to see here. Once this works I will start to build the recipes page to show the stored data. |
(1 row)
</details>

<details>
<summary>Output of writing to the recipe and recipe_stages tables</summary>
<img src="docs/add_recipe_test2.png">

Recipe Name: This is a test of the recipe stages<br>
Recipe Description: Testing to see if a single stage can be added OK<br>
2<br>
Instructions List: ['Just a single stage test. ']<br>
Is Final Stage?: None<br>
127.0.0.1 - - [29/Sep/2024 21:22:27] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 21:22:27] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 21:22:28] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:22:28] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:22:28] "GET /static/js/script.js HTTP/1.1" 304 -<br>

open_punch_bath_8981=> \dt<br>
           List of relations<br>
| Schema |     Name      | Type  |    Owner     |
| ------ | ------------- | ----- | ------------ |
| public | recipe_stages | table | urbqgoc5q8y  |
| public | recipes       | table | urbqgoc5q8y  |
(2 rows)

open_punch_bath_8981=> select * from recipes;<br>

| recipe_id |             recipe_name             |                   recipe_desc                     |
| --------  |------------------------------------ | ------------------------------------------------- |
|     1     | This is a test of the recipe stages | Testing to see if a single stage can be added OK  |
(1 row)

open_punch_bath_8981=> select * from recipe_stages;<br>

| stage_id | recipe_id | stage_num |        instructions        | is_final_stage   |
| -------- | --------- | --------- | -------------------------- | ---------------- |
|    1     |         1 |         1 | Just a single stage test.  | f                | 
(1 row)
</details>


<details>
<summary>basic functionality to write to the recipes table and add multiple stages to the recipes_stages table</summary>
<img src="docs/add_recipe_test3.png">

Recipe Name: Testing adding 2 stages<br>
Recipe Description: This is a test of 2 stages<br>
3<br>
Instructions List: ['This is the first stage.', 'This is the second stage. ']<br>
Is Final Stage?: None<br>
127.0.0.1 - - [29/Sep/2024 21:25:01] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 21:25:01] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 21:25:02] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:25:02] "GET /static/js/script.js HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:25:02] "GET /static/css/style.css HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> select * from recipes;<br>

| recipe_id |       recipe_name       |        recipe_desc         |
| --------- | ----------------------- | -------------------------- |
|      1    | Testing adding 2 stages | This is a test of 2 stages |
(1 row)

open_punch_bath_8981=> select * from recipe_stages;<br>
| stage_id | recipe_id | stage_num |        instructions        | is_final_stage  |
| -------- | --------- | --------- | -------------------------- | --------------- |
|     1    |      1    |      1    | This is the first stage.   | f               |
|     2    |      1    |      2    | This is the second stage.  | f               |
(2 rows)
</details>

<details>
<summary>Output of writing to the recipe and recipe_stages tables and testing the Boolean</summary>
<img src="docs/add_recipe_test4.png">

Recipe Name: Testing three stages with a final stage<br>
Recipe Description: This is a test of all functions added so far, recipe name, recipe description, multiple recipe stages and finally if the final stage bool is honoured. <br>
4<br>
Instructions List: ['This is stage 1 of the third test', 'This is stage 2 of the third test', 'This is stage 3 of the third test']<br>
Is Final Stage?: on<br>
127.0.0.1 - - [29/Sep/2024 21:28:22] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 21:28:22] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 21:28:22] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:28:22] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:28:22] "GET /static/js/script.js HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> select * from recipes;<br>


| recipe_id |               recipe_name               |                                                                       recipe_desc                                                                      |
| --------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
|     1     | Testing three stages with a final stage | This is a test of all functions added so far, recipe name, recipe description, multiple recipe stages and finally if the final stage bool is honoured. |

(1 row)<br>
<br>
open_punch_bath_8981=> select * from recipe_stages;<br>
| stage_id | recipe_id | stage_num |           instructions            | is_final_stage |
| -------- | --------- | --------- | --------------------------------- | -------------- |
|     1    |      1    |      1    | This is stage 1 of the third test | t              |
|     2    |      1    |      2    | This is stage 2 of the third test | t              | 
|     3    |      1    |      3    | This is stage 3 of the third test | t              | 
</details>

It seemed this assigned true to all stages, rather than just the last. This caused me to rethink how this should be handled, either giving the user an option per stage, which seems like too clunky a solution. Or to automatically assume the last stage added is the last stage of the instructions, which would make more sense since this is where we would normally expect the image used in the card for the recipe to be selected from. 

<details>
<summary>Output of writing to the recipe and recipe_stages tables and testing the new Boolean logic</summary>
<img src="docs/add_recipe_test5.png">
<br>
Recipe Name: Retest of multiple stages, with the new logic for the final stage added<br>
Recipe Description: This is hopefully a final test of the add recipe function, featuring the ability to add multiple stages and for the last stage to automatically have its bool set as 'true' to denote it as the last stage, meaning its attached image will be used for the recipes image<br>
5<br>
Instructions List: ['This stage 1 of the test of the adjusted Boolean handling', 'This stage 2 of the test of the adjusted Boolean handling', 'This stage 3 of the test of the adjusted Boolean handling', 'This stage 4 of the test of the adjusted Boolean handling']<br>
Is Final Stage?: None<br>
127.0.0.1 - - [29/Sep/2024 21:43:16] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 21:43:16] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 21:43:17] "GET /static/js/script.js HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:43:17] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:43:17] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> select * from recipes;<br>

| recipe_id |                               recipe_name                               |                                                                                                                                recipe_desc                                                                                                                                |
| --------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | 
|     1     | Testing three stages with a final stage                                 | This is a test of all functions added so far, recipe name, recipe description, multiple recipe stages and finally if the final stage bool is honoured.                                                                                                                    |
|     2     | Retest of multiple stages, with the new logic for the final stage added | This is hopefully a final test of the add recipe function, featuring the ability to add multiple stages and for the last stage to automatically have its bool set as 'true' to denote it as the last stage, meaning its attached image will be used for the recipes image |
(2 rows)

| stage_id | recipe_id | stage_num | instructions                                     | is_final_stage |
|----------|-----------|-----------|--------------------------------------------------|----------------|
| 1        | 1         | 1         | This is stage 1 of the third test                | t              |
| 2        | 1         | 3         | This is stage 2 of the third test                | t              |
| 3        | 1         | 3         | This is stage 3 of the third test                | t              |
| 4        | 2         | 1         | This is stage 1 of the adjusted Boolean handling | f              |
| 5        | 2         | 2         | This is stage 2 of the adjusted Boolean handling | f              |
| 6        | 2         | 3         | This is stage 3 of the adjusted Boolean handling | f              |
| 7        | 2         | 4         | This is stage 4 of the adjusted Boolean handling | f              |

</details>

<details>
<summary>Output of writing to the recipe and recipe_stages tables and testing the fix Boolean logic</summary>
<img src="docs/add_recipe_test6.png">
<br>
Recipe Name: Test of adjusted logic for Bool handling<br>
Recipe Description: THis is hopefully a final test for the adjusted Boolean logic<br>
3<br>
Instructions List: ['Stage 1 of the adjusted logic test', 'Stage 2 of the adjusted logic test']<br>
Is Final Stage?: None<br>
127.0.0.1 - - [29/Sep/2024 21:55:34] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [29/Sep/2024 21:55:34] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [29/Sep/2024 21:55:34] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:55:34] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:55:34] "GET /static/js/script.js HTTP/1.1" 304 -<br>
127.0.0.1 - - [29/Sep/2024 21:55:39] "GET /static/css/style.css HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> select * from recipes;<br>

| recipe_id |                               recipe_name                               |                                                                                                                                recipe_desc                                                                                                                                 |
| --------  | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     1     | Testing three stages with a final stage                                 | This is a test of all functions added so far, recipe name, recipe description, multiple recipe stages and finally if the final stage bool is honoured.                                                                                                                     |
|     2     | Retest of multiple stages, with the new logic for the final stage added | This is hopefully a final test of the add recipe function, featuring the ability to add multiple stages and for the last stage to automatically have its bool set as 'true' to denote it as the last stage, meaning its attached image will be used for the recipes image  |
|     3     | Testing adjusted logic for last stage check                             | Adjusted logic check for final stage logic                                                                                                                                                                                                                                 |
|     4     | Test of adjusted logic for Bool handling                                | THis is hopefully a final test for the adjusted Boolean logic                                                                                                                                                                                                              |
(4 rows)<br>

open_punch_bath_8981=> select * from recipe_stages;<br>

| stage_id | recipe_id | stage_num |                       instructions                        | is_final_stage |
| -------- | --------- | --------- | --------------------------------------------------------- | -------------- |
|    1     |    1      |    1      | This is stage 1 of the third test                         | t              |
|    2     |    1      |    2      | This is stage 2 of the third test                         | t              |
|    3     |    1      |    3      | This is stage 3 of the third test                         | t              |
|    4     |    2      |    1      | This stage 1 of the test of the adjusted Boolean handling | f              |
|    5     |    2      |    2      | This stage 2 of the test of the adjusted Boolean handling | f              |
|    6     |    2      |    3      | This stage 3 of the test of the adjusted Boolean handling | f              |
|    7     |    2      |    4      | This stage 4 of the test of the adjusted Boolean handling | f              |
|    8     |    4      |    1      | Stage 1 of the adjusted logic test                        | f              |
|    9     |    4      |    2      | Stage 2 of the adjusted logic test                        | t              |
(9 rows)
</details>

<details>
<summary>Output of writing to the recipe, recipe_stages tables, uploading to Cloudinary and finally writing the results of the upload to the recipe_images table</summary>
<img src="docs/add_recipe_test7.png">
<br>
Recipe Name: This is a test of adding the images to Cloudinary and the DB<br>
Recipe Description: Testing of image upload for a single stage<br>
1<br>
Instructions List: ['This is the first and only stage. The Bool should be true. Their should be an image URL and Thumbnail URL. ']<br>
Is Final Stage?: None<br>
Image names: [<FileStorage: 'hero-image.png' ('image/png')>]<br>
127.0.0.1 - - [30/Sep/2024 18:04:08] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [30/Sep/2024 18:04:08] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [30/Sep/2024 18:04:08] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 18:04:08] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 18:04:08] "GET /static/js/script.js HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> SELECT * FROM recipes;<br>

| recipe_id |                         recipe_name                          |                recipe_desc                 |
| --------- | ------------------------------------------------------------ | ------------------------------------------ |
|     1     | This is a test of adding the images to Cloudinary and the DB | Testing of image upload for a single stage |
(1 row)

open_punch_bath_8981=> SELECT * FROM recipe_stages;<br>
| stage_id | recipe_id | stage_num |                                                instructions                                                 | is_final_stage |
| -------- | --------- | --------- | ----------------------------------------------------------------------------------------------------------- | -------------- |
|     1    |     1     |     1     | This is the first and only stage. The Bool should be true. Their should be an image URL and Thumbnail URL.  | t              |
(1 row)

open_punch_bath_8981=> SELECT * FROM recipe_images;<br>
| image_id | stage_id |                                       image_url                                        |                                        thumbnail_url                                         |                                 alt_text                                |
| -------- | -------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
|     1    |     1    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727715847/eupydc07vwmej3en6xbs.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/eupydc07vwmej3en6xbs.jpg | This is a hero image for the Pokebattler website for my second project. |
(1 row)
</details>

<details>
<summary>Output of writing to the recipe, recipe_stages tables, uploading to Cloudinary and finally writing the results of the upload to the recipe_images table</summary>
<img src="docs/add_recipe_test8.png">
<br>
Recipe Name: This is a test of adding multiple images<br>
Recipe Description: Will try for three images this time over 4 stages<br>
1<br>
Instructions List: ['This is the first stages image', 'This is the second stages image', 'The third stage will have no alt_text added', 'This will have no image attached ']<br>
Is Final Stage?: None<br>
Image names: [<FileStorage: '404-page-desktop.png' ('image/png')>]<br>
127.0.0.1 - - [30/Sep/2024 18:12:03] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [30/Sep/2024 18:12:03] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [30/Sep/2024 18:12:03] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 18:12:03] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 18:12:03] "GET /static/js/script.js HTTP/1.1" 304 -<br>

127.0.0.1 - - [30/Sep/2024 18:04:08] "GET /static/js/script.js HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> SELECT * FROM recipes;<br>

| recipe_id |                         recipe_name                          |                    recipe_desc                    |
| --------- | ------------------------------------------------------------ | ------------------------------------------------- |
|      1    | This is a test of adding the images to Cloudinary and the DB | Testing of image upload for a single stage        |
|      2    | This is a test of adding multiple images                     | Will try for three images this time over 4 stages |
(2 rows)

open_punch_bath_8981=> SELECT * FROM recipe_stages;<br>
| stage_id | recipe_id | stage_num |                                                instructions                                                 | is_final_stage  |
| -------- | --------- | --------- | ----------------------------------------------------------------------------------------------------------- | --------------- |
|    1     |     1     |     1     | This is the first and only stage. The Bool should be true. Their should be an image URL and Thumbnail URL.  | t               |
|    2     |     2     |     1     | This is the first stages image                                                                              | f               |
(2 rows)

open_punch_bath_8981=> SELECT * FROM recipe_images;<br>
| image_id | stage_id |                                       image_url                                        |                                        thumbnail_url                                         |                                 alt_text                                 | 
| -------- | -------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | 
|     1    |     1    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727715847/eupydc07vwmej3en6xbs.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/eupydc07vwmej3en6xbs.jpg | This is a hero image for the Pokebattler website for my second project.  | 
|     2    |     2    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727716322/tnp1ssx1ac3gjs8blb0g.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/tnp1ssx1ac3gjs8blb0g.jpg | Sad Pikachu!                                                             | 
(2 rows)
</details>

The above only seemed to add a single image of the several that were input. On inspection, I'd missed creating the images and alt text entries as arrays. 

<details>
<summary>Output of writing to the recipe, recipe_stages tables, uploading to Cloudinary and finally writing the results of the upload to the recipe_images table</summary>
<img src="docs/add_recipe_test9.png">
<br>
Recipe Name: Testing multiple image uploads<br>
Recipe Description: This is a test<br>
3<br>
Instructions List: ['Stage 1', 'Stage 2', 'Stage 3']<br>
Is Final Stage?: None<br>
Image names: ['404-page-desktop.png', 'hero-image.png', 'Screenshot 2024-06-16 123914.png']<br>
alt text: ['Sad pika', 'Hero Image', 'Local Map']<br>
127.0.0.1 - - [30/Sep/2024 22:17:19] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [30/Sep/2024 22:17:19] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [30/Sep/2024 22:17:19] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 22:17:19] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 22:17:19] "GET /static/js/script.js HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> SELECT * FROM recipes;<br>

| recipe_id |          recipe_name           |  recipe_desc   | 
| --------- | ------------------------------ | -------------- |
|     1     | Testing multiple image uploads | This is a test |
(1 row)

open_punch_bath_8981=> SELECT * FROM recipe_stages;<br>
| stage_id | recipe_id | stage_num | instructions | is_final_stage |
| -------- | --------- | --------- | ------------ | -------------- |
|     1    |     1     |     1     | Stage 1      | f              |
|     2    |     1     |     2     | Stage 2      | f              |
|     3    |     1     |     3     | Stage 3      | t              |
(3 rows)

open_punch_bath_8981=> SELECT * FROM recipe_images;<br>
| image_id | stage_id |                                       image_url                                        |                                        thumbnail_url                                         |  alt_text   |
| -------- | -------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------- |
|    1     |     1    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731037/zcs4iirp7kqhspzje4lv.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/zcs4iirp7kqhspzje4lv.jpg | Sad pika    |
|    2     |     2    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731037/ixa63ye6aszg97ls8vvu.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/ixa63ye6aszg97ls8vvu.jpg | Hero Image  | 
|    3     |     3    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731038/ocke1j24jnwolatvzmb3.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/ocke1j24jnwolatvzmb3.jpg | Local Map   |
(3 rows)
</details>

<details>
<summary>Output of testing unexpected behaviours, such as not filling in all fields, forgetting to add alt-text (image description), forgetting to add an image, etc.</summary>
<img src="docs/add_recipe_test10.png">
<img src="docs/add_recipe_test10a.png">
<br>
Recipe Name: Test of not adding data to all fields for multiple stages<br>
Recipe Description: Some stages will have all fields filled. Some will not.<br>
5<br>
Instructions List: ['Stage 1 - this is the control and will have data in all fields ', 'Stage 2 - this will only have the instructions ', 'Stage 3 - This will just be an image', "Stage 4 - this is a possible, but unlikely scenario where an image description is added for an image alt. Once i've wired up the default placeholder image this should be overwritten so I may need logic for this. ", 'Stage 5 - this needed to be filled in to submit, as expected']<br>
Is Final Stage?: None<br>
Image names: ['Screenshot 2024-06-08 021116.png', '', 'Screenshot 2024-09-12 223744.png', '', 'Screenshot 2024-07-25 202904.png']<br>
alt text: ['The Thing', '', '', 'I forgot to add an image', "Phone Mock-up - In this instance I'm testing adding images and no Instructions"]<br>
127.0.0.1 - - [30/Sep/2024 22:28:38] "POST /add_recipe HTTP/1.1" 302 -<br>
127.0.0.1 - - [30/Sep/2024 22:28:38] "GET /recipes HTTP/1.1" 200 -<br>
127.0.0.1 - - [30/Sep/2024 22:28:39] "GET /static/css/style.css HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 22:28:39] "GET /static/images/logo.png HTTP/1.1" 304 -<br>
127.0.0.1 - - [30/Sep/2024 22:28:39] "GET /static/js/script.js HTTP/1.1" 304 -<br>
<br>
open_punch_bath_8981=> SELECT * FROM recipes;<br>


| recipe_id |                        recipe_name                        |                       recipe_desc                        | 
| --------- | --------------------------------------------------------- | -------------------------------------------------------- |
|      1    | Testing multiple image uploads                            | This is a test                                           |
|      2    | Test of not adding data to all fields for multiple stages | Some stages will have all fields filled. Some will not.  |
(2 rows)

open_punch_bath_8981=> SELECT * FROM recipe_stages;<br>
| stage_id | recipe_id | stage_num |                                                                                                     instructions                                                                                                     | is_final_stage | 
| -------- | --------- | ----------| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  | -------------- |
|     1    |     1     |     1     | Stage 1                                                                                                                                                                                                              | f              |
|     2    |     1     |     2     | Stage 2                                                                                                                                                                                                              | f              |
|     3    |     1     |     3     | Stage 3                                                                                                                                                                                                              | t              |
|     4    |     2     |     1     | Stage 1 - this is the control and will have data in all fields                                                                                                                                                       | f              |
|     5    |     2     |     2     | Stage 2 - this will only have the instructions                                                                                                                                                                       | f              |
|     6    |     2     |     3     | Stage 3 - This will just be an image                                                                                                                                                                                 | f              |
|     7    |     2     |     4     | Stage 4 - this is a possible, but unlikely scenario where an image description is added for an image alt. Once i've wired up the default placeholder image this should be overwritten so I may need logic for this.  | f              |
|     8    |     2     |     5     | Stage 5 - this needed to be filled in to submit, as expected                                                                                                                                                         | t              |
(8 rows)

open_punch_bath_8981=> SELECT * FROM recipe_images;<br>
| image_id | stage_id |                                       image_url                                        |                                        thumbnail_url                                         |                                   alt_text                                    |
| -------- | -------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
|    1     |     1    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731037/zcs4iirp7kqhspzje4lv.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/zcs4iirp7kqhspzje4lv.jpg | Sad pika                                                                      |
|    2     |     2    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731037/ixa63ye6aszg97ls8vvu.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/ixa63ye6aszg97ls8vvu.jpg | Hero Image                                                                    |
|    3     |     3    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731038/ocke1j24jnwolatvzmb3.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/ocke1j24jnwolatvzmb3.jpg | Local Map                                                                     |
|    4     |     4    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731716/jwrsx0hlqixuxl2k1fdc.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/jwrsx0hlqixuxl2k1fdc.jpg | The Thing                                                                     |
|    5     |     6    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731717/ytwtbmoc6wmrxenzk5fj.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/ytwtbmoc6wmrxenzk5fj.jpg |                                                                               |
|    6     |     8    | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727731718/xeynhlcgz4jbzuysjg34.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/xeynhlcgz4jbzuysjg34.jpg | Phone Mockup - In this instance I'm testing adding images and no Instructions |
(6 rows)
</details>

The above test, while initially using 6 stages for testing, also let me test what would happen if I removed a stage using the remove button before submitting, since the 5th and 6th stages were both initially intended to have the instructions empty, with the sixth stage having just the images alt-text added. Since both stages were unable to be submitted as empty as per design this meant that stage 6 was no longer needed, allowing me to prove the removal of a stage stops it being submitted. 

<details>
<summary>Testing writing to all tables needed for adding a recipe, recipes, recipe_stages, recipe_images, recipe_tags and entity_tags  </summary>
<img src="docs/add_recipe_test11.png">
<br>
Recipe Name: Dark Angels Desaturated Power Armour<br>
Recipe Description: This is a simple 3-4 paint recipe for very dark, very desaturated Dark Angels power armour<br>
1<br>
Instructions List: ['Undercoat the model with a flat black paint. ', "Using Caliban Green as a base coat, heavily drybrush the model - while we want to cover as much as we can, it's not a huge deal if the recesses are missed since the black will provide natural shadows where it is left. ", "using Loren Forest we now need to give the mini a much lighter drybrush, this can happily go over flat panels on the armour too, sinInstructions List: ['Undercoat the model with a flat black paint. ', "Using Caliban Green as a base coat, heavily drybrush the model - while we want to cover as much as we can, it's not a huge deal if the recesses are missed since the black will provide natural shadows where it is left. ", "using Loren Forest we now need to give the mini a much lighter drybrush, this can happily go over flat panels on the armour too, since we'll be cleaning this up in the next stage a little and it will help provide a more organic-looking highlight to the miniature. ", 'Next up, we cover the model in Coelia Greenshade once its dried this should start to filter the lighter Loren forest coat and pull it down to be a little closer to the Dark Angels Green base coat. ']<br>
Is Final Stage?: None<br>
Image names: ['404-page-desktop.png', 'game-wave.png', 'hero-image.png', 'jest.png']<br>
alt text: ['Undercoated Dark Angel', 'Base coat', 'First Highlight', 'Wash']<br>
Full form content ImmutableMultiDict([('recipe_name', 'Dark Angels Desaturated Power Armour'), ('recipe_desc', 'This is a simple 3-4 paint recipe for very dark, very desaturated Dark Angels power armour'), ('tags', 'Dark Angels,Warhammer,Space Marines,Power Armour,Desaturated'), ('instructions[]', 'Undercoat the model with a flat black paint. '), ('instructions[]', "Using Caliban Green as a base coat, heavily drybrush the model - while we want to cover as much as we can, it's not a huge deal if the recesses are missed since the black will provide natural shadows where it is left. "), ('instructions[]', "using Loren Forest we now need to give the mini a much lighter drybrush, this can happily go over flat panels on the armour too, since we'll be cleaning this up in the next stage a little and it will help provide a more organic-looking highlight to the miniature. "), ('instructions[]', 'Next up, we cover the model in Coelia Greenshade once its dried this should start to filter the lighter Loren forest coat and pull it down to be a little closer to the Dark Angels Green base coat. '), ('image_desc[]', 'Undercoated Dark Angel'), ('image_desc[]', 'Base coat'), ('image_desc[]', 'First Highlight'), ('image_desc[]', 'Wash')])<br>
<br>
open_punch_bath_8981=> \dt<br>

           List of relations<br>

| Schema |     Name      | Type  |    Owner    | 
| ------ |-------------  | ----- | ----------- |
| public | entity_tags   | table | urbqgoc5q8y |
| public | recipe_images | table | urbqgoc5q8y |
| public | recipe_stages | table | urbqgoc5q8y | 
| public | recipe_tags   | table | urbqgoc5q8y |
| public | recipes       | table | urbqgoc5q8y |
(5 rows)

open_punch_bath_8981=> select * from recipes;<br>
| recipe_id |             recipe_name              |                                        recipe_desc                                         |
| --------- | ------------------------------------ | ------------------------------------------------------------------------------------------ |
|      1    | Dark Angels Desaturated Power Armour | This is a simple 3-4 paint recipe for very dark, very desaturated Dark Angels power armour | 
(1 row)

open_punch_bath_8981=> select * from recipe_stages;<br>
| stage_id | recipe_id | stage_num |                                                                                                                               instructions                                                                                                                               | is_final_stage  |
| -------- | --------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
|     1    |     1     |     1     | Undercoat the model with a flat black paint.                                                                                                                                                                                                                             | f               |
|     2    |     1     |     2     | Using Caliban Green as a base coat, heavily drybrush the model - while we want to cover as much as we can, it's not a huge deal if the recesses are missed since the black will provide natural shadows where it is left.                                                | f               |
|     3    |     1     |     3     | using Loren Forest we now need to give the mini a much lighter drybrush, this can happily go over flat panels on the armour too, since we'll be cleaning this up in the next stage a little and it will help provide a more organic-looking highlight to the miniature.  | f               |
|     4    |     1     |     4     | Next up, we cover the model in Coelia Greenshade once its dried this should start to filter the lighter Loren forest coat and pull it down to be a little closer to the Dark Angels Green base coat.                                                                     | t               |
(4 rows)

open_punch_bath_8981=> select * from recipe_images;<br>
| image_id | stage_id |                                       image_url                                        |                                        thumbnail_url                                         |        alt_text         |       
| -------- | -------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------- | 
|    1     |    1     | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727987873/q5i2ftplla6udtqxdlob.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/q5i2ftplla6udtqxdlob.jpg | Undercoated Dark Angel  | 
|    2     |    2     | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727987876/afcihcowy0sjo7jvtzx1.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/afcihcowy0sjo7jvtzx1.jpg | Base coat               | 
|    3     |    3     | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727987877/bc4onemhmikj4otzngk2.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/bc4onemhmikj4otzngk2.jpg | First Highlight         | 
|    4     |    4     | https://res.cloudinary.com/dlmbpbtfx/image/upload/v1727987878/g5ccnr4thoblvveatmpq.png | http://res.cloudinary.com/dlmbpbtfx/image/upload/c_fill,h_100,w_100/g5ccnr4thoblvveatmpq.jpg | Wash                    | 
(4 rows)

open_punch_bath_8981=> select * from recipe_tags;<br>
| tag_id |   tag_name    |
| ------ | ------------- |
|    1   | Dark Angels   |
|    2   | Warhammer     |
|    3   | Space Marines |
|    4   | Power Armour  |
|    5   | Desaturated   |
(5 rows)

open_punch_bath_8981=> select * from entity_tags;<br>
| recipe_id | tag_id | entity_type  |
| --------- | ------ | ------------ |
|     1     |      1 | recipe       |
|     1     |      2 | recipe       |
|     1     |      3 | recipe       |
|     1     |      4 | recipe       |
|     1     |      5 | recipe       |
(5 rows)
</details>

# Bugs, Issues and challenges 

### Tags

Tags were a challenge to get to work correctly due to not only the need for the many to many relationship to work, but also to have them be able to be re-used by users once they'd been entered so to have existing tags presented as they were being typed. I tried a few alternative approaches to this, including using [Materialize Tags Input](https://henrychavez.github.io/materialize-tags/) as well as a few other tagging tools I found online, but was unable to get to work fully as intended, effectively the main issues I as finding is that I wasn't able to use the Materialize Chips when adding or editing tags, which caused me to shift approach and treat editing and entry more like a text field. After some research I found Awesomeplete which would cover the autocomplete functionality, allowing users to draw on and add to the library of tags available on the site. I was able to get this working using some tweaking to some Javascript I found online, so the section around Awesomeplete in the JS File should not be graded since this was heavily reliant on code from [this source.](https://elixirforum.com/t/how-to-use-a-js-library-like-awesomplete-within-a-liveview/32251/9) 

### Refactoring and DRY 
While working on the app routes for recipe functionality, it quickly became apparent that I would need to start to refactor these down into smaller helper functions, since at one point the edit route alone was pushing around 120 lines of code and was becoming increasingly difficult to understand how different parts of the code were causing issues or impacting other parts of the code. This has the added benefit of encouraging more DRY focused methodology allowing for reuse of code. More refactoring work will be needed, since the core focus of this was on the routes file, the auth and admin files were added later and the routes contained within them were relatively small, so were not a priority for refactoring. 
In some cases, I am aware of instances where I may be repeating code in the Helpers file, from skimming I've spotted that I'm performing image uploads as part of a specific function, rather than handing this off to the function that is in place to upload images, this is something that will be addressed going forwards as time allows. 

### Cloudinary Deletion
While developing the edit function, I realised that I was leaving images on Cloudinary that were no longer needed, since I hadn't built any logic to remove these. As such where stage deletion or image changes were handled, I added in functions to also delete the image from Cloudinary using the images public ID. 

### Accidental Image Deletion
I had an issue that was detected late on that allowed the default images used in the demo recipe to be deleted by any user when they delete the Demo Recipe, which is understandably not desirable, since this will impact all users who may join. As such, I added an additional check when deleting images to ensure that the public ID does not start with the word 'Placeholder'. Since I can manually set the PublicID and image names on images hosted on Cloudinary I was able to use this as a way of preventing this from being an issue. 

### Button Debounce
While working on getting edit functionality fully online I decided to publish the app to Heroku to allow me to get some user testing as things were moving forwards. This very quickly highlighted an issue where a user could submit the same recipe multiple times which I' hadn't factored for. A simple button disable function was implemented in the Javascript to prevent this from occurring. Initially this is only on the add_recipe page, but gradually it was slowly added to every other page where a user could submit a form, since the same issue was present on all form entries. 

While the majority of the site has the submit buttons disabled onclick, to prevent the potential for users to spam adding recipes etc, I cannot get this to work in conjunction with Google ReCaptcha on the email form, since it seems that ReCaptcha takes control of the button when its clicked, which prevents me from disabling this. 
Further investigation will be needed how to resolve this, however since ReCaptcha was more of a stretch goal for the project, since I'm pushing beyond what should be an MVP here, I feel reasonably comfortable letting this go for the time being, since all that it will mean is that users may be able to send the same email to the inbox multiple times, which has no real impact on the site or its functionality, and instead allows users to repeatedly send a single email in error. 

### Jinja Issues caused by not storing data in the DB
Found an issue when creating the edit recipe page, where when an image was using placeholders, so had no entry in the DB, since I was just populating these via the HTML it would generate the following Werkzeug error: UndefinedError
jinja2.exceptions.UndefinedError: sqlalchemy.orm.collections.InstrumentedList object has no element 0
While falling back to rendering a placeholder file locally is fine, I couldn't quite work out how to skip over non-existent DB entries when loading the edit page for recipes that had no images. As such, I adjusted the image handling logic in the routes.py file so that it would insert a URL string into the images table when the user didn't submit an image, allowing this to be loaded and rendered from the Jinja insertions on the edit page. While this works, I will be leaving the HTML fall backs in place as a safety net, though these shouldn't ever be needed, since unless the connection to the DB goes down then the site should always see the entry and if the DB connection fails, the recipes wont be loading anyway. 

### Card Reflow issues.
During development a persistent issue was that cards would sometimes grow to be larger than other cards in the same row, causing the row below to reflow into the next row below it.
To resolve this I ended up adding some significant tweaks via CSS, requiring me to use a lot of Media Queries to ensure that the cards rendered in a reasonably acceptable manner over multiple window sizes and screen resolutions.
This is very much a band aid solution and ideally this should be resolved by making further adjustments to font sizes, card sizes, text reflow and so on, however this will take time to fully implement.

<details>
<summary>Reflow Bug</summary>
<img src="docs/bugs/reflow issue.png">
</details>

### Text Box issues. 
Another persistent issue I encountered was with the Materialize text box. For some reason this would not readily adjust when changing screen resolution during testing, consistently causing issues with page overflow which resulted in the page shrinking within the window at varying screen resolutions, compressing the site into itself. 
I noticed that I'd omitted to include the Javascript provided by Materialize to help with text box resizing, however even with this added I was finding the behaviour was still present. In order to resolve this I had to create my own custom text box, outside of that offered by materialize and come up with some custom javascript to assist with resizing. I'm still unsure why the Materialize solution didn't work, however I feel that adding my own custom box actually improved the UI somewhat, since it allowed me to make text boxes stand out from text fields more, since the Materialize CSS framework presents both as blank lines that the user can type in, where as my custom approach presents the text box as a distinct box which I feel makes it more obvious that it can take a large volume of text, as opposed to a single line. 

<details>
<summary>Reflow Bug</summary>
<img src="docs/bugs/crushed-site-1.png">
<img src="docs/bugs/crushed-site-2.png">
</details>

### Stage Ordering Issues. 
Found an issue late in development where when updating a single stage of a multistage recipe, the stages would reorder. This seems very hit and miss where it doesn't always seem to occur on recipe editing. 

<details>
<summary>Sorting Bug</summary>
<img src="docs/bugs/recipe-sort-bug-edit.png">
<img src="docs/bugs/recipe-sort-bug.png">
</details>

<details>
<summary>Resolved Sorting Bug</summary>
<img src="docs/bugs/resolved-sort-bug-edit.png">
<img src="docs/bugs/resolved-sort-bug.png">
</details>

This was the recipe before editing. 
open_punch_bath_8981=> select * from recipe_stages where recipe_id = 53;
| stage_id | recipe_id | stage_num | instructions | is_final_stage 
| -------- | --------- | --------- | ------------ | --------------- |
|      135 |        53 |         1 | Testing 1    | f               |
|      136 |        53 |         2 | Testing 2    | f               |
|      137 |        53 |         3 | Testing 3    | t               |
(3 rows)

This was it after
open_punch_bath_8981=> select * from recipe_stages where recipe_id = 53;
| stage_id | recipe_id | stage_num |           instructions           | is_final_stage |
| -------- | --------- | --------- | -------------------------------- |--------------- |
|      136 |        53 |         2 | Testing 2                        | f              |
|      135 |        53 |         1 | Testing 1\r                      | f              |
|          |           |           | \r                               |                |
|          |           |           | this should move to stage 2 or 3 |                |
|      137 |        53 |         3 | Testing 3                        | t              |
(3 rows)

A quick fix to this was to force a sort on the for loop on any pages that render the recipe stages to ensure that the user sees them in the correct order, irrespective of what order the recipe is in the DB. While this isn't a fix of the underlying issue, it does provide a quick, short term user facing resolution to the issue to allow me time to properly investigate and resolve the underlying issue. Even if/when I resolve the underlying issue this can also happily remain in the HTML for the foreseeable future, since it's a useful fallback in-case of other issues which may cause reordering of stages that I may miss or may crop up as I develop the site further, or as I continue to refine and refactor the code. 

Jinja for loop before the fix:<br>
{% for stage in recipe.stages %}<br>
Jinja for loop after the fix:<br>
{% for stage in recipe.stages|sort(attribute='stage_num') %}

# Unresolved Issues
Something I neglected to realise early on is that the free version of Cloudinary has a [max file size](https://support.cloudinary.com/hc/en-us/articles/202520592-Do-you-have-a-file-size-limit#:~:text=On%20our%20free%20plan%2C%20the,also%20limited%20to%2010%20MB.) for uploads, which is set at 10Mb. Currently I'm not sure I have time to try to investigate and implement a fix for this. I have found t[he following StackOverflow article](https://stackoverflow.com/questions/2104080/how-do-i-check-file-size-in-python) that outlines an approach I may be able to build off and implement a file size check which will alert a user when adding too large an image, however I do not know if I will be able to implement this between now and the deadline to hand in for marking. Sadly in the meantime this means that users who upload an image larger than 10Mb will see a Werkzueg error, which is a less than ideal experience. I suspect this may not be a huge issue in the short term, since the majority of users will more than likely be uploading cropped smartphone photos, rather than un-cropped images and photos taken from dSLRs and other devices that are more likely to take photos that will generate larger sized images, but it would be better to ensure their are protections in place to prevent the site throwing a Werkzueg error and instead just kicking a flashed message. 

<details>
<summary>Large Image Bug</summary>
<img src="docs/bugs/large-image-error.png">
</details>

While this bug is present, when it is triggered, it can cause recipes to not be accessible via the GUI, since the image or image description are used as the link for the recipe. 

<details>
<summary>Large Image Bug</summary>
<img src="docs/bugs/unviewable-recipes.png">
</details>

The site has a couple of minor graphical issues that I have noticed but can't quite pin down. THe search box bug is the more frustrating of the two, since this is user facing. The Admin Menu issue is less of a problem since it would only be an issue for a very small subset of users. However neither of these causes significant issues for functionality and are more very minor UI issues. 

 - The desktop search bar shows a strip of white beneath it when a user clicks into it to search, I cannot locate a cause for this. 

 <details>
<summary>Searchbox Bug</summary>
<img src="docs/bugs/searchbox-bug.png">
</details>

Additionally I have noticed an issue with the admin menu drop down on the nav bar. This is set to fit the contents, yet seems to insist on word wrapping when the Recipe Admin option is selected. 

<details>
<summary>Admin Menu Bug</summary>
<img src="docs/bugs/user-admin.png">
<img src="docs/bugs/recipe-admin-bug.png">
</details>

Additionally, while I have already mentioned it in the resolved bugs section. I feel it's worth again calling out the issues with recipe ordering, since while I have a fix in place, it is, at best a band aid solution to what I think may be a much larger issue which warrants further investigation, particularly since the fix I have in place would cause issues with potential future functionality where reordering the recipe stages or adding in new between existing ones is concerned. 

# HTML Validation

W3Schools HTML Validator was used to test all HTML. Since much of the site is locked behind a login requirement the testing tool cannot test directly from the website, so I have had to view source and paste for each page that needed to be tested. 

| Page                  | Result                                                          | 
| --------------------- | --------------------------------------------------------------- |
| Logged out home page  | <img src="docs/html-testing/loggedout-home.png">                |
| About Page            | <img src="docs/html-testing/loggedout-about.png">               |
| Login Page            | <img src="docs/html-testing/loggedout-login.png">               |
| Register Page         | <img src="docs/html-testing/loggedout-register.png">            |
| Contact Page          | <img src="docs/html-testing/loggedout-contact.png">             |
| Logged in Home Page   | <img src="docs/html-testing/loggedin-home.png">                 |
| My Recipes Page       | <img src="docs/html-testing/loggedin-my-recipes.png">           |
| Recipe Page           | <img src="docs/html-testing/loggedin-recipe-page.png">          |
| Add Recipe Page       | <img src="docs/html-testing/loggedin-add-recipe.png">           |
| Edit Recipe Page      | <img src="docs/html-testing/loggedin-edit-recipe.png">          |
| Account Page          | <img src="docs/html-testing/loggedin-account.png">              |
| Account Admin Page    | <img src="docs/html-testing/loggedin-account-admin.png">        |
| Account Admin Search  | <img src="docs/html-testing/loggedin-account-admin-search.png"> |
| Recipe Admin Page     | <img src="docs/html-testing/loggedin-recipe-admin.png">         |
| Recipe Admin Search   | <img src="docs/html-testing/loggedin-recipe-admin-search.png">  |
| Tag Search Page       | <img src="docs/html-testing/loggedin-tag-search.png">           |
| Error Pages           | <img src="docs/html-testing/error-pages.png">                   |


# CSS Validation

CSS validation was conducted using the W3 Schools validation service. This highlighted errors with Materialize CSS and a few errors in my own CSS, specifically around the user of vendor extensions which were needed to ensure that Webkit based browsers were able to render parts of the site as expected. 

There were also two deprecation warnings for Clip and Break-word. Clip was being used in a hidden class investigating found that his had been replaced with clip path, so after some reading of MDN docs, I adjusted this to use clip path instead. Similarly after reading MDN docs, I replaced break word with overflow-wrap: anywhere, which is the current equivalent, though is a bit more aggressive on word breaks than break-word was. Once I'd made the needed adjustments 

The results of the CSS validation be found here: [W3Schools Jigsaw test results](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fcolourforge.co.uk&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)

# Accessibility
WAVE was used to check to ensure the site conforms to accessibility standards. 

A few issues were highlighted, specifically around duplication of the link to the Home Page, since this features in both the site name and the home button; some images having 'suspicious' Alt Text, which was caused by the 'Default Image' placeholder Alt Texts used for placeholder images. Some broken and missing link messages were occurring on every page, which were caused by the side nav menu and both the admin and search drop downs, which use fake links for them to work. Also some forms reported no labels. However, other than two forms on the contact page which I believe may be caused by ReCaptcha, I could not locate any forms that were missing labels on the site. There were a few minor call outs to headings also, which considering the site can't really conform to standardised layouts I think is reasonably acceptable, since theirs no sections etc to have H2, H3 and so on and these were used where it was appropriate to do so. 

## Logged Out Pages
<details>
<summary>Home Page</summary>
<img src="docs/wave/wave-home-loggedout.png">
</details>
<br>

<details>
<summary>About Page (to add)</summary>
<img src="docs/wave/WAVE">
</details>
<br>

<details>
<summary>Login Page</summary>
<img src="docs/wave/wave-login-loggedout.png">
</details>
<br>

<details>
<summary>Register Page</summary>
<img src="docs/wave/wave-register-loggedout.png">
</details>
<br>

<details>
<summary>Contact Page</summary>
<img src="docs/wave/wave-contact-logedout.png">
</details>
<br>

## Logged In Pages
<details>
<summary>Home Page</summary>
<img src="docs/wave/WAVE-Home-LoggedIn.png">
</details>
<br>

<details>
<summary>My Recipes Page</summary>
<img src="docs/wave/WAVE-MyRecipes-LoggedIn.png">
</details>
<br>

<details>
<summary>Account Page (to add)</summary>
<img src="docs/wave/WAVE-Acc.png">
</details>
<br>

<details>
<summary>Tag Search Results</summary>
<img src="docs/wave/WAVE-TagSearchResults-LoggedIn.png">
</details>
<br>

<details>
<summary>Add Recipe Page Results</summary>
<img src="docs/wave/WAVE-Addrecipe-LoggedIn-SingleStage.png">
<img src="docs/wave/WAVE-AddRecipe-LoggedIn-MultiStage.png">
</details>
<br>

<details>
<summary>Recipe Page Results</summary>
<img src="docs/wave/WAVE-RecipePage-Loggedin.png">
</details>
<br>

<details>
<summary>Edit Recipe Results</summary>
<img src="docs/wave/WAVE-EditRecipe-LoggedIn.png">
</details>
<br>

<details>
<summary>Error Page Results</summary>
<img src="docs/wave/WAVE-ErrorPages-LoggedIn.png">
</details>
<br>

## Admin Pages
<details>
<summary>User Admin Results</summary>
<img src="docs/wave/WAVE-Admin-LoggedIn.png">
</details>
<br>

<details>
<summary>User Admin Search Results</summary>
<img src="docs/wave/WAVE-AdminSearchResults-LoggedIn.png">
</details>
<br>

<details>
<summary>Recipe Admin Search Results</summary>
<img src="docs/wave/WAVE-RecipeAdmin-LoggedIn.png">
</details>
<br>

<details>
<summary>Recipe Admin Search Results</summary>
<img src="docs/wave/WAVE-RecipeAdminSearch-LoggedIn.png">
</details>
<br>

# Performance

Performance testing was conducted with Googles Lighthouse, which is part of its DevTools package in Chrome. 

Due to the sites reliance on several external resources, which in some cases are on free tiers, which can impact performance I fully expected performance tests to not be great for this app, since external services can be factor when it comes to load times that are beyond the control of the site owner. Similarly the nature of the site being image and DB query heavy will be contributing factors since the images can, often intentionally so, be large. Similarly their can be multiple calls made to the DB per page where multi stage recipes are concerned. This is part of the reason I opted to use CloudFlare for caching content when the site has been browsed, since this can help to mitigate load times where possible. 

I suspect I may be able to implement things like preloading and similar to help. Similarly I have generated a minified CSS file which the site uses and may, in future shift to minimized Javascript and HTML files to see if these help with load times. 


## Logged Out
<details>
<summary>Home Page Results</summary>
<img src="docs/lighthouse/Lighthouse-Home-LoggedOut.png">
</details>
<br>

<details>
<summary>Login Page Results</summary>
<img src="docs/lighthouse/Lighthouse-Login-LoggedOut.png">
</details>
<br>

<details>
<summary>Registration Page Results</summary>
<img src="docs/lighthouse/Lighthouse-Register-LoggedOut.png">
</details>
<br>

<details>
<summary>Contact Page Results</summary>
<img src="docs/lighthouse/Lighthouse-Contact-LoggedOut.png">
</details>
<br>

## Logged In
<details>
<summary>Logged in Home Page Results</summary>
<img src="docs/lighthouse/Lighthouse-Home-LoggedIn.png">
</details>
<br>

<details>
<summary>My Recipes Results</summary>
<img src="docs/lighthouse/Lighthouse-MyRecipes-LoggedIn.png">
</details>
<br>

<details>
<summary>Account Results</summary>
<img src="docs/lighthouse/Lighthouse-Account-LoggedIn.png">
</details>
<br>

<details>
<summary>Recipe Page Results</summary>
<img src="docs/lighthouse/Lighthouse-RecipePage-LoggedIn.png">
</details>
<br>

<details>
<summary>Add Recipe Results</summary>
<img src="docs/lighthouse/Lighthouse-AddRecipe-LoggedIn.png">
</details>
<br>

<details>
<summary>Edit Recipe Results</summary>
<img src="docs/lighthouse/Lighthouse-EditRecipe-LoggedIn.png">
</details>
<br>

<details>
<summary>Tag Search Results</summary>
<img src="docs/lighthouse/Lighthouse-TagSearch-LoggedIn.png">
</details>
<br>

## Admin Pages
<details>
<summary>User Admin Results</summary>
<img src="docs/lighthouse/Lighthouse-Admin-LoggedIn.png">
</details>
<br>

<details>
<summary>User Admin Search Results</summary>
<img src="docs/lighthouse/Lighthouse-AdminSearch-LoggedIn.png">
</details>
<br>

<details>
<summary>Recipe Admin Results</summary>
<img src="docs/lighthouse/Lighthouse-RecipeAdmin-LoggedIn.png">
</details>
<br>

<details>
<summary>Recipe Admin Search Results</summary>
<img src="docs/lighthouse/Lighthouse-RecipeAdminSearch-LoggedIn.png">
</details>
<br>

# User Testing
User level testing was conducted throughout development by contacting a small group of fellow hobbyists who I know are often keen to share information on how they approach painting, which lead to a few issues being discovered, which have been highlighted elsewhere, including the ability to add multiple duplicate entries, issues with shared images being deleted by a single user deleting a recipe. 

# User Story Testing



# Javascript Testing
Javascript validation was performed using [JSHint](https://jshint.com/) which highlighted a few unused variables, some undeclared variables and a lot of informational warnings about some features only being available in ES6. 

I need to refactor the JS file and break things up into functions to make it more readable however from some initial attempts at refactoring and cleaning up the unused variables this causes functionality to break in terms of adding and removing stages as well as some other features. So for now I will leave this mostly untouched so I can go back and refactor at a later date. 


# Python Testing
PEP8 Compliance testing was conducted with the Code Institute provided [Python Linter ](https://pep8ci.herokuapp.com/) the results of which can be seen below. 

| File Name   | Result                               |
| ----------- | ------------------------------------ |
| __init__.py | One issue detected, see notes below  |
| admin.py    | Pass                                 |
| auth.py     | Pass                                 |
| helpers.py  | Two issues detected, see notes below |
| mail.py     | Pass                                 |
| models.py   | Pass                                 |
| routes.py   | Pass                                 |
| seed.py     | Two issues detected, see notes below |

### Init File
The file has an issue where an import is declared mid way through the document. Specifically on line 58
```
from colourforge.models import User
```
If I declare this at the top of the document I get circular import errors. I cannot work out what is causing this to prevent it being an issue. 

### helpers.py
This file has two lines that are two long. Specifically lines 50 and 52, with them being 86 and 93 characters in length respectively. 

Both these lines are URL strings for images which are set as variables to be used in a few places in the document. I have been advised by my mentor that long URLs are fine for being longer than 79 characters, since its easier to read when they're on a single line rather than split and concatenated back together. 

### seed.py 
Much like the helpers file this is throwing errors due to long line lengths. Specifically 35 and 37, which are again 86 and 93 characters in length respectively. Again, these are two URL strings which are used by the variables they're assigned to to populate URLs into the DB when the file is accessed and are more readable as a single long string than split over two lines. 

# Device and Browser Testing

# Responsiveness

# Automated testing
Automated testing was something I had attempted to consider, but ended up being skipped in favour of live use testing, where since the site was published on Heroku I could invite a limited selection of users to test the site and put it through its paces. This helped highlight a few issues as testing occurred, such as being able to submit duplicate DB entries by repeatedly clicking the button, adding multiple images to a stage via button spam, finding that their were issues with ordering when saving a single stage of a recipe and so on. User testing occurred from the moment I had basic functionality in place right through to two weeks before the due date for the project, giving me around 3-4 weeks of fairly constant user testing to work with. 