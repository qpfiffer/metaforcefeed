from flask import g, request, current_app, Blueprint, render_template, redirect

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
    if request.method == 'POST':
        return redirect(url_for('metaforcefeed.root'))
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('metaforcefeed.root'))
    return render_template("index.html")
