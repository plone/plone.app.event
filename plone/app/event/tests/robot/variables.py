from datetime import datetime
from datetime import timedelta


# important for MONTHNAME
NOW = datetime.now() + timedelta(days=1)
EVENT_START_ISO = NOW.strftime("%Y-%m-%dT%H:00")

END = NOW + timedelta(hours=1)
EVENT_END_ISO = END.strftime("%Y-%m-%dT%H:00")
