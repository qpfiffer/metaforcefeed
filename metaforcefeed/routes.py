from flask import current_app, Blueprint, render_template

from metaforcefeed.cache import ol_view_cache


app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
@ol_view_cache
def root():
    return render_template("index.html")
