# D&D Character Auto-Generator
#### Video Demo:  [https://youtu.be/H5a77db3ZaM](https://youtu.be/H5a77db3ZaM)

<br/>

#### **Description**:

<br/>

This project is a web application that uses Python, Javascript and SQL to auto-generate character ideas for Dungeons and Dragons campaigns, and subsequently store any ideas liked by the user. I personally enjoy D&D a lot, but can be fairly indecisive when it comes to character creation, so I figured this could be a cool and fun workaround for other indecisive people like myself.

<br/>

I started the project with a similar framework to a previous assignment in my CS50 course, the C$50 Finance web application. This included `app.py`, where the majority of my functions would go, `dnd.db`, my aptly named sqlite3 database, and `extra.py`, for any additional functionality I wanted to add to the main code without adding clutter.

<br/>

#

## `dnd.db`:
I implemented three separate tables in this sqlite3 database, all of which connect to each other in some way via foreign keys and the like. The `users` table includes a username and hash for implementation of the `register()` and `login()` functions, as well as a unique id serving as the primary key.

<br/>

`characters` includes a unique id for each character serving as the primary key, but also includes a user_id column that connects to `users` as a *foreign key* referencing id. This table also includes race, class, and names for all inserted characters.

<br/>

`stats` has columns for each stat class, namely strength (str), dexterity (dex), constitution (con), intelligence (int), wisdom (wis) and charisma (cha). This table also includes a char_id value, that connects to `characters` as a *foreign key* referencing that table's id values.

<br/>

#

## `app.py`:

<br/>

I first imported the necessary libraries for the project, namely `cs50`, `flask`, `flask_session`, and my other file, `extra`. I also imported the entire `random` library, as well as some functions from `werkzeug.security` for added functionality.

<br/>

### Global Variables
I set a few global variables, `CLASSES`, `RACES`, `NAMES`, and `STATS`, all of which had fairly static data I knew I'd be using throughout the program. Classes and races were compiled from DnDBeyond, and I found a large list of names online from [Nerds on Earth](https://nerdsonearth.com/2018/08/dnd-names-2/).
<br/><br/>

#### `after_request(response)`
This function makes sure that the user responses aren't cached.

<br/>

#### `index()`

This returns the home page, `index.html`, for the web application, introducing the user to the page and describing what it is the application does.

<br/>

This function also defines two choices that pop up on the home screen. `#option1`, or `random`, generates a completely random character for the user, including a race, class, name, and rolling stats for the character. `#option2`, or `newchar`, simply redirects the user to the new character page for a more hands-on experience.

<br/>

#### `register()`

This function first clears any sessions that are currently open. If the request is a `GET` request, the function renders the template `register.html`. If the request is `POST`, we assume the user has submitted the form to register.

<br/>

All necessary variables are collected using `request.form.get()`. A few conditionals follow this code to prevent users from not inputting a username, password, or not matching the password and confirmation inputs. This included using my sqlite3 code, `dnd.db`, to find the specific username in my database and, if already existing, outputting an error specifying that.

<br/>

Finally, I used the function `generate_password_hash` from the `werkzeug.security` library to create a hash for the password the user inputted, so as not to input the actual password into my database, and inserted both the username and hash of the password into the `users` table.

<br/>

#### `login()`

This function started out very functionally similar to `register()`, checking input values and using conditionals to return potential errors. The main difference is that we are checking that both the username and the password's hash *exist* in `dnd.db`, not that they don't exist.

<br/>

For this we used sqlite3 to select all info from our users table where the username was the one inputted, and from there used `check_password_hash()`, another function from `werkzeug.security`, to make sure the hash matches what would be generated from the user's input. If all of this ends up passing, the result is labeling the user's id as the session's user id, and redirecting to the home page, effectively logging them in.

<br/>

#### `newchar()`
This function, when used in a `GET` request, renders `newchar.html`, the page where the `POST` request for this function takes place.

<br/>

The user fills out a form including two dropdown menus, one for class and one for race, and both are recorded via `request.form.get()`. Importantly, neither dropdown *needs* to be selected for the request to go through, as the following conditionals randomize the class and race choices if this is the case. I did this mainly for a user-friendly experience, as not everyone knows the exact class or race they want their character to be, but some people do.

<br/>

A random name is chosen regardless of form choice, and stats are rolled at random using `stat_roller()`, a function I created in `extra.py` that will be detailed later in this README file. Finally, the request renders the check template `check.html`, which, notably, includes a form that triggers the next function to be discussed.

