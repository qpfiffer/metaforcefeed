from flask import g, request, current_app, Blueprint, render_template,\
        redirect, url_for, session

from metaforcefeed.cache import ol_view_cache


app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
@ol_view_cache
def root():
    #TODO: Refactor this when prefix matching is done.
    all_items = g.db.get("all_items") or []

    for item_key in all_items:
        pass

    return render_template("index.html")

@app.route("/submit", methods=['GET', 'POST'])
def submit():
    if not session.get('username', None):
        return redirect(url_for('metaforcefeed.login'))

    if request.method == 'POST':
        return redirect(url_for('metaforcefeed.root'))

    return render_template("submit.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('metaforcefeed.root'))
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('metaforcefeed.root'))
    return render_template("register.html")
