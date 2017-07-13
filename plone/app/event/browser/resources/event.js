/* jslint browser: true */
/* globals require */

(function($) {

    'use strict';

    var start_end_delta = 1 / 24;  // Delta in days

    function getDateTime(datetimewidget) {
        var date, time, datetime, set_time;
        date = $('input[name="_submit"]:first', datetimewidget).prop('value');
        if (! date) {
          return;
        }
        date = date.split("-");
        time = $('input[name="_submit"]:last', datetimewidget).prop('value');
        if (! time) {
          // can happen with optional start/end dates without default values.
          set_time = true;
          time = '00:00';
        }
        time = time.split(":");

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
          $('.pattern-pickadate-time', datetimewidget).pickatime('picker').set('select', datetime);
        }
        return datetime;
    }

    function initStartEndDelta(start_container, end_container) {
        var start_datetime = getDateTime(start_container);
        var end_datetime = getDateTime(end_container);

        if (! start_datetime || ! end_datetime) {
          return;
        }

        // delta in days
        start_end_delta = (end_datetime - start_datetime) / 1000 / 60;
    }

    function updateEndDate(start_container, end_container) {
        var start_date = getDateTime(start_container);
        if (! start_date) {
          return;
        }

        var new_end_date = new Date(start_date);
        new_end_date.setMinutes(start_date.getMinutes() + start_end_delta);

        $('.pattern-pickadate-date', end_container).pickadate('picker').set('select', new_end_date);
        $('.pattern-pickadate-time', end_container).pickatime('picker').set('select', new_end_date);
    }

    function validateEndDate(start_container, end_container) {
        var start_datetime = getDateTime(start_container);
        var end_datetime = getDateTime(end_container);
        if (! start_datetime || ! end_datetime) {
          return;
        }

        if (end_datetime < start_datetime) {
            start_container.addClass("error");
        } else {
            end_container.removeClass("error");
        }
    }

    function show_hide_widget(widget, hide, fade) {
        var $widget = $(widget);
        if (hide === true) {
            if (fade === true) { $widget.fadeOut(); }
            else { $widget.hide(); }
        } else {
            if (fade === true) { $widget.fadeIn(); }
            else { $widget.show(); }
        }
    }


    function event_listing_calendar_init(cal) {
        // Dateinput selector for event_listing view
        if ($().dateinput && cal.length > 0) {
            var get_req_param, val;
            get_req_param = function (name) {
                // http://stackoverflow.com/questions/831030/how-to-get-get-request-parameters-in-javascript
                if (name === (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(window.location.search)) {
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
            cal.dateinput({
                selectors: true,
                trigger: true,
                format: 'yyyy-mm-dd',
                yearRange: [-10, 10],
                firstDay: 1,
                value: val,
                change: function () {
                    var value = this.getValue("yyyy-mm-dd");
                    window.location.href = 'event_listing?mode=day&date=' + value;
                }
            }).unbind('change').bind('onShow', function () {
                var trigger_offset = $(this).next().offset();
                $(this).data('dateinput').getCalendar().offset({
                    top: trigger_offset.top + 20,
                    left: trigger_offset.left
                });
            });
        }
    }

    function initilize_event(
        $start_input,
        $start_container,
        $pickadate_starttime,
        $end_input,
        $end_container,
        $pickadate_endtime,
        $whole_day_input,
        $open_end_input
    ) {

        if (!$pickadate_starttime.length || !$pickadate_endtime.length || !$whole_day_input.length) {
            debugger;
        }

        // WHOLE DAY INIT
        if ($whole_day_input.length > 0) {
            $whole_day_input.bind('change', function (e) {
              show_hide_widget($pickadate_starttime, e.target.checked, true);
              show_hide_widget($pickadate_endtime, e.target.checked, true);
            });
            show_hide_widget($pickadate_starttime, $whole_day_input.get(0).checked, false);
            show_hide_widget($pickadate_endtime, $whole_day_input.get(0).checked, false);
        }

        // OPEN END INIT
        if ($open_end_input.length > 0) {
            $open_end_input.bind('change', function (e) {
              show_hide_widget($end_container, e.target.checked, true);
            });
            show_hide_widget($end_container, $open_end_input.get(0).checked, false);
        }

        // START/END SETTING/VALIDATION
        $start_container.each(function () {
            $(this).on('focus', '.picker__input', function () { initStartEndDelta($start_container, $end_container); });
            $(this).on('change', '.picker__input', function () { updateEndDate($start_container, $end_container); });
        });
        $end_container.each(function () {
            $(this).on('focus', '.picker__input', function () { initStartEndDelta($start_container, $end_container); });
            $(this).on('change', '.picker__input', function () { validateEndDate($start_container, $end_container); });
        });

        // EVENT LISTING CALENDAR POPUP
        event_listing_calendar_init($("#event_listing_calendar"));

    }


    function get_dom_element(sel) {
        /* Try to get the DOM element from a selector and return it or return undefined.
         * */
        var $el = $(sel);
        return $el.length ? $el : undefined;
    }

   
    $(document).ready(function() {
        // Initialize necessary DOM elements and wait until all are foumd.
        var $start_input,
            $start_container,
            $pickadate_starttime,
            $end_input,
            $end_container,
            $pickadate_endtime,
            $whole_day_input,
            $open_end_input;

        var interval = setInterval(function(){
            $start_input     = !$start_input && get_dom_element('form input.event_start');
            $start_container = !$start_container && $start_input && $start_input.closest('div');
            $pickadate_starttime = !$pickadate_starttime && $start_container && get_dom_element('.pattern-pickadate-time-wrapper', $start_container);

            $end_input       = !$end_input && get_dom_element('form input.event_end');
            $end_container   = !$end_container && $end_input && $end_input.closest('div');
            $pickadate_endtime = !$pickadate_endtime && $end_container && $('.pattern-pickadate-time-wrapper', $end_container);

            $whole_day_input = !$whole_day_input && get_dom_element('form input.event_whole_day');
            $open_end_input  = !$open_end_input && get_dom_element('form input.event_open_end');

            if (
                $start_input &&
                $start_container &&
                $pickadate_starttime &&
                $end_input &&
                $end_container &&
                $pickadate_endtime &&
                $whole_day_input &&
                $open_end_input
            ) {
                clearInterval(interval);
                initilize_event(
                    $start_input,
                    $start_container,
                    $pickadate_starttime,
                    $end_input,
                    $end_container,
                    $pickadate_endtime,
                    $whole_day_input,
                    $open_end_input
                );
            }

        }, 100);
    }); 

}(jQuery));
