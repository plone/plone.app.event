# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import pytz
import unittest2 as unittest


class ControlpanelTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])
        set_env_timezone('UTC')
        set_timezone('UTC')

    def test_current_datetime_in_controlpanel(self):
        """Oskar Öhman is a successful CEO of his startup company specialized
        in Toys. He's a sharp thinker and an even sharper HTML programmer (he
        thinks). His business to build cheap toys in China and sell them as
        quality build in Finnland brings him quite a huge turnaround in profit.

        With his new venture to throw kids parties where he can sell his toys,
        he needs a system to schedule and announce events. One of his
        developers installed him a Plone instance the other morning for him to
        play with.

        Oskar open's his browser:
        """

        portal = self.portal
        browser = self.browser
        portal_url = portal.absolute_url()

        """and logs in:
        """

        browser.addHeader(
            'Authorization', 'Basic %s:%s'
            % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        browser.open(portal_url)

        """He is very happy of what he sees. He creates a new event for this
        afternoon: "Kids Toy Party with Big Wins" and announces it in his
        newsletter.

        The next day he's very angry. No one showed up at the scheduled time.
        A few parents showed up 2 hours late with their kids. What could have
        gone wrong? He turns to his developers and tells them to fix this
        problem. They tell him, that he simply needs to set a default timezone
        in the Plone site setup to avoid making those mistakes again.

        Default Timezone
        ----------------

        Oskar opens the site setup:
        """

        browser.getLink('admin').click()
        browser.getLink('Site Setup').click()
        browser.getLink('Event Settings').click()

        """Oskar can clearly see the current default settings:
        """

        self.assertTrue(
            browser.getControl('Portal default timezone').displayValue
            ==
            ['UTC']
        )

        """He think's that is not the appropriate timezone the portal has
        chosen here. This is absurd. What does UTC stand for anyway? Clearly,
        timezones are for chumps and every region on the world should use:
        """

        tz = 'Atlantic/Bermuda'
        browser.getControl('Portal default timezone').displayValue = [tz]
        browser.getControl('Save').click()

        """Every event he now creates will be set to the 'Atlantic/Bermuda'
        timezone:
        """

        browser.getLink('Event Settings').click()
        # Compare with isoformat, since this is what the string representation
        # of an datetime object returns.
        # display_offset is -03:00 or -04:00, depending on STD or DST
        display_offset = datetime.now(pytz.timezone(tz)).isoformat()[-6:]
        self.assertTrue(display_offset in browser.contents)

    def test_first_weekday(self):
        # Make sure the first weekday was set when the profile was run.
        first_weekday = self.portal.portal_registry['plone.app.event.first_weekday']
        self.assertEqual(first_weekday, 6)

        # Change the site language. Re-running the import step should not change the setting.
        portal = self.portal
        old_language = portal.language
        portal.language = 'de'
        from plone.app.event.setuphandlers import first_weekday_setup
        first_weekday_setup(portal)
        first_weekday = self.portal.portal_registry['plone.app.event.first_weekday']
        self.assertEqual(first_weekday, 6)

        # But if we remove the setting, re-running the step should set it based on the language.
        self.portal.portal_registry['plone.app.event.first_weekday'] = None
        first_weekday_setup(portal)
        first_weekday = self.portal.portal_registry['plone.app.event.first_weekday']
        self.assertEqual(first_weekday, 0)

        # Restore the site language.
        portal.language = old_language
