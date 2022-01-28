/* jslint browser: true */
/* globals require */

(function($) {

  var eventedit = {

    start_end_delta: 1 / 24, // Delta in days

    // DOM ELEMENTS
    $start_input: undefined,
    $start_container: undefined,
    $pickadate_starttime: undefined,
    $end_input: undefined,
    $end_container: undefined,
    $pickadate_endtime: undefined,
    $whole_day_input: undefined,
    $open_end_input: undefined,

    get_dom_element: function (sel, $container) {
      /* Try to get the DOM element from a selector and return it or return undefined.
       * */
      var $el;
      if ($container) {
        $el = $(sel, $container);
      } else {
        $el = $(sel);
      }
      return $el.length ? $el : undefined;
    },

    getDateTime: function (datetimewidget) {
      var date, time, datetime, set_time;
      date = $('input[name="_submit"]:first', datetimewidget).prop('value');
      if (!date) {
        return;
      }
      date = date.split('-');
      time = $('input[name="_submit"]:last', datetimewidget).prop('value');
      if (!time) {
        // can happen with optional start/end dates without default values.
        set_time = true;
        time = '00:00';
      }
      time = time.split(':');

      // We can't just parse the ``date + 'T' + time`` string, because of
      // Chromium bug: https://code.google.com/p/chromium/issues/detail?id=145198
      // When passing date and time components, the passed date/time is
      // interpreted as local time and not UTC.
      datetime = new Date(
        parseInt(date[0], 10),
        parseInt(date[1], 10) - 1, // you know, javascript's month index starts with 0
        parseInt(date[2], 10),
        parseInt(time[0], 10),
        parseInt(time[1], 10)
      );
      if (set_time) {
        // we have a date but no time?! set it.
        $('.pattern-pickadate-time', datetimewidget)
          .pickatime('picker')
          .set('select', datetime);
      }
      return datetime;
    },

    initStartEndDelta: function (start_container, end_container) {
      var start_datetime = this.getDateTime(start_container);
      var end_datetime = this.getDateTime(end_container);

      if (!start_datetime || !end_datetime) {
        return;
      }

      // delta in days
      this.start_end_delta = (end_datetime - start_datetime) / 1000 / 60;
    },

    updateEndDate: function (start_container, end_container) {
      var start_date = this.getDateTime(start_container);
      if (!start_date) {
        return;
      }

      var new_end_date = new Date(start_date);
      new_end_date.setMinutes(start_date.getMinutes() + this.start_end_delta);

      $('.pattern-pickadate-date', end_container)
        .pickadate('picker')
        .set('select', new_end_date);
      $('.pattern-pickadate-time', end_container)
        .pickatime('picker')
        .set('select', new_end_date);
    },

    validateEndDate: function (start_container, end_container) {
      var start_datetime = this.getDateTime(start_container);
      var end_datetime = this.getDateTime(end_container);
      if (!start_datetime || !end_datetime) {
        return;
      }

      if (end_datetime < start_datetime) {
        start_container.addClass('error');
      } else {
        end_container.removeClass('error');
      }
    },

    show_hide_widget: function (widget, hide, fade) {
      var $widget = $(widget);
      if (hide === true) {
        if (fade === true) {
          $widget.fadeOut();
        } else {
          $widget.hide();
        }
      } else {
        if (fade === true) {
          $widget.fadeIn();
        } else {
          $widget.show();
        }
      }
    },

    event_listing_calendar_init: function (cal) {
      // Dateinput selector for event_listing view
      if ($().dateinput && cal.length > 0) {
        var get_req_param, val;
        get_req_param = function(name) {
          // http://stackoverflow.com/questions/831030/how-to-get-get-request-parameters-in-javascript
          if (
            name ===
            new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)').exec(
              window.location.search
            )
          ) {
            return decodeURIComponent(name[1]);
          }
        };
        // Preselect current date, if exists
        val = get_req_param('date');
        if (val === undefined) {
          val = new Date();
        } else {
          val = new Date(val);
        }
        cal
          .dateinput({
            selectors: true,
            trigger: true,
            format: 'yyyy-mm-dd',
            yearRange: [-10, 10],
            firstDay: 1,
            value: val,
            change: function() {
              var value = this.getValue('yyyy-mm-dd');
              window.location.href = 'event_listing?mode=day&date=' + value;
            }
          })
          .unbind('change')
          .bind('onShow', function() {
            var trigger_offset = $(this).next().offset();
            $(this).data('dateinput').getCalendar().offset({
              top: trigger_offset.top + 20,
              left: trigger_offset.left
            });
          });
      }
    },

    initilize_event: function () {

      var $start_container = this.$start_container,
          $end_container = this.$end_container,
          $pickadate_starttime = this.$pickadate_starttime,
          $pickadate_endtime = this.$pickadate_endtime,
          $open_end_input = this.$open_end_input,
          $whole_day_input = this.$whole_day_input;

      // WHOLE DAY INIT
      if ($whole_day_input.length > 0) {
        $whole_day_input.bind('change', function(e) {
          this.show_hide_widget($pickadate_starttime, e.target.checked, true);
          this.show_hide_widget($pickadate_endtime, e.target.checked, true);
        }.bind(this));
        this.show_hide_widget(
          $pickadate_starttime,
          $whole_day_input.get(0).checked,
          false
        );
        this.show_hide_widget(
          $pickadate_endtime,
          $whole_day_input.get(0).checked,
          false
        );
      }

      // OPEN END INIT
      if ($open_end_input.length > 0) {
        $open_end_input.bind('change', function(e) {
          this.show_hide_widget($end_container, e.target.checked, true);
        }.bind(this));
        this.show_hide_widget($end_container, $open_end_input.get(0).checked, false);
      }

      // START/END SETTING/VALIDATION
      $start_container.on('focus', '.picker__input', function() {
        this.initStartEndDelta($start_container, $end_container);
      }.bind(this));
      $start_container.on('change', '.picker__input', function() {
        this.updateEndDate($start_container, $end_container);
      }.bind(this));
      
      $end_container.on('focus', '.picker__input', function() {
        this.initStartEndDelta($start_container, $end_container);
      }.bind(this));
      $end_container.on('change', '.picker__input', function() {
        this.validateEndDate($start_container, $end_container);
      }.bind(this));

    },
  
  };

  $(document).ready(function() {

    eventedit.$start_input = eventedit.get_dom_element('form input.event_start');
    if (!eventedit.$start_input) {
      // Not an event edit form.
      return;
    }
    eventedit.$end_input = eventedit.get_dom_element('form input.event_end');
    if (!eventedit.$end_input) {
      // Not an event edit form.
      return;
    }

    eventedit.$start_container = eventedit.$start_input.closest('div');
    eventedit.$end_container   = eventedit.$end_input.closest('div');
    eventedit.$whole_day_input = eventedit.get_dom_element('form input.event_whole_day');
    eventedit.$open_end_input  = eventedit.get_dom_element('form input.event_open_end');

    var interval = setInterval(function() {
      eventedit.$pickadate_starttime = !eventedit.$pickadate_starttime && eventedit.get_dom_element('.pattern-pickadate-time-wrapper', eventedit.$start_container);
      eventedit.$pickadate_endtime   = !eventedit.$pickadate_endtime   && eventedit.get_dom_element('.pattern-pickadate-time-wrapper', eventedit.$end_container);

      if (
        eventedit.$pickadate_starttime &&
        eventedit.$pickadate_endtime
      ) {
        clearInterval(interval);
        eventedit.initilize_event();
      }
    }, 100);

    // EVENT LISTING CALENDAR POPUP
    eventedit.event_listing_calendar_init($('#event_listing_calendar'));

  });
})(jQuery);
