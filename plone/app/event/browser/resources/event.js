function is_valid_date(date) {
  // https://stackoverflow.com/a/1353711/1337474
  return date instanceof Date && !isNaN(date);
}

function tzaware_date(date) {
  tzoffset = -date.getTimezoneOffset() * 60 * 1000;
  date.setTime(date.getTime() + tzoffset);
  return date;
}

function add_hours(date, hours) {
  // https://stackoverflow.com/a/1050782/1337474
  date.setTime(date.getTime() + hours * 60 * 60 * 1000);
  return date;
}

function set_date(el, datevalue) {
  var date = new Date(datevalue); // change to Date to enforce datetime isostrings.
  if (!is_valid_date(date)) {
    return;
  }
  isostring = tzaware_date(date).toISOString();
  if (el.type === "date") {
    el.value = isostring.split("T")[0];
  } else if (el.type === "datetime-local") {
    el.value = isostring.split(".")[0];
  }
}

function open_end_toggle(event_edit__open_end, event_edit__end) {
  if (event_edit__open_end.checked) {
    $(event_edit__end.closest(".field")).hide();
  } else {
    $(event_edit__end.closest(".field")).show();
  }
}

function whole_day_toggle(event_edit__whole_day, event_edit__start, event_edit__end) {
  start_val = event_edit__start.value;
  end_val = event_edit__end.value;
  if (event_edit__whole_day.checked) {
    event_edit__start.type = "date";
    event_edit__end.type = "date";
  } else {
    event_edit__start.type = "datetime-local";
    event_edit__end.type = "datetime-local";
  }
  // set start/end values with current hours when switching back to
  // datetime-local
  if(start_val.indexOf("T") == -1) {
    start_val = `${start_val}T${(new Date()).getHours()}:00`;
    end_val = `${end_val}T${(new Date()).getHours() + 1}:00`;
  }
  set_date(event_edit__start, start_val);
  set_date(event_edit__end, end_val);
}

document.addEventListener("DOMContentLoaded", function() {

  var event_edit__open_end = document.querySelector("input[name='form.widgets.IEventBasic.open_end:list'], input[name='form.widgets.IEventBasicNonRequired.open_end:list']"); // prettier-ignore
  var event_edit__whole_day = document.querySelector("input[name='form.widgets.IEventBasic.whole_day:list'], input[name='form.widgets.IEventBasicNonRequired.whole_day:list']"); // prettier-ignore
  var event_edit__start = document.querySelector("[name='form.widgets.IEventBasic.start'], [name='form.widgets.IEventBasicNonRequired.start']"); // prettier-ignore
  var event_edit__end = document.querySelector("[name='form.widgets.IEventBasic.end'], [name='form.widgets.IEventBasicNonRequired.end']"); // prettier-ignore

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
        end_val = _end.toISOString();
        set_date(event_edit__end, end_val);
      }
    });
  }

  if (event_edit__open_end) {
    open_end_toggle(event_edit__open_end, event_edit__end);
    event_edit__open_end.addEventListener("input", function() {
      open_end_toggle(event_edit__open_end, event_edit__end);
    });
  }

  if (event_edit__whole_day) {
    // on load
    whole_day_toggle(event_edit__whole_day, event_edit__start, event_edit__end);
    // on change
    event_edit__whole_day.addEventListener("input", function(e) {
      whole_day_toggle(event_edit__whole_day, event_edit__start, event_edit__end);
    });
  }
});
