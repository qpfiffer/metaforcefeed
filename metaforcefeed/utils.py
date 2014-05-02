from bcrypt import hashpw, gensalt
from calendar import calendar
from slugify import slugify

from metaforcefeed.conprocs import get_user

import random, string, time

ALL_ITEMS_LIST = "all_items"
USERS_PREFIX = "users"
SUMMARY_PREFIX = "summary"
SCHEMA_VERSION = "0001"

def _get_user_str(username):
    return "{}{}".format(USERS_PREFIX, username)

def _get_summary_str(slug):
    return "{}{}".format(SUMMARY_PREFIX, slug)

def _hash_pw(username, pw, salt):
    return hashpw("{}{}".format(username, pw), salt)

def ping_summary(connection, slug, expiration):
    key = _get_summary_str(slug)
    summary = connection.get(key)

    if not summary:
        return (False, "Summary with that key does not exist.")

    summary['pings'] = summary['pings'] + 1
    connection.set(key, summary)

    return (True, summary)
def submit_idea(connection, short_summary, long_summary):
    error = ""
    if not short_summary or len(short_summary) == 0:
        return (False, "Short summary is blank.")

    if not long_summary or len(long_summary) == 0:
        return (False, "Long summary is blank.")

    user = get_user()["user"]

    if not user:
        return (False, "User not logged in.")

    slug = slugify(short_summary)
    summary = {
        "slug": slug,
        "api_version": SCHEMA_VERSION,
        "created_by": user["username"],
        "comments": [],
        "short_summary": short_summary,
        "long_summary": long_summary,
        "pings": 0
    }

    key = _get_summary_str(slug)
    connection.set(key, summary)

    # TODO: Refactor this when we have compare-and-set
    all_items = connection.get(ALL_ITEMS_LIST)
    if all_items:
        all_items.append(key)
    else:
        all_items = [key]
    connection.set(ALL_ITEMS_LIST, all_items)

    return (True, summary)

def auth_user(connection, username, pw):
    getstr = _get_user_str(username)

    userobj = connection.get(getstr)
    if userobj and userobj['username'] == username:
        salt = userobj['salt']
        sent_hash = _hash_pw(username, pw, salt)

        if sent_hash == userobj['password']:
            return True
    return False

def sign_up(connection, username, password, admin=False):
    salt = gensalt()
    pwhash = _hash_pw(username, password, salt)
    user = connection.get(_get_user_str(username))

    if not user:
        new_user = {
            "api_version": SCHEMA_VERSION,
            "username": username,
            "password": pwhash,
            "salt": salt,
            "admin": admin
        }
        connection.set(_get_user_str(username), new_user)
        return (True, new_user)
    else:
        return (False, "Username already taken.")
    return (False, "Could not create user for some reason.")

def random_csrf():
    myrg = random.SystemRandom()
    length = 32
    # If you want non-English characters, remove the [0:52]
    alphabet = string.letters[0:52] + string.digits
    pw = str().join(myrg.choice(alphabet) for _ in range(length))
    return pw
