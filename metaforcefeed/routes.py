from datetime import datetime
from flask import (g, request, current_app, Blueprint, render_template,
                   redirect, url_for, session, abort, Response)
from werkzeug.exceptions import BadRequestKeyError

#from metaforcefeed.cache import ol_view_cache
from metaforcefeed.utils import (ping_summary, sign_up, auth_user, set_user,
                                 _get_summary_str, ALL_ITEMS_LIST, edit_idea,
                                 log_action, ALL_EVENTS_LIST)
from metaforcefeed.conprocs import get_user
import json, time, calendar

app = Blueprint('metaforcefeed', __name__, template_folder='templates')

@app.route("/", methods=['GET'])
def root():
    from metaforcefeed.utils import ALL_ITEMS_LIST, ALL_ACTIONS_LIST
    #TODO: Refactor this when prefix matching is done.
    all_items = g.db.get(ALL_ITEMS_LIST) or []
    all_actions = g.db.get(ALL_ACTIONS_LIST) or []

    # Get all ideas from the db:
    passed_items = []
    for item_key in all_items:
        passed_items.append(g.db.get(item_key))

    # Filter out Nones and sort by pings:
    passed_items = sorted([x for x in passed_items if x],
        key=lambda x: x['pings'], reverse=False)

    # Get last 25 actions from the db:
    actions = []
    for action_key in all_actions:
        actions.append(g.db.get(action_key))

    # Filter by newest and get only the last 25:
    actions = sorted([x for x in actions if x],
            key=lambda x: x['created_at'], reverse=True)[:25]

    return render_template("index.html", items=passed_items, all_actions=actions)

@app.route("/ack/<slug>/<stamp>", methods=['POST'])
def calendar_event_ack(slug, stamp):
    to_return = { 'success': True, 'error': "" }
    user = get_user()['user']

    if not user:
        return abort(503)

    if not slug:
        return abort(404)

    from metaforcefeed.utils import ack_to_event, _get_event_str
    created, err = ack_to_event(g.db, slug, stamp, user)

    if not created:
        extra = err
    else:
        event = g.db.get(_get_event_str(slug, stamp))
        action_str = '{} ACK\'d to "{}, {}".'.format(user["username"], stamp, slug)
        log_action(g.db, action_str)

    return redirect(url_for('metaforcefeed.calendar_event', slug=slug, stamp=stamp))

@app.route("/deack/<slug>/<stamp>", methods=['POST'])
def calendar_event_de_ack(slug, stamp):
    to_return = { 'success': True, 'error': "" }
    user = get_user()['user']

    if not user:
        return abort(503)

    if not slug:
        return abort(404)

    from metaforcefeed.utils import de_ack_to_event, _get_event_str
    created, err = de_ack_to_event(g.db, slug, stamp, user)

    if not created:
        extra = err
    else:
        event = g.db.get(_get_event_str(slug, stamp))
        action_str = '{} DE-ACK\'d "{}, {}".'.format(user["username"], stamp, slug)
        log_action(g.db, action_str)

    return redirect(url_for('metaforcefeed.calendar_event', slug=slug, stamp=stamp))

@app.route("/ping/<slug>", methods=['POST'])
def ping(slug):
    to_return = { 'success': True, 'error': "" }
    user = get_user()['user']

    if not user:
        return abort(503)

    if not slug:
        return abort(404)

    gmtime = time.gmtime()
    seconds = int(calendar.timegm(gmtime))
    expiration = seconds + (60 * 60 * 24) #24 hours later

    ping_obj = {
        'pinged': slug,
        'when': seconds
    }
    pings = user.get('pings', None)
    def _handle_creation():
        # Inline because fuck a scope
        created, obj = ping_summary(g.db, slug, expiration)
        if created:
            user['pings'][slug] = ping_obj
            set_user(g.db, user)
            to_return['ping_obj'] = obj
            return Response(json.dumps(to_return), mimetype="application/json")
        else:
            to_return['error'] = obj
            return Response(json.dumps(to_return), mimetype="application/json")

    if not pings:
        user['pings'] = { slug: ping_obj }
        set_user(g.db, user)
        return _handle_creation()
    else:
        last_ping = pings.get(slug, None)
        if not last_ping:
            return _handle_creation()

        if seconds > (last_ping['when'] + (60 * 60 * 24)):
            return _handle_creation()

        to_return['success'] = False
        to_return['error'] = "You need to wait 24 hours to ping again."

    return Response(json.dumps(to_return), mimetype="application/json")

def _timestamp(timestamp_str):
    x = datetime.fromtimestamp(float(timestamp_str))
    return x

@app.route("/calendar", methods=['GET'])
def calendar_root():
    import calendar
    all_events = g.db.get(ALL_EVENTS_LIST) or []

    passed_events = []
    for e_key in all_events:
        passed_events.append(g.db.get(e_key))

    passed_events = sorted([x for x in passed_events if x],
        key=lambda x: x['day'], reverse=False)

    happened_events = filter(lambda x: _timestamp(x['day']).date() < datetime.now().date(), passed_events)
    todays_events = filter(lambda x: _timestamp(x['day']).date() == datetime.now().date(), passed_events)
    soon_events = filter(lambda x: _timestamp(x['day']).date() > datetime.now().date(), passed_events)

    calendars = []
    current_month_int = int(datetime.today().strftime("%m"))
    for month in [(current_month_int - 1) % 12, current_month_int, (current_month_int + 1) % 12]:
        cal = calendar.HTMLCalendar(calendar.SUNDAY)
        formatted = cal.formatmonth(2015, month)
        calendars.append(formatted)

    return render_template("calendar.html", happened_events=happened_events,
            todays_events=todays_events, soon_events=soon_events, calendars=calendars)

