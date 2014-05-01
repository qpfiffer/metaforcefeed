from bcrypt import hashpw, gensalt
import random, string

USERS_PREFIX = "users"
def _get_user_str(username):
    return "{}{}".format(USERS_PREFIX, username)

def _hash_pw(username, pw, salt):
    return hashpw("{}{}".format(username, pw), salt)

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
