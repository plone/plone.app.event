from AccessControl.Permission import addPermission
from zope.i18nmessageid import MessageFactory

import icalendar
import logging


logger = logging.getLogger(__name__)
packageName = __name__
_ = MessageFactory("plone")

# We are not yet ready to use the standard zoneinfo implementation
# introduced in icalendar 6.  For starters, the tests fail when
# Products.DateRecurringIndex.index.index_object is called:
# SystemError: <class 'BTrees.IIBTree.IISet'> returned a result with an exception set
try:
    icalendar.use_pytz()
    logger.info("icalendar has been set up to use pytz instead of zoneinfo.")
except AttributeError:
    # If use_pytz does not exist, we either have an older icalender version
    # that only supports pytz anyway, or we have a newer version that no
    # longer supports it at all.
    pass

# BBB Permissions
PORTAL_ADD_PERMISSION = "Add portal events"  # CMFCalendar/ATCT permissions

addPermission(
    PORTAL_ADD_PERMISSION,
    (
        "Manager",
        "Site Administrator",
        "Owner",
    ),
)
