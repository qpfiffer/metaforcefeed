from flask import request, current_app
from functools import wraps
import requests, time, urllib, calendar

def ol_view_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_cache_time = time.time()
        # Debug
        if not current_app.config['CACHE']:
            return f(*args, **kwargs)

        res = None
        fancy = u"{}{}{}{}{}".format(0,
                request.host,
                request.query_string,
                unicode(request.path).replace("/", "_"),
                f.func_name)
        quoted = urllib.quote(fancy.encode('ascii', 'replace'))
        print "Hash str: " + quoted

        resp = requests.get("http://localhost:8080/{}".format(quoted), stream=True)
        if resp.status_code == 404:
            res = f(*args, **kwargs)
            # 24 hours
            expiration = int(calendar.timegm(time.gmtime())) + 60 #(60 * 60 * 24)
            utf_data = res.encode('utf-8')
            requests.post("http://localhost:8080/{}".format(quoted),
                data=utf_data,
                headers={
                    "Content-Type": "text/html",
                    "X-OlegDB-use-by": expiration})
        else:
            res = resp.raw.read()

        full_time = lambda: "%.2fms" % ((time.time() - start_cache_time) * 1000)
        cache_str = "<!-- Cache time: {} -->".format(full_time())
        appended = res
        try:
            appended = "{}{}".format(res, cache_str)
        except UnicodeEncodeError:
            pass
        return appended
    return decorated_function
