import datetime


def humanize_time(timestamp: str) -> str:
    creation_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=datetime.UTC
    )
    t = datetime.datetime.now(datetime.UTC) - creation_time

    if t.days > 0:
        age = f"{t.days}d"
    elif t.seconds >= 3600:
        age = f"{t.seconds // 3600}h"
    elif t.seconds >= 60:
        age = f"{t.seconds // 60}m"
    else:
        age = f"{t.seconds}s"

    return age
