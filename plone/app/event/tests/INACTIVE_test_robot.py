from plone.app.event.testing import PAEventDX_ROBOT_TESTING
from plone.app.testing.interfaces import ROBOT_TEST_LEVEL
from plone.testing import layered

import robotsuite
import unittest


# TODO: Remove
# The robot test fails irregularily, most probably when run on end-of-day, even
# with this fix in place:
# https://github.com/plone/plone.app.event/commit/623cec04872a847e2b9f810346424a6d663c6370
# Example test failure:
# Job started: 31.08.2014 22:07:05
# http://jenkins.plone.org/job/plone-5.0-python-2.7/3136/testReport/junit/plone.app.event.tests.test_robot/RobotTestCase/Scenario_Create_and_view_an_event/  # noqa
# Scenario: plone.app.event.tests.test_robot.RobotTestCase.Scenario Create and view an event  # noqa
# Message: Value of text field 'css=#formfield-form-widgets-IEventBasic-end input.pattern-pickadate-date' should have been 'February 10, 2014' but was 'February 11, 2014'  # noqa
@unittest.skip("Skipping due to irregular failures")
def INACTIVE_test_suite():
    suite = unittest.TestSuite()
    suite.level = ROBOT_TEST_LEVEL
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'),
                layer=PAEventDX_ROBOT_TESTING),
    ])
    return suite
