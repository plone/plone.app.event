from plone.app.event.testing import PAEventDX_ROBOT_TESTING
from plone.testing import layered

import robotsuite
import unittest
from plone.app.testing.interfaces import ROBOT_TEST_LEVEL


def test_suite():
    suite = unittest.TestSuite()
    suite.level = ROBOT_TEST_LEVEL
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'),
                layer=PAEventDX_ROBOT_TESTING),
    ])
    return suite
