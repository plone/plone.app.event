Development design choices
==========================

- Timezone support. Every event has a timezone.

- Usage of pytz. The timezone library used it pytz. Other timezone identifiers
  than defined in pytz (Olson database) are not allowed.

- Dropped support for ambiguous timezones. Three letter timezones like CET,
  MET, PST, etc. are not allowed (partly implemented).

- Start/end datetime inputs are treated as localized values. If a timezone on
  an event is changed afterwards, the datetime values are not converted to the
  target timezone.

- Whole day events last from 0:00 until 23:59:59 on the same day.

- Events without an end date/time end on exactly the same date/time as it
  starts (not implemented and to be discussed).
