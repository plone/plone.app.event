*** Settings ***

Resource    plone/app/robotframework/browser.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords    Plone test teardown

Variables    variables.py


*** Test cases ***

Scenario: Create and view an event
    Given a site owner
      and an event add form
     When I click on Recurrence Add
     Then I should see the recurrence overlay

     When I select weekly repeat
     Then I should see the recurrence overlay in weeekly repeat mode

     When I fill 3 occurrences
     Then I should see 3 occurrences in the overlay

     When I click save in the overlay
     Then the overlay should be closed
      and I should see 3 occurrences in the form

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
    Type text    //input[@name="form.widgets.IDublinCore.title"]    Testevent
    Type text    //textarea[@id="form-widgets-IDublinCore-description"]    Test description
    Type text    //input[@id="form-widgets-IEventLocation-location"]    Test location
    Type text    //textarea[@id="form-widgets-IEventAttendees-attendees"]    Test attendee
    Type text    //input[@id="form-widgets-IEventContact-contact_name"]    Test name
    Type text    //input[@id="form-widgets-IEventContact-contact_email"]    test@email.com
    Type text    //input[@id="form-widgets-IEventContact-contact_phone"]    +1234567890
    Type text    //input[@id="form-widgets-IEventContact-event_url"]    http://test.url

  # we can't set safely the date in the test via native browser ui "date input" element
  # reason 1: different ui's, depending on language of system browser
  #         12 hours format with meridiem input (AM/PM) vs. 24 hours format
  # reason 2: shadow root (user-agent) can't access via css or xpath selectors
  #
  # temporarily solution: set value via javascript

    Evaluate JavaScript    //input[@name="form.widgets.IEventBasic.start"]
 ...    (el, arg) => {
 ...        el.setAttribute("value", arg)
 ...    }
 ...    all_elements=False
 ...    arg=${EVENT_START_ISO}

    Evaluate JavaScript    //input[@name="form.widgets.IEventBasic.start"]
 ...    (el,arg) => {
 ...        el.setAttribute("value", arg)
 ...    }
 ...    all_elements=False
 ...    arg=${EVENT_END_ISO}

# When

I click on Recurrence Add
    Click  //a[@name="riedit"]

I select weekly repeat
    Select Options By  //div[contains(@class,"modal-wrapper")]//select[@id="rirtemplate"]    value    weekly

I fill ${NUM} occurrences
    Type Text    //div[contains(@class,"modal-wrapper")]//form//input[@name="rirangebyoccurrencesvalue"]    ${NUM}
    Keyboard Key    press    Tab

I click save in the overlay
    Click    //div[contains(@class,"modal-wrapper")]//div[@class="modal-footer"]//button[contains(@class,"risavebutton")]

I click save in the form
    Click  //button[@name="form.buttons.save"]

I open an event occurrence
    ${url}=    Get Property    //*[@id="content-core"]/div/div/div/div[2]/div[1]/div/div/div[2]/p/span[2]/a    href
    Go to  ${url}

I open the event listing
    Go to  ${PLONE_URL}/@@event_listing?mode=all

# Then

I should see the recurrence overlay
    Get Text    //div[contains(@class,"modal-wrapper")]//form/div[@class="rioccurrencesactions"]/div/h6/strong    should be    Selected dates
    Get Element Count    //div[contains(@class, 'occurrence') and contains(@class, 'start')]    should be    1
    Get Element Count    //div[contains(@class, 'occurrence') and contains(@class, 'rrule')]    should be    6

I should see the recurrence overlay in weeekly repeat mode
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyinterval"]    contains    Repeat every
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Sun
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Mon
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Tue
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Wed
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Thu
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Fri
    Get Text    //div[contains(@class,"modal-wrapper")]//form//div[@id="riweeklyweekdays"]    contains    Sat

I should see ${NUM} occurrences in the overlay
    Get Element Count    //div[contains(@class,"modal-wrapper")]//div[@class="rioccurrences"]/div[contains(@class, 'occurrence')]    should be    ${NUM}

the overlay should be closed
    Get Element Count    //div[contains(@class,"modal-wrapper")]//*[contains(@class,"riform")]    should be    0

I should see ${NUM} occurrences in the form
    Get Element Count    //div[contains(@class,"ridisplay")]//div[@class="rioccurrences"]/div[contains(@class, 'occurrence')]    should be    ${NUM}

I should see the event detail view
    Get Text    //*[@id="global_statusmessage"]    contains   Item created
    Get Text    //article[@id="content"]/header    contains   Testevent
    Get Text    //article[@id="content"]/header    contains   Test description
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test location
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test name
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    +1234567890
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test attendee
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Visit external website
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    iCal

I should see the occurrence detail view
    Get Text    //article[@id="content"]/header    contains   Testevent
    Get Text    //article[@id="content"]/header    contains   Test description
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test location
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test name
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    +1234567890
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Test attendee
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    Visit external website
    Get Text    //div[@id="content-core"]//div[contains(@class,"event-summary")]    contains    iCal

I should see the event listing view
    Get Element Count    //article[contains(@class,"vevent")]    should be    3
