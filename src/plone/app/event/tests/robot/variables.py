# setup dates
from datetime import datetime
from datetime import timedelta

import locale


# important for MONTHNAME
locale.setlocale(locale.LC_ALL, "en_US")

NOW = datetime.now() + timedelta(days=1)
EVENT_START_YEAR = NOW.strftime("%Y")
EVENT_START_MONTH = str(NOW.month - 1)
EVENT_START_MONTHNAME = NOW.strftime("%B")
EVENT_START_DAY = NOW.strftime("%d")
EVENT_START_HOUR = str(int(NOW.strftime("%I")))

END = NOW + timedelta(hours=1)
EVENT_END_YEAR = END.strftime("%Y")
EVENT_END_MONTH = str(END.month - 1)
EVENT_END_MONTHNAME = END.strftime("%B")
EVENT_END_DAY = END.strftime("%d")
EVENT_END_HOUR = str(int(END.strftime("%I")))
