
(function () {
  function zero_pad(val, len) {
    val = val.toString();
    len = len || 2;
    while (val.length < len) {
      val = "0" + val;
    }
    return val;
  }

  function datetime_local_iso(date) {
    // Return the current date/time as timezone naive ISO string.
    return (
      zero_pad(date.getFullYear()) +
      "-" +
      zero_pad(date.getMonth() + 1) +
      "-" +
      zero_pad(date.getDate()) +
      "T" +
      zero_pad(date.getHours()) +
      ":" +
      zero_pad(date.getMinutes())
    );
  }

  function is_valid_date(date) {
    // https://stackoverflow.com/a/1353711/1337474
    return date instanceof Date && !isNaN(date);
  }

  function add_hours(date, hours) {
    // https://stackoverflow.com/a/1050782/1337474
    hours = hours || 1;
    date.setTime(date.getTime() + hours * 60 * 60 * 1000);
    var iso = datetime_local_iso(date);
    return new Date(iso);
  }

  function set_date(el, datevalue) {
    var date = new Date(datevalue); // change to Date to enforce datetime isostrings.
    if (!is_valid_date(date)) {
      return;
    }
    isostring = datetime_local_iso(date);
    if (el.type === "date") {
      el.value = isostring.split("T")[0];
    } else if (el.type === "datetime-local") {
      el.value = isostring;
    }
  }

  function open_end_toggle(event_edit__open_end, event_edit__end) {
    if (event_edit__open_end.checked) {
      event_edit__end.closest(".field").style.display = "none";
    } else {
      event_edit__end.closest(".field").style.display = "block";
    }
  }

  function whole_day_toggle(
    event_edit__whole_day,
    event_edit__start,
    event_edit__end
  ) {
    start_val = event_edit__start.value;
    end_val = event_edit__end.value;
    if (event_edit__whole_day.checked) {
      event_edit__start.type = "date";
      event_edit__end.type = "date";
    } else {
      event_edit__start.type = "datetime-local";
      event_edit__end.type = "datetime-local";
    }
    set_date(event_edit__start, start_val);
    set_date(event_edit__end, end_val);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var event_edit__open_end = document.querySelector("input[name='form.widgets.IEventBasic.open_end:list']"); // prettier-ignore
    var event_edit__whole_day = document.querySelector("input[name='form.widgets.IEventBasic.whole_day:list']"); // prettier-ignore
    var event_edit__start = document.querySelector("[name='form.widgets.IEventBasic.start']"); // prettier-ignore
    var event_edit__end = document.querySelector("[name='form.widgets.IEventBasic.end']"); // prettier-ignore

    var start_val;
    var end_val;

    if (event_edit__start) {
      event_edit__start.addEventListener("change", function () {
        start_val = event_edit__start.value;
        end_val = event_edit__end.value;
        var _start = new Date(start_val);
        var _end = new Date(end_val);
        if (!is_valid_date(_end) || _end < _start) {
          _end = _start;
          _end = add_hours(_end, 1);
          set_date(event_edit__end, _end);
        }
      });
    }

    if (event_edit__open_end) {
      open_end_toggle(event_edit__open_end, event_edit__end);
      event_edit__open_end.addEventListener("input", function () {
        open_end_toggle(event_edit__open_end, event_edit__end);
      });
    }

    if (event_edit__whole_day) {
      // on load
      whole_day_toggle(
        event_edit__whole_day,
        event_edit__start,
        event_edit__end
      );
      // on change
      event_edit__whole_day.addEventListener("input", function (e) {
        whole_day_toggle(
          event_edit__whole_day,
          event_edit__start,
          event_edit__end
        );
      });
    }
  });
})();
