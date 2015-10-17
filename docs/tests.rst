Running tests
=============

After running buildout with the dev.cfg or tests.cfg config files, you can run all tests (including robot tests with ``--all`` switch) like so::

    ./bin/test -s plone.app.event --all

The `-t` switch allows you to run a specific test file or method. The `--list-tests` lists all available tests.

To run the robot tests do::

    ./bin/test --all -s plone.app.event -t robot


For development, it might be more convenient to start a test server and run robot tests individually, like so::

    ./bin/robot-server plone.app.event.testing.PAEventDX_ROBOT_TESTING
    ./bin/robot plone/app/event/tests/robot/test_event_roundtrip.robot

In the robot test you can place the `debug` statement to access a robot shell to try things out.

For more information on this topic visit: http://docs.plone.org/external/plone.app.robotframework/docs/source/index.html
