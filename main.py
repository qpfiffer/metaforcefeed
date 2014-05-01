#!/usr/bin/env python2
from flask import abort, Flask, g, request, session
from olegsessions import OlegDBSessionInterface
from olegdb import OlegDB

from metaforcefeed.routes import app as routes
from metaforcefeed.utils import random_csrf, auth_user
from metaforcefeed.conprocs import app as conprocs
import sys, getopt, random, string

app = Flask('metaforcefeed')
app.register_blueprint(routes)
app.register_blueprint(conprocs)
app.config['CACHE'] = True
app.session_interface = OlegDBSessionInterface()

@app.before_request
def setup_db():
    if request.method == "POST":
        token = session.get('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)
    g.db = OlegDB()

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_csrf()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def main(argv):
    debug = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"dp",["debug", "port="])
    except getopt.GetoptError:
        print "Specifiy some options"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--debug"):
            debug = True
        elif opt in ("--port"):
            port = int(arg)

    if debug:
        app.config['CACHE'] = False

    app.run(debug=debug, port=port)

if __name__ == '__main__':
    main(sys.argv[1:])
