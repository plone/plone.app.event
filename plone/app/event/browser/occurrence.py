from Products.CMFPlone.PloneBatch import Batch
from zope.publisher.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.app.event.base import get_occurrences
from plone.app.event.base import get_portal_events
from plone.app.event.base import guess_date_from


class Occurrences(BrowserView):

    def get_data(self):
        start = guess_date_from(self.request.form.get('start', ''))
        b_size = self.request.form.get('b_size', 20)
        b_start = self.request.form.get('b_start', 0)
        result = get_portal_events(self.context, range_start=start)
        return Batch(
            get_occurrences(self.context, result, range_start=start),
            b_size,
            b_start)
