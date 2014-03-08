from plone.app.event.testing import PAEventDX_ROBOT_TESTING
from plone.app.testing.interfaces import ROBOT_TEST_LEVEL
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.level = ROBOT_TEST_LEVEL
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'),
                layer=PAEventDX_ROBOT_TESTING),
    ])
    return suite
