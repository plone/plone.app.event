NOTES from ploneconf2010 open space
===================================

focus on finishing
------------------
* widget (datepicker & recurrencewidget)
* calendar & events portlets
* export ical (maybe also vcal. thet is suggesting to drop support for vcal since it's an really old standard)
* whole day events
* more daterecurringindex tests

* migration work can be done after plip

more
----

* rss support

* calendar views
    monthly view, weekly view, daily view

* hcal microformat

IDEA:
    when deleting an occurence of an recurring event from calendar view,
    deleting should be faked by adding an exclusion date
    google calendar does that thing


timezone issues
---------------
    don't use timezone information at all?
        NO. better not.
    save and display dates in users local timezone
         timezone from request, set by user's browser
    confusing usecase:
        german guy editing events in bristol.
        adapting timezone when editing and displaying
    google calendar: asks if event should be displayed in users local timezone
    or timezone of event location
    when using timezones, tz information must be updated regulary and often
    (several times in the year). admins won't be very happy beeing in such a
    situation.

discussion
----------

* archetype datetime
    see c.z3cform.datetimewidget

* archetype recurrence event widget
    see z3cform recurrence event widget

* subclassing ATEvent possible? yes, should be.

hcal microformat
ical/vcal, drop vcal?
