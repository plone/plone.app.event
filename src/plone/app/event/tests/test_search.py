from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN
from unittest import mock


class FunctionalTestSearchEvent(AbstractSampleDataEvents):
    layer = PAEventDX_FUNCTIONAL_TESTING

    @mock.patch("plone.app.event.base.localized_now", new=PN)
    def test_searchabletext(self):
        results = self.portal.portal_catalog(SearchableText="Überraschung")
        self.assertTrue(len(results) == 1)
