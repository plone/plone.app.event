from plone.app.event.base import default_timezone
from plone.app.event.base import get_occurrences
from plone.app.event.base import get_portal_events
from zope.publisher.browser import BrowserView
import datetime
import pytz


class Occurrences(BrowserView):

    format = '%Y-%m-%d'

    def get_data(self):
        start = self.guess_start_date()
        result = get_portal_events(self.context, range_start=start)
        return get_occurrences(self.context, result, range_start=start)

    def guess_start_date(self):
        """
        Returns the start date if a query string 'start' with a date
        format is passed in for querying events.

        Otherwise None is returned.
        """
        try:
            dateobj = datetime.datetime.strptime(
                self.request.form.get('start', ''), self.format)
        except ValueError:
            return

        dateobj = pytz.timezone(
                default_timezone(self.context)).localize(dateobj)
        return dateobj
