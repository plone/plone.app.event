*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***

${ADMIN_ROLE}  Site Administrator

*** Test Cases ***

Scenario: Open the Add Event form
    Given a site owner
      and an event add form
    When I click on Recurrence Add
    Then I should see the recurrence overlay
    When I select weekly repeat
    Then I should see the recurrence overlay in weeekly repeat mode


*** Keywords ***

# Given

a site owner
    Enable autologin as  Manager

an event add form
    Go to  ${PLONE_URL}/++add++Event
    Wait until page contains  Add Event
    Input text  name=form.widgets.IDublinCore.title  Testevent

# When

I click on Recurrence Add
    Click Link  css=a[name='riedit']
    Wait until page contains  Repeat

I select weekly repeat
    Select From List  css=#rirtemplate, Weekly

# Then

I should see the recurrence overlay
    Then Page Should Contain  Recurrence
     And Page Should Contain  Selected dates
     And Xpath Should Match X Times  //div[contains(@class, 'occurrence') and contains(@class, 'start')]  1
     And Xpath Should Match X Times  //div[contains(@class, 'occurrence') and contains(@class, 'rrule')]  6

I should see the recurrence overlay in weeekly repeat mode
    Then Page Should Contain  Repeats every
     And Page Should Contain  Sun
     And Page Should Contain  Mon
     And Page Should Contain  Tue
     And Page Should Contain  Wed
     And Page Should Contain  Thu
     And Page Should Contain  Fri
     And Page Should Contain  Sat

