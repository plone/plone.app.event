from pathlib import Path
from plone.app.event.ical.importer import IcalendarImportSettingsFormView
from plone.app.event.interfaces import IICalendarImportEnabled
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from unittest import mock

import requests
import transaction
import unittest


class MockResponse:
    def __init__(self, content):
        self.content = content

    @property
    def headers(self):
        return {"Content-Length": len(self.content)}

    def raise_for_status(self):
        if not self.content:
            raise requests.exceptions.HTTPError("404 not found")

    def iter_content(self, limit):
        yield self.content[:limit]


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
        self.browser.getControl(name="form.widgets.ical_url").value = (
            "file:///tmp/test.ical"
        )
        self.browser.getControl(name="form.buttons.save").click()
        self.assertIn("URL not accepted", self.browser.contents)

    def test_no_file_protocol_url(self):
        # The no_file_protocol_url validator initially only checked for a file
        # protocol.  We enhanced it with more checks.
        from plone.app.event.ical.importer import no_file_protocol_url as validator
        from zope.interface import Invalid

        self.assertTrue(validator("http://example.com"))
        self.assertTrue(validator("https://example.com"))

        # No file url
        with self.assertRaises(Invalid):
            validator("file:///tmp/test.ical")
        # A different spelling should not catch us off guard
        with self.assertRaises(Invalid):
            validator("File:///tmp/test.ical")
        with self.assertRaises(Invalid):
            validator("FILE:///tmp/test.ical")

        # No localhost or other single domains, as may be used in an
        # internal network
        with self.assertRaises(Invalid):
            validator("http://localhost")
        with self.assertRaises(Invalid):
            validator("http://backend")

        # No docker either
        with self.assertRaises(Invalid):
            validator("http://host.docker.internal")

        # No port numbers, to avoid misusing this as a port scanner
        with self.assertRaises(Invalid):
            validator("http://example.com:8080")

        # No ip addresses, they may too easily be internal.
        # Let's especially check some private IP addresses.
        with self.assertRaises(Invalid):
            validator("http://10.0.0.0.1")
        with self.assertRaises(Invalid):
            validator("http://172.16.0.255")
        with self.assertRaises(Invalid):
            validator("http://192.168.0.1")
        with self.assertRaises(Invalid):
            validator("http://169.254.169.254")
        # Watch out for false positives though.
        self.assertTrue(validator("http://2026.ploneconf.org"))

        # Let's try some more possibly dangerous urls.
        # Products.isurlinportal has gathered some nice ones, and we should
        # accept even less, e.g. no relative paths in the portal.
        with self.assertRaises(Invalid):
            validator("//example.com")
        with self.assertRaises(Invalid):
            validator("////example.com")
        with self.assertRaises(Invalid):
            validator("\\\\example.com")
        with self.assertRaises(Invalid):
            validator("/absolute/path")
        with self.assertRaises(Invalid):
            validator("relative/path")
        with self.assertRaises(Invalid):
            validator('<script>alert("hi");</script>')
        with self.assertRaises(Invalid):
            validator("jaVascript:alert(3)")
        with self.assertRaises(Invalid):
            validator("javascript%3Aalert(3)")
        with self.assertRaises(Invalid):
            validator(
                "data:text/html%3bbase64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K"
            )
        with self.assertRaises(Invalid):
            validator("mailto:someone@example.org")
        with self.assertRaises(Invalid):
            validator("ftp//ftp.example.com")

    def test_download_ical(self):
        from plone.app.event.ical.importer import download_ical

        with mock.patch(
            "plone.app.event.ical.importer.requests.get",
            return_value=MockResponse("I am an icalendar file."),
        ):
            self.assertEqual(download_ical("some.url"), "I am an icalendar file.")
            with self.assertRaises(ValueError):
                download_ical("some.url", limit=10)
        with mock.patch(
            "plone.app.event.ical.importer.requests.get",
            return_value=MockResponse("X" * 100001),
        ):
            with self.assertRaises(ValueError):
                download_ical("some.url")

    def test_ical_import_too_many(self):
        from plone.app.event.ical.importer import ical_import
        from plone.app.event.ical.importer import TooManyEventsToImport

        ical_path = Path(__file__).parent / "icaltest.ics"
        icsdata = ical_path.read_bytes()
        with self.assertRaises(TooManyEventsToImport):
            ical_import(self.portal, icsdata, "Event", limit=3)
