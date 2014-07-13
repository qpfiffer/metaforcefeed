#!/usr/bin/env python2
from flask import abort, Flask, g, request, session
from flaskext.markdown import Markdown
from functools import wraps
from olegsessions import OlegDBSessionInterface
from olegdb import OlegDB

from metaforcefeed.routes import app as routes
from metaforcefeed.utils import random_csrf, auth_user, enable_admin
from metaforcefeed.conprocs import app as conprocs
from metaforcefeed.filters import unix_to_human
import sys, getopt, random, string, json, time

app = Flask('metaforcefeed')
app.register_blueprint(routes)
app.register_blueprint(conprocs)
app.config['CACHE'] = True
app.session_interface = OlegDBSessionInterface()
app.jinja_env.filters['unix_to_human'] = unix_to_human
Markdown(app)

def profile_wrapper(to_profile):
    all_funcs = {x:getattr(to_profile, x) for x in dir(to_profile)
            if str(type(getattr(to_profile, x))) == "<type 'instancemethod'>"\
            and not x.startswith("__")}

    calls_dict = {}

    def delta_wrapper(to_profile, old_function):
        @wraps(old_function)
        def new(*args, **kwargs):
            start = time.time()
            ret = old_function(*args, **kwargs)
            time_taken = (time.time() - start) * 1000
            call_obj = {
                "time": time_taken,
                "ms": "%.2fms" % (time_taken)
            }
            name = str(old_function)
            #print "{} {}".format(name, call_obj["ms"])

            if calls_dict.get(name):
                calls_dict[name].append(call_obj)
            else:
                calls_dict[name] = [call_obj]

            #print "Times called: {}".format(len(calls_dict[name]))

            return ret
        return new

    for name,old_function in all_funcs.iteritems():
        setattr(to_profile, name, delta_wrapper(to_profile, old_function))
    return to_profile

@profile_wrapper
class ProlegDB(OlegDB):
    pass

@app.before_request
def setup_db():
    if request.method == "POST":
        token = session.get('_csrf_token', None)
        in_form = token == request.form.get('_csrf_token')
        try:
            stuff = json.loads(request.data).get("_csrf_token")
            in_data = stuff == token
        except Exception as e:
            print e
            in_data = False
        if not token or not (in_form or in_data):
            abort(403)
    g.db = ProlegDB()

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_csrf()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def main(argv):
    debug = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"dpa",["debug", "port=", "admin-enable="])
    except getopt.GetoptError:
        print "Specifiy some options"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--debug"):
            debug = True
        elif opt in ("--port"):
            port = int(arg)
        elif opt in ("--admin-enable"):
            enable_admin(OlegDB(), arg)

    if debug:
        app.config['CACHE'] = False

    app.run(debug=debug, port=port)

if __name__ == '__main__':
    main(sys.argv[1:])
