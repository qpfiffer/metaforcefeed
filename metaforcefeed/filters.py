from datetime import datetime

def unix_to_human(timestamp_str):
    time = float(timestamp_str)
    return unicode(datetime.fromtimestamp(time))
