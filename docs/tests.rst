Running tests
=============

If you have run the buildout (dev.cfg, test-42.cfg or test-43.cfg), you can run
all tests like so::

    ./bin/test -s plone.app.event

The `-t` switch allows you to run a specific test file or method. The
`--list-tests` lists all available tests.

To run the robot tests do::

    ./bin/test --all -s plone.app.event -t robot


For development, it might be more convenient to start a test server and run
robot tests individually, like so::

    ./bin/robot-server plone.app.event.testing.PAEventDX_ROBOT_TESTING
    ./bin/robot plone/app/event/tests/robot/test_event_add_form.robot 

In the robot test you can place the `debug` statement to access a robot shell
to try things out.

For more information on this topic visit:
http://developer.plone.org/reference_manuals/external/plone.app.robotframework/happy.html