@app.route("/item/<slug>/<stamp>/cancel", methods=['POST'])
def calendar_event_cancel(slug, stamp):
    if not slug or not stamp:
        return abort(404)

    from metaforcefeed.utils import _get_event_str
    event = g.db.get(_get_event_str(slug, stamp))

    event["cancelled"] = True
    g.db.set(_get_event_str(slug, stamp), event)

    # Log that we cancelled an event
    event = g.db.get(_get_event_str(slug, stamp))
    action_str = 'Cancelled on "{}, {}".'.format(stamp, slug)
    log_action(g.db, action_str)

    return redirect(url_for('metaforcefeed.root'))

@app.route("/calendar/event/<slug>/<stamp>", methods=['GET', 'POST'])
def calendar_event(slug, stamp):
    from metaforcefeed.utils import _get_event_str
    event = g.db.get(_get_event_str(slug, stamp))

    if not event:
        return abort(404)

    if request.method == 'POST':
        from metaforcefeed.utils import post_comment_to_event
        if not session.get('username', None):
            return redirect(url_for('metaforcefeed.login'))

        username = session['username']
        created, err = post_comment_to_event(g.db, slug, stamp, request.form['comment'], username)

        if not created:
            extra = err
        else:
            event = g.db.get(_get_event_str(slug, stamp))
            action_str = 'Commented on "{}, {}".'.format(stamp, slug)
            log_action(g.db, action_str)
        event = g.db.get(_get_event_str(slug, stamp))

    return render_template("calendar_event.html", event=event)

@app.route("/calendar/new", methods=['GET', 'POST'])
def calendar_new():
    error = None
    if not session.get('username', None):
        return redirect(url_for('metaforcefeed.login'))

    if request.method == 'POST':
        from metaforcefeed.utils import submit_event
        day = request.form.get("day")
        from_time = request.form.get("from_time")
        to_time = request.form.get("to_time")
        name = request.form.get("name")
        description = request.form.get("description")

        created, event = submit_event(g.db, day, from_time, to_time, name, description)

        if created:
            action_str = 'Created new event "{}".'.format(name)
            log_action(g.db, action_str)
            return redirect(url_for('metaforcefeed.calendar_root'))
        error = event

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("calendar_new.html", error=error, today=today)

@app.route("/item/<slug>", methods=['GET', 'POST'])
def item(slug):
    extra = None
    item = None
    if not slug:
        return abort(404)

    if request.method == 'POST':
        if not session.get('username', None):
            return redirect(url_for('metaforcefeed.login'))
        from metaforcefeed.utils import post_comment_to_item
        username = session['username']
        created, err = post_comment_to_item(g.db, slug, request.form['comment'], username)
        if not created:
            extra = err
        else:
            item = g.db.get(_get_summary_str(slug))
            action_str = 'Commented on "{}".'.format(item['short_summary'])
            log_action(g.db, action_str)


    if not item:
        item = g.db.get(_get_summary_str(slug))

    return render_template("item.html", item=item, extra=extra)

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
            action_str = 'Created new item "{}".'.format(shorts)
            log_action(g.db, action_str)
            return redirect(url_for('metaforcefeed.root'))
        error = summary

    return render_template("submit.html", error=error)

@app.route("/user/<username>", methods=['GET'])
def user_history(username):
    from metaforcefeed.utils import ALL_ACTIONS_LIST
    #TODO: Refactor this when prefix matching is done.
    all_actions = g.db.get(ALL_ACTIONS_LIST) or []

    # Get last 25 actions from the db:
    actions = []
    for action_key in all_actions:
        action = g.db.get(action_key)
        if action is not None and action['user'] == username:
            actions.append(action)

    # Filter by newest and get only the last 25:
    actions = sorted([x for x in actions if x],
            key=lambda x: x['created_at'], reverse=True)[:25]

    return render_template("user_history.html", username=username, all_actions=actions)

@app.route("/item/<slug>/edit", methods=['GET', 'POST'])
def edit(slug):
    error = None
    item = g.db.get(_get_summary_str(slug))

    if not item:
        return redirect(url_for('metaforcefeed.root'))

    if not session.get('username', None):
        return redirect(url_for('metaforcefeed.login'))

    if request.method == 'POST':
        from metaforcefeed.utils import submit_idea
        shorts = request.form.get("short_summary")
        longs = request.form.get("longer_summary")
        edited, summary = edit_idea(g.db, slug, shorts, longs)

        if edited:
            action_str = 'Edited item "{}".'.format(item['short_summary'])
            log_action(g.db, action_str)
            return redirect(url_for('metaforcefeed.root'))
        error = summary

    return render_template("edit.html", error=error, item=item)

@app.route("/item/<slug>/delete", methods=['POST'])
def delete(slug):
    if not slug:
        return abort(404)

    item = None
    item = g.db.get(_get_summary_str(slug))
    g.db.delete(_get_summary_str(slug))

    # NOW WE HAVE TO GO DELETE THEM FROM THE LIST
    all_items = g.db.get(ALL_ITEMS_LIST)
    all_items = filter(lambda x: x != _get_summary_str(slug), all_items)
    g.db.set(ALL_ITEMS_LIST, all_items)

    action_str = 'Deleted "{}".'.format(item['short_summary'])
    log_action(g.db, action_str)

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

            action_str = 'Registered.'
            log_action(g.db, action_str)

            return redirect(url_for('metaforcefeed.root'))
        # Well something didn't work right.
        error = user_obj

    return render_template("register.html", error=error)

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('metaforcefeed.root'))
