from plone.app.event.ical.importer import IcalendarImportSettingsFormView
from plone.app.event.interfaces import IICalendarImportEnabled
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser

import transaction
import unittest


class TestICALImportSettings(unittest.TestCase):
    layer = PAEventDX_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

    def test_enable_ical_import(self):
        """Test that ical import can be enabled/disabled in the browser.
        Failed in Zope4: https://github.com/zopefoundation/Zope/issues/397
        """
        self.portal.invokeFactory("Folder", "f1")
        f1 = self.portal["f1"]
        self.assertFalse(IICalendarImportEnabled.providedBy(f1))

        # enable/disable with the view
        view = IcalendarImportSettingsFormView(f1, self.request)
        view.enable()
        self.assertTrue(IICalendarImportEnabled.providedBy(f1))
        view.disable()
        self.assertFalse(IICalendarImportEnabled.providedBy(f1))

        # enable/disable with traversal
        enable_method = f1.restrictedTraverse("ical_import_settings/enable")
        enable_method()
        self.assertTrue(IICalendarImportEnabled.providedBy(f1))
        disable_method = f1.restrictedTraverse("ical_import_settings/disable")
        disable_method()
        self.assertFalse(IICalendarImportEnabled.providedBy(f1))

        # enable/disable in the browser
        transaction.commit()
        f1_url = f1.absolute_url()
        self.assertFalse(IICalendarImportEnabled.providedBy(f1))
        self.browser.open(f1_url + "/ical_import_settings/enable")
        self.browser.getControl("Confirm action").click()
        self.assertTrue(IICalendarImportEnabled.providedBy(f1))
        self.browser.open(f1_url + "/ical_import_settings/disable")
        self.browser.getControl("Confirm action").click()
        self.assertFalse(IICalendarImportEnabled.providedBy(f1))

        # the form can be rendered
        self.browser.open(f1_url + "/ical_import_settings")
        self.assertIn(
            "URL to an external icalendar resource file", self.browser.contents
        )

    def test_constraint(self):
        self.portal.invokeFactory("Folder", "f1")
        f1 = self.portal["f1"]
        f1_url = f1.absolute_url()
        transaction.commit()

        # Enable ical import.
        self.browser.open(f1_url + "/ical_import_settings/enable")
        self.browser.getControl("Confirm action").click()

        # Set it to a file url.
        self.browser.open(f1_url + "/ical_import_settings")
        self.assertIn(
            "URL to an external icalendar resource file", self.browser.contents
        )
        self.browser.getControl(
            name="form.widgets.ical_url"
        ).value = "file:///tmp/test.ical"
        self.browser.getControl(name="form.buttons.save").click()
        self.assertIn("URLs with file: are not allowed.", self.browser.contents)