<br/>

#### `confirm(dndClass, dndRace, dndName)`
In contrast to the majority of the other functions in this application, this function takes three inputs, all of which come from the `newchar` page prior. This is because this function inserts said inputs into `dnd.db` if the user likes the character generated for them. `check.html` includes a sentence at the very top that describes the character to the user, followed by a form asking if they'd like to add the character.

<br/>

If they click yes, `db.execute()` works to insert not only the character's class, name, and race, but also their stats, which are inputted through a special SELECT statement that uses the character's unique id. The user is then redirected to the `/chars` route, or the `characters()` function.

<br/>

#### `characters()`
This function, as a `GET` request, simply acts to select the character information from `dnd.db` and subsequently render the `characters.html` page, where all of the user's characters, and their relevant data, are shown in a table. The character table has additional functionality using Javascript, in that a user can **hide** or **show** stats using a button at the top of the table, depending on what they'd like to see at that present moment.

<br/>

As a `POST` request, this function is used as a stat-reroller. There is a drop down menu at the top of the table, next to a "reroll" button, with all the names of the user's current characters. The user's choice is gathered, and a for loop iterates through the user's characters until a name matches the choice. When this is the case, the global `STATS` variable is updated to a new random stat roll, using `stat_roller()`.

<br/>

After the character's unique id is selected as well, the stats for that character id are updated accordingly with the new global variable's values. Finally, the user's character info and stats are re-selected and the character template is rendered again to reflect any changes.

<br/>

#### `remover()`
This function operates on the `characters.html` template as well, and acts to remove a character's info from the table as well as from `dnd.db`. Each character row in the table has a form element appended, with a checkbox with a name corresponding to the character name, as well as a submit button that simply says "Remove?"

<br/>

The function, therefore, iterates through the characters and, when `request.form.get("name in question")`, this means the box was checked, and the removal can occur. This simply entails two separate DELETE statements via `db.execute` that get rid of that character's stat data, and then their character data. The function ends by redirecting to the `/chars` route again, which essentially refreshes the page, showing that that character has indeed been deleted from the database.

<br/>

#### `logout()`
While this doesn't need too much explanation, this function simply clears the session, and redirects to the `/` route. In this case, since `/` has the `@login_required` decorator function included, it returns the user to the login screen as a result.

<br/>

#

## `extra.py`:

<br/>

#### `login_required(f)`
This function makes use of *decorated functions*, so that if a user tries to get to a particular page without being logged in, it will redirect the user to the login page automatically. This helps clean up the webpage a bit and makes it a bit safer for users.

<br/>

#### `error(message, code=400)`
All this function does is return an error message when a step in the login or registration process is skipped by the user.

<br/>

#### `stat_roller()`
I made this function to mimic the actual dice rolls made to roll stats in a D&D campaign. Common convention is to roll four d6s (six-sided dice), remove the lowest of the four rolls, and add the remaining three rolls together. The resulting sum is the stat you were rolling for. I implemented this using the `random` library, as well as python's included `remove(min())` functionality, to get rid of the lowest number in a list.

<br/>

#

<br/>

## Potential Improvements / Future Functionality

<br/>

While I am happy with how my code came out at the end of the day, and feel good submitting it, it feels noteworthy to address some features that I wish to learn about / implement in the future. This helps solidify to me that this project was in fact a learning experience, and that even when a project is "finished", there's always more to learn.

<br/>

In particular, I really want to improve the user-friendliness and general aesthetic of the `characters.html` page. The remove button required the user to check a box prior to being able to remove their character which wasn't the most intuitive thing. I'd like to learn more about using SQL from within Javascript so I don't necessarily need a form and subsequent python code to remove info from the database, and can instead do so by solely pressing the "Remove?" button.

<br/>

Another aspect of `characters.html` I'd like to improve in the future is the appearance of the table. The stats ended up being spaced oddly, most likely due to the presence of the reroll dropdown menu, as this acted as a `.table-column` element and was much wider than every other element of the same type. Additionally, the "Hide Stats" button didn't really make the screen any more accessible to the user, so I'd like to look into that more in the future as well.

<br/>

## Key Note

<br/>

This application is not able to be deployed to a production environment. GCP was going to be used for this purpose, but it does not support sqlite3. Production-ready formatting may be implemented at a later date using MySQL or other SQL database. Thank you for your understanding. 

Thank you for reading, and for taking the time to look at my project. I had a lot of fun making it from the ground up, and I look forward to creating future projects as well :D
