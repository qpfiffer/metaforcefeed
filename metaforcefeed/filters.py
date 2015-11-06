# -*- coding: UTF-8 -*-
from datetime import datetime

badges = [u"☹", u"♞", u"★", u"☎", u"☂", u"📱", u"📴", u"📶", u"📼", u"🔀"]
colors = [u"FF667F", u"FF9966", u"FFE666", u"CCFF66", u"66CCFF"]

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
