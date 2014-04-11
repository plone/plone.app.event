*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***


*** Test Cases ***

Scenario: Create and view an event
    Given a site owner
      and an event add form
    When I select a date in calendar overlay
    Then it should be filled in the form
    When I click on Recurrence Add
    Then I should see the recurrence overlay
    When I select weekly repeat
    Then I should see the recurrence overlay in weeekly repeat mode
    When I fill 3 occurrences
    Then I should see 3 occurrences in the overlay
    When I click save in the overlay
    Then the overlay should be closed
     And I should see 3 occurrences in the form
    When I click save in the form
    Then I should see the event detail view
    When I open an event occurrence
    Then I should see the occurrence detail view
    When I open the event listing
    Then I should see the event listing view


*** Keywords ***

# Given

a site owner
    Enable autologin as  Manager

an event add form
    Go to  ${PLONE_URL}/++add++Event
    Wait until page contains  Add Event
    Input text  name=form.widgets.IDublinCore.title  Testevent
    Input text  id=form-widgets-IDublinCore-description  Test description
    Input text  id=form-widgets-IEventLocation-location  Test location
    Input text  id=form-widgets-IEventAttendees-attendees  Test attendee
    Input text  id=form-widgets-IEventContact-contact_name  Test name
    Input text  id=form-widgets-IEventContact-contact_email  test@email.com
    Input text  id=form-widgets-IEventContact-contact_phone  +1234567890
    Input text  id=form-widgets-IEventContact-event_url  http://test.url

# When

I select a date in calendar overlay
    Click Link  css=#formfield-form-widgets-IEventBasic-start a.caltrigger
    Select From List  css=#calroot #calmonth  1
    Select From List  css=#calroot #calyear  2014
    Click Link  css=#calroot #calweeks a[href='#10']

I click on Recurrence Add
    Click Link  css=a[name='riedit']
    Wait until page contains  Repeat

I select weekly repeat
    Select From List  css=#rirtemplate  weekly

I fill ${NUM} occurrences
    Input text  name=rirangebyoccurrencesvalue  ${NUM}
    Focus  css=.risavebutton

I click save in the overlay
    Click Button  css=.risavebutton

I click save in the form
    Click Button  name=form.buttons.save

I open an event occurrence
    Go to  ${PLONE_URL}/testevent/2014-02-17

I open the event listing
    Go to  ${PLONE_URL}/@@event_listing?mode=all


# Then

it should be filled in the form
    Then List Selection Should Be  css=#form-widgets-IEventBasic-start-day  10
     And List Selection Should Be  css=#form-widgets-IEventBasic-start-month  2
     And List Selection Should Be  css=#form-widgets-IEventBasic-start-year  2014
     And List Selection Should Be  css=#form-widgets-IEventBasic-end-day  10
     And List Selection Should Be  css=#form-widgets-IEventBasic-end-month  2
     And List Selection Should Be  css=#form-widgets-IEventBasic-end-year  2014

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

the overlay should be closed
  Then Page Should Not Contain  class=.riform

# About class matching with x-path, see:
# http://stackoverflow.com/questions/1604471/how-can-i-find-an-element-by-css-class-with-xpath

I should see ${NUM} occurrences in the overlay
    Then Xpath Should Match X Times  //div[contains(concat(' ', normalize-space(@class), ' '), ' rioccurrences ')]/div[contains(@class, 'occurrence')]  ${NUM}

I should see ${NUM} occurrences in the form
    Then Xpath Should Match X Times  //div[contains(concat(' ', normalize-space(@class), ' '), ' ridisplay ')]/div[contains(concat(' ', normalize-space(@class), ' '), ' rioccurrences ')]/div[contains(@class, 'occurrence')]  ${NUM}

I should see the event detail view
    Then Page Should Contain  Testevent
     And Page Should Contain  Test description
     And Page Should Contain  All dates
     And Page Should Contain  Test location
     And Page Should Contain  Test name
     And Page Should Contain  +1234567890
     And Page Should Contain  Test attendee
     And Page Should Contain  Visit external website
     And Page Should Contain  iCal

I should see the occurrence detail view
    Then Page Should Contain  Testevent
     And Page Should Contain  Test description
     And Page Should Contain  All dates
     And Page Should Contain  Test location
     And Page Should Contain  Test name
     And Page Should Contain  +1234567890
     And Page Should Contain  Test attendee
     And Page Should Contain  Visit external website
     And Page Should Contain  iCal

I should see the event listing view
    Then Xpath Should Match X Times  //article[@class="vevent"]  3
