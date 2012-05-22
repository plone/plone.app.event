from plone.app.event.base import get_occurrences
from plone.app.event.base import get_portal_events
from plone.app.event.base import guess_date_from
from zope.publisher.browser import BrowserView


class Occurrences(BrowserView):

    def get_data(self):
        start = guess_date_from(self.request.form.get('start', ''))
        result = get_portal_events(self.context, range_start=start)
        return get_occurrences(self.context, result, range_start=start)
