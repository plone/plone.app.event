from plone.app.event.base import default_timezone
from plone.app.event.interfaces import IEventSettings
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.event.utils import default_timezone as os_default_timezone
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest2 as unittest


class TimezoneTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        set_env_timezone('UTC')
        set_timezone('UTC')

    def test_timezone_vocabulary(self):
        tzvocab = getUtility(IVocabularyFactory, 'plone.app.event.Timezones')
        tz_list = [item.value for item in tzvocab(self.portal)]
        self.assertTrue('Africa/Abidjan' in tz_list)
        self.assertTrue('CET' not in tz_list)

    def test_timezone_vocabulary_query(self):
        tzvocab = getUtility(IVocabularyFactory, 'plone.app.event.Timezones')
        tz_list = [item.value for item in tzvocab(self.portal, query='vienna')]
        self.assertTrue('Europe/Vienna' in tz_list)
        self.assertTrue(len(tz_list) == 1)

    def test_available_timezones_vocabulary(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")

        # initially, all zones are available in AvailableTimezones
        all_zones_vocab = getUtility(
            IVocabularyFactory,
            'plone.app.event.Timezones'
        )(self.portal)
        avail_zones_vocab = getUtility(
            IVocabularyFactory,
            'plone.app.event.AvailableTimezones'
        )(self.portal)
        self.assertTrue(len(all_zones_vocab) == len(avail_zones_vocab) != 0)

        # let's limit it to the first 10 zones of all_zones
        all_zones = [term.value for term in all_zones_vocab]
        settings.available_timezones = all_zones[0:10]

        # the AvailableTimezones vocabulary must instantiated again, to reflect
        # those changes
        del avail_zones_vocab
        avail_zones_vocab = getUtility(
            IVocabularyFactory,
            'plone.app.event.AvailableTimezones'
        )(self.portal)

        # the length of the avail_zones_vocab is still the same as
        # all_zones_vocab
        self.assertTrue(len(all_zones_vocab) == len(avail_zones_vocab) != 0)
        # but when iterating over every item, the length equals the
        # available_timezones setting.
        # this magic is done by collective.elephantvocabulary and has the
        # purpose that timezones are still available for events or users, who
        # used them, even if the portal manager retracked them later.
        self.assertTrue(len([item for item in avail_zones_vocab]) == 10)

        # Test querying AvailableTimezones vocabulary
        filtered_zones_vocab = getUtility(
            IVocabularyFactory,
            'plone.app.event.AvailableTimezones'
        )(self.portal, query='vienna')
        # filtered all items down to one
        self.assertTrue(len(filtered_zones_vocab) == 1)
        # iterating over all items returns empty list, since filtered item
        # isn't in available zones
        self.assertTrue(len([item for item in filtered_zones_vocab]) == 0)

    def test_default_timezone(self):
        self.assertTrue(os_default_timezone() == default_timezone() == 'UTC')

        reg = getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")

        settings.portal_timezone = "Europe/Vienna"
        self.assertTrue(default_timezone() == 'Europe/Vienna')
