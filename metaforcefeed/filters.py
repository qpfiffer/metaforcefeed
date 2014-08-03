# -*- coding: UTF-8 -*-
from datetime import datetime

badges = [u"☹", u"♞", u"★", u"☎", u"☂"]

def unix_to_human(timestamp_str):
    time = float(timestamp_str)
    return unicode(datetime.fromtimestamp(time))

def user_badge(username):
    username_hash = hash(username)
    return u'<span class="user_badge">{}</span>'.format(badges[username_hash % len(badges)])
