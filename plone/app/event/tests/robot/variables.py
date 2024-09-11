from datetime import datetime
from datetime import timedelta


NOW = datetime.now() + timedelta(days=1)
END = NOW + timedelta(hours=1)

EVENT_START_ISO = NOW.strftime("%Y-%m-%dT%H:00")
EVENT_END_ISO = END.strftime("%Y-%m-%dT%H:00")
