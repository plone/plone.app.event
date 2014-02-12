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
    Given I'm logged in as a '${ADMIN_ROLE}'
     And an event add form  Testevent
    When I click on Recurrence Add
    Then Page Should Contain  Recurrence
     And Page Should Contain  Selected dates 
    When I select Repeats Weekly
    Then Page Should Contain  Repeats every 
     And Page Should Contain  Sun
     And Page Should Contain  Mon
     And Page Should Contain  Tue
     And Page Should Contain  Wed
     And Page Should Contain  Thu
     And Page Should Contain  Fri
     And Page Should Contain  Sat

*** Keywords ***

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}
    Go to  ${PLONE_URL}

an event add form
  [Arguments]  ${title}
  Go to  ${PLONE_URL}/++add++Event
  Wait until page contains  Add Event
  Input text  name=form.widgets.IDublinCore.title  ${title}

I click on Recurrence Add
  Click Link  css=a[name='riedit']
  Wait until page contains  Repeat

I select Repeats Weekly
  Select From List  css=#rirtemplate, Weekly

