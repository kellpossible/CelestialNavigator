from datetime import datetime, tzinfo, timedelta

ZEROTIME = timedelta(0)

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZEROTIME

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZEROTIME