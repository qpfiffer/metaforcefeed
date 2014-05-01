from flask import g, request, current_app, Blueprint, render_template,\
        redirect, url_for, session
from werkzeug.exceptions import BadRequestKeyError

from metaforcefeed.cache import ol_view_cache
from metaforcefeed.utils import sign_up, auth_user


app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
@ol_view_cache
def root():
    from metaforcefeed.utils import ALL_ITEMS_LIST
    #TODO: Refactor this when prefix matching is done.
    all_items = g.db.get(ALL_ITEMS_LIST) or []

    for item_key in all_items:
        pass

    return render_template("index.html")

@app.route("/submit", methods=['GET', 'POST'])
def submit():
    error = None
    if not session.get('username', None):
        return redirect(url_for('metaforcefeed.login'))

    if request.method == 'POST':
        from metaforcefeed.utils import submit_idea
        shorts = request.form.get("short_summary")
        longs = request.form.get("longer_summary")
        created, summary = submit_idea(g.db, shorts, longs)

        if created:
            return redirect(url_for('metaforcefeed.root'))
        error = summary

    return render_template("submit.html", error=error)

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth_user(g.db, username, password):
            session.permanent = True
            session['username'] = username
            return redirect(url_for('metaforcefeed.root'))
        error = "Could not log in for some reason."
    return render_template("login.html", error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = ""
    if request.method == 'POST':
        try:
            username = request.form['username']
            password1 = request.form['password1']
            password2 = request.form['password2']
        except BadRequestKeyError:
            error = "Some data didn't make it to the front."
            return render_template("register.html", error=error)

        if len(username) == 0:
            error = "Must input username."
            return render_template("register.html", error=error)

        if password1 != password2:
            error = "Passwords do not match."
            return render_template("register.html", error=error)

        created, user_obj = sign_up(g.db, username, password1)
        if created:
            session.permanent = True
            session['username'] = user_obj['username']
            return redirect(url_for('metaforcefeed.root'))
        # Well something didn't work right.
        error = user_obj

    return render_template("register.html", error=error)

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('metaforcefeed.root'))
