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
  Click Element  xpath=//div[@data-fieldname="form.widgets.IEventBasic.start"]//input[contains(@class,"pattern-pickadate-date")]
  Wait until page contains  Sat
# For Javascript: Month 1 = February.
  Select from list  css=div[data-fieldname="form.widgets.IEventBasic.start"] .picker__select--month  1
  Select from list  css=div[data-fieldname="form.widgets.IEventBasic.start"] select.picker__select--year  2014
  Click Element  xpath=//div[@data-fieldname="form.widgets.IEventBasic.start"]//div[contains(@class, 'picker__day')][contains(text(), "10")]
# Select Times
  Click Element  xpath=//div[@data-fieldname="form.widgets.IEventBasic.start"]//input[contains(@class,"pattern-pickadate-time")]
  Click Element  xpath=//div[@data-fieldname="form.widgets.IEventBasic.start"]//div[contains(@class, 'picker--time')]//li[contains(@class, 'picker__list-item')][contains(text(), "10:00 a.m.")]


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
  Textfield Value Should Be  css=#formfield-form-widgets-IEventBasic-start input.pattern-pickadate-date  February 10, 2014
  Textfield Value Should Be  css=#formfield-form-widgets-IEventBasic-start input.pattern-pickadate-time  10:00 a.m.
  Textfield Value Should Be  css=#formfield-form-widgets-IEventBasic-end input.pattern-pickadate-date  February 10, 2014
  Textfield Value Should Be  css=#formfield-form-widgets-IEventBasic-end input.pattern-pickadate-time  11:00 a.m.

I should see the recurrence overlay
  Page Should Contain  Recurrence
  Page Should Contain  Selected dates
  Xpath Should Match X Times  //div[contains(@class, 'occurrence') and contains(@class, 'start')]  1
  Xpath Should Match X Times  //div[contains(@class, 'occurrence') and contains(@class, 'rrule')]  6

I should see the recurrence overlay in weeekly repeat mode
  Page Should Contain  Repeats every
  Page Should Contain  Sun
  Page Should Contain  Mon
  Page Should Contain  Tue
  Page Should Contain  Wed
  Page Should Contain  Thu
  Page Should Contain  Fri
  Page Should Contain  Sat

the overlay should be closed
  Page Should Not Contain  class=.riform

# About class matching with x-path, see:
# http://stackoverflow.com/questions/1604471/how-can-i-find-an-element-by-css-class-with-xpath

I should see ${NUM} occurrences in the overlay
  Xpath Should Match X Times  //div[contains(concat(' ', normalize-space(@class), ' '), ' rioccurrences ')]/div[contains(@class, 'occurrence')]  ${NUM}

I should see ${NUM} occurrences in the form
  Xpath Should Match X Times  //div[contains(concat(' ', normalize-space(@class), ' '), ' ridisplay ')]/div[contains(concat(' ', normalize-space(@class), ' '), ' rioccurrences ')]/div[contains(@class, 'occurrence')]  ${NUM}

I should see the event detail view
  Page Should Contain  Testevent
  Page Should Contain  Test description
  Page Should Contain  All dates
  Page Should Contain  Test location
  Page Should Contain  Test name
  Page Should Contain  +1234567890
  Page Should Contain  Test attendee
  Page Should Contain  Visit external website
  Page Should Contain  iCal

I should see the occurrence detail view
  Page Should Contain  Testevent
  Page Should Contain  Test description
  Page Should Contain  All dates
  Page Should Contain  Test location
  Page Should Contain  Test name
  Page Should Contain  +1234567890
  Page Should Contain  Test attendee
  Page Should Contain  Visit external website
  Page Should Contain  iCal

I should see the event listing view
  Xpath Should Match X Times  //article[@class="vevent"]  3
