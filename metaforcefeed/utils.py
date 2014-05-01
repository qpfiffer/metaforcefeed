from bcrypt import hashpw, gensalt

USERS_PREFIX = "user"
def auth_user(connection, username, pw):
    getstr = "{}{}".format(USERS_PREFIX, username)

    userobj = connection.get(getstr)
    if userobj and userobj['username'] == username:
        salt = userobj['salt']
        sent_hash = hashpw("{}{}".format(username, pw), salt)

        if sent_hash == userobj['password']:
            return True
    return False

def random_csrf():
    myrg = random.SystemRandom()
    length = 32
    # If you want non-English characters, remove the [0:52]
    alphabet = string.letters[0:52] + string.digits
    pw = str().join(myrg.choice(alphabet) for _ in range(length))
    return pw
