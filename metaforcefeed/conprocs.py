from flask import g, current_app, Blueprint, session

app = Blueprint("metaforcefeed_cp", __name__, template_folder='templates')

@app.app_context_processor
def get_user():
    from metaforcefeed.utils import _get_user_str
    user = None
    username = session.get("username")
    if username:
        oleg = g.db
        user_str = _get_user_str(username)
        user = oleg.get(user_str)

    return {"user": user}
