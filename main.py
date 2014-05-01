#!/usr/bin/env python2
from flask import Flask, g, request, session
from olegsessions import OlegDBSessionInterface

from metaforcefeed.routes import app as routes

app = Flask('metaforcefeed')
app.register_blueprint(routes)
app.config['CACHE'] = True
app.session_interface = OlegDBSessionInterface()

def main(argv):
    debug = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["debug", "port="])
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
