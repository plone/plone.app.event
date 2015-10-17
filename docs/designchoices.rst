Development design choices
==========================

- Timezone support. Every event has a timezone.

- Usage of pytz. The timezone library used it pytz. Other timezone identifiers than defined in pytz (Olson database) are not supported.

- Dropped support for ambiguous timezones. Three letter timezones like CET, MET, PST, etc. are not supported.

- Start/end datetime inputs are treated as localized values. If a timezone on an event is changed afterwards, the datetime values are not converted to the target timezone.

- Whole day events last from ``0:00`` until ``23:59:59`` on the same day.

- Open end events end on the same day at ``23:59:59``.

- For recurring events, we do not support unlimited occurrences. The number of possible recurrences of an event is limited to 1000 occurrences. This way, indexing and other operations doesn't take too long.  The maximum number of occurrences is set via the ``MAXCOUNT`` constant in ``plone.event.recurrence``.

- We save the timezone of the event now (since 2.0) on ``start`` and ``end`` in datetime as tzinfo expecting implicitly a valid ``pytz``. That way we ensure to not loose the original timezone. It does not matter if its stored in UTC or not, because a timezone is just that: a timezone. UTC is also just a timezone.  Not converting here to UTC makes thing less complex and gives maximum flexibility. Calculation can be done easily from one timezone to an other timezone if needed at display time. Also we now may have different timezones on start and end. Even if this a rare use-case now we can support movement between timezone, i.e a flight or train ride. Not supported are naive datetimes, since we can not calculate anything with them nor does ``DateRecurringIndex`` or ``dateutil.rrule`` supports them. Thus the use-case of a world plone day happens on a date all over the world the whole day in every timezone is not supported. This is not a limitation of not supporting naive datetimes, moreover we need a special timezone i.e ``wholeworld`` and an index and calculation methods that can deal with it. This makes things way more complex and so we decided to skip that feature for now.

- We identified two major use-cases: 1) The event happens at a physical location, i.e. a project meeting happens in Madrid with participant traveling to Madrid weekly on monday at 9:00am.  2) A phone conference of an international organisation with participants from all over the world happens every work day at 10:00 am.

  In both cases we create the event with the date with a given timezone. So for use-case (1) the editor sits in Taipeh but edits a conference in Madrid, so she has to set the timezone of the event in the form. At display time usally the viewer is interested to see the local time of the conference in the output, so display should be in Europe/Madrid timezone.

  In use-case (2) the editor usally refers to his own local timezone. He will keep the preset in the form. At display time the viewer is interested to see the date and time in his local timezone. On change of daylight-saving time in the original timezone the datetime was entered stays on 10:00am.  But if the participant in a other timezone has not this change it means he has the call scheduled one hour earlier or later in summer or winter time. So DST makes things again difficult, but heres no way to get rid of it as long as theres the concept of daylightsaving time is handled differently all over the world.
