from flask import g, current_app, Blueprint, render_template

from metaforcefeed.cache import ol_view_cache


app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
@ol_view_cache
def root():
    items = g.db.get("all_items") or []
    return render_template("index.html")
