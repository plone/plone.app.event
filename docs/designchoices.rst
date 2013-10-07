Development design choices
==========================

- Timezone support. Every event has a timezone.

- Usage of pytz. The timezone library used it pytz. Other timezone identifiers
  than defined in pytz (Olson database) are not supported.

- Dropped support for ambiguous timezones. Three letter timezones like CET,
  MET, PST, etc. are not supported.

- Start/end datetime inputs are treated as localized values. If a timezone on
  an event is changed afterwards, the datetime values are not converted to the
  target timezone.

- Whole day events last from 0:00 until 23:59:59 on the same day.

- Open end events end on the same day at 23:59:59.

- For recurring events, we do not support unlimited occurrences. The number of
  possible recurrences of an event is limited to 1000 occurrences. This way,
  indexing and other operations doesn't take too long.  The maximum number of
  occurrences is set via the ``MAXCOUNT`` constant in
  ``plone.event.recurrence``.

