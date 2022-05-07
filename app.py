import random

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from extra import login_required, error, stat_roller
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///dnd.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

CLASSES = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin",
            "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Artificer"]

RACES = ["Dragonborn", "Dwarf", "Elf", "Gnome", "Half-Elf", "Halfling", "Half-Orc", "Human", "Tiefling",
            "Leonin", "Satyr", "Aarakocra", "Genasi", "Goliath", "Aasimar", "Goblin", "Hobgoblin",
            "Kenku", "Kobold", "Orc", "Tabaxi"]

NAMES = []

STATS = {
        "STR": None,
        "DEX": None,
        "CON": None,
        "INT": None,
        "WIS": None,
        "CHA": None
}


with open("/workspaces/97992904/project/static/names.txt") as f:
    for line in f:
        NAMES.append(line)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":
        if request.form["options"] == "random":

            dndClass = random.choice(CLASSES)
            dndRace = random.choice(RACES)
            dndName = random.choice(NAMES)

            for key in STATS:
                STATS[key] = stat_roller()

            return render_template("check.html", dndClass=dndClass, dndRace=dndRace, dndName=dndName, stats=STATS)

        else:
            return redirect("/newChar")

    else:

        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return error("Please input a username", 400)

        elif not password:
            return error("Please input a password", 400)

        elif confirmation != password:
            return error("Passwords do not match", 400)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) > 0:
            return error("Username already exists", 400)

        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return error("Please input a username", 400)

        elif not password:
            return error("Please input a password", 400)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return error("Invalid username and/or password, please try again.")

        session["user_id"] = user[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/newChar", methods=["GET", "POST"])
@login_required
def newchar():

    if request.method == "POST":

        dndClass = request.form.get("classes")
        dndRace = request.form.get("races")

        if dndClass == "none":
            dndClass = random.choice(CLASSES)

        if dndRace == "none":
            dndRace = random.choice(RACES)

        dndName = random.choice(NAMES)

        for key in STATS:
            STATS[key] = stat_roller()

        return render_template("check.html", dndRace=dndRace, dndClass=dndClass, dndName=dndName, stats=STATS)

    else:

        return render_template("newchar.html", CLASSES = CLASSES, RACES = RACES)


@app.route("/confirmchar/<dndClass>/<dndRace>/<dndName>", methods=["GET", "POST"])
@login_required
def confirm(dndClass, dndRace, dndName):

    if request.method == "POST":
        if request.form["option"] == "yes":

            db.execute("INSERT INTO characters (user_id, name, class, race) VALUES (?, ?, ?, ?)",
                        session["user_id"], dndName, dndClass, dndRace)

            idCharacter = db.execute("SELECT id FROM characters WHERE name = ? AND class = ? AND race = ?",
                                        dndName, dndClass, dndRace)

            db.execute("INSERT INTO stats (char_id, str, dex, con, int, wis, cha) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (idCharacter[0])["id"], STATS["STR"], STATS["DEX"], STATS["CON"], STATS["INT"], STATS["WIS"], STATS["CHA"])

            return redirect("/chars")

        else:
            return redirect("/newChar")

    else:
        return redirect("/newChar")


@app.route("/chars", methods=["GET", "POST"])
@login_required
def characters():

    if request.method == "POST":

        characterNames = db.execute("SELECT name FROM characters WHERE user_id = ?", session["user_id"])

        rerollName = request.form.get("rerolls")

        for reroll in characterNames:
            if reroll["name"] == rerollName:
                for key in STATS:
                    STATS[key] = stat_roller()

        characterId = (db.execute("SELECT id FROM characters WHERE name = ?", rerollName))[0]["id"]

        db.execute("UPDATE stats SET str = ?, dex = ?, con = ?, int = ?, wis = ?, cha = ? WHERE char_id = ?",
                        STATS["STR"], STATS["DEX"], STATS["CON"],
                        STATS["INT"], STATS["WIS"], STATS["CHA"], characterId)

        characters = db.execute("SELECT * FROM characters WHERE user_id = ? ORDER BY id", session["user_id"])
        stats = db.execute("SELECT * FROM stats WHERE char_id IN (SELECT id FROM characters WHERE user_id = ?) ORDER BY char_id", session["user_id"])

        return render_template("characters.html", characters=characters, stats=stats)

    else:

        characters = db.execute("SELECT * FROM characters WHERE user_id = ? ORDER BY id", session["user_id"])
        stats = db.execute("SELECT * FROM stats WHERE char_id IN (SELECT id FROM characters WHERE user_id = ?) ORDER BY char_id", session["user_id"])

        return render_template("characters.html", characters=characters, stats=stats)


@app.route("/charsremove", methods=["GET", "POST"])
@login_required
def remover():

    if request.method == "POST":

        characterNames = db.execute("SELECT name FROM characters WHERE user_id = ?", session["user_id"])
        for character in characterNames:
            removeName = character["name"]
            if request.form.get(removeName):

                db.execute("DELETE FROM stats WHERE char_id = (SELECT id FROM characters WHERE name = ? AND user_id = ?)",
                                removeName, session["user_id"])

                db.execute("DELETE FROM characters WHERE name = ? AND user_id = ?",
                                removeName, session["user_id"])

        return redirect("/chars")

    else:

        return redirect("/chars")


@app.route("/logout")
@login_required
def logout():

    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
