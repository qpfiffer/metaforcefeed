# -*- coding: UTF-8 -*-
from datetime import datetime

badges = [u"☹", u"♞", u"★", u"☎", u"☂", u"📱", u"📴", u"📶", u"📼", u"🔀"]
colors = [u"FF667F", u"FF9966", u"FFE666", u"CCFF66", u"66CCFF"]

taglines = ['<span style="color: #FFF; background-color: #000;"><span style="color: #FF4ABD;">nijotz</span> | You just manage their addictions until they die</span>',
            '<span style="color: #FFF; background-color: #000;">Bash disinformation campain.</span>',
            '<span style="color: #4DAFA2; background-color: #000;"> // continue on with life!! </span>'
            ]

def unix_to_human(timestamp_str):
    time = float(timestamp_str)
    return unicode(datetime.fromtimestamp(time))

def event_to_human(timestamp_str):
    x = datetime.fromtimestamp(float(timestamp_str))
    return x.strftime("%Y-%m-%d")

def user_badge(username):
    username_hash = hash(username)
    badge = badges[username_hash % len(badges)]
    color = colors[username_hash % len(colors)]
    return u'<span style="color: #{}">{}</span>'.format(color, badge)

def random_tagline(x):
    from random import randint
    return taglines[randint(0, len(taglines))]
