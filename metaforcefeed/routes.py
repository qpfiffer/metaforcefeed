from flask import (g, request, current_app, Blueprint, render_template,
                   redirect, url_for, session, abort, Response)
from werkzeug.exceptions import BadRequestKeyError

#from metaforcefeed.cache import ol_view_cache
from metaforcefeed.utils import (ping_summary, sign_up, auth_user,
                                 _get_summary_str, ALL_ITEMS_LIST)
import json, time, calendar

app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
def root():
    from metaforcefeed.utils import ALL_ITEMS_LIST
    #TODO: Refactor this when prefix matching is done.
    all_items = g.db.get(ALL_ITEMS_LIST) or []

    passed_items = []
    for item_key in all_items:
        passed_items.append(g.db.get(item_key))

    passed_items = sorted([x for x in passed_items if x],
        key=lambda x: x['pings'], reverse=False)

    return render_template("index.html", items=passed_items)

@app.route("/ping/<slug>", methods=['POST'])
def ping(slug):
    to_return = { 'success': True, 'error': "" }
    if not slug:
        return abort(404)

    gmtime = time.gmtime()
    seconds = int(calendar.timegm(gmtime))
    expiration = seconds + (60 * 60 * 24) #24 hours later

    ping_obj = {
        'pinged': slug,
        'when': seconds
    }
    pings = session.get('pings', None)
    if not pings:
        session['pings'] = { slug: ping_obj }
        ping_summary(g.db, slug, expiration)
        return Response(json.dumps(to_return), mimetype="application/json")
    else:
        last_ping = pings.get(slug, None)
        if not last_ping:
            created, obj = ping_summary(g.db, slug, expiration)
            if created:
                session['pings'][slug] = ping_obj
                return Response(json.dumps(to_return), mimetype="application/json")
            else:
                to_return['error'] = obj
                return Response(json.dumps(to_return), mimetype="application/json")

        if last_ping['when'] > expiration:
            created, obj = ping_summary(g.db, slug, expiration)
            if created:
                session['pings'][slug] = ping_obj
                return Response(json.dumps(to_return), mimetype="application/json")
            else:
                to_return['error'] = obj
                return Response(json.dumps(to_return), mimetype="application/json")

        to_return['success'] = False
        to_return['error'] = "You need to wait 24 hours to ping again."

    return Response(json.dumps(to_return), mimetype="application/json")

@app.route("/item/<slug>", methods=['GET'])
def item(slug):
    if not slug:
        return abort(404)

    item = None
    item = g.db.get(_get_summary_str(slug))

    return render_template("item.html", item=item)

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

@app.route("/item/<slug>/delete", methods=['POST'])
def delete(slug):
    if not slug:
        return abort(404)

    item = None
    item = g.db.delete(_get_summary_str(slug))

    # NOW WE HAVE TO GO DELETE THEM FROM THE LIST
    all_items = g.db.get(ALL_ITEMS_LIST)
    all_items = filter(lambda x: x != _get_summary_str(slug), all_items)
    g.db.set(ALL_ITEMS_LIST, all_items)
    return redirect(url_for('metaforcefeed.root'))

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
