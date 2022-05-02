from flask import redirect, render_template, request, session
from functools import wraps
import random

# define login_required function using decorators (research decorators)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# define error function to redirect to error page

def error(message, code=400):
    return render_template("error.html", code = code, message = message), code


def stat_roller():

    stat = 0

    rolls = random.sample(range(1, 7), 4)

    rolls.remove(min(rolls))

    for roll in rolls:
        stat += roll

    return stat