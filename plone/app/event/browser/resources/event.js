/*jslint browser: true*/
/*global $, jQuery, plone, require*/


if(require === undefined){
  require = function(reqs, torun){
    'use strict';
    return torun(window.jQuery);
  }
}


require([
    'jquery'
], function($){
    'use strict';

    var end_start_delta = 1 / 24;  // Delta in days

    function a_or_b(a, b) {
        var ret;
        if (a.length > 0) {
            ret = a;
        } else {
            ret = b;
        }
        return ret;
    }

    function getDateTime(datetimewidget) {
        var date, time, datetime;
        date = $('input[name="_submit"]:first', datetimewidget).prop('value');
        date = date.split("-");
        time = $('input[name="_submit"]:last', datetimewidget).prop('value') || '00:00';
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
        return datetime;
    }

    function initDelta() {
        var start_datetime, end_datetime;
        start_datetime = getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate')));
        end_datetime = getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate')));
        // delta in days
        end_start_delta = (end_datetime - start_datetime) / 1000 / 60;
    }

    function updateEndDate() {
        var jq_start, jq_end, start_date, new_end_date;
        jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
        jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));

        start_date = getDateTime(jq_start);
        new_end_date = new Date(start_date);
        new_end_date.setMinutes(start_date.getMinutes() + end_start_delta);

        $('.pattern-pickadate-date', jq_end).pickadate('picker').set('select', new_end_date);
        $('.pattern-pickadate-time', jq_end).pickatime('picker').set('select', new_end_date);
    }

    function validateEndDate() {
        var jq_start, jq_end, start_datetime, end_datetime;
        jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
        jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));

        start_datetime = getDateTime(jq_start);
        end_datetime = getDateTime(jq_end);

        if (end_datetime < start_datetime) {
            jq_end.addClass("error");
        } else {
            jq_end.removeClass("error");
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

    function initilize_event() {

        // EDIT FORM

        var jq_whole_day, jq_time, jq_open_end, jq_end, jq_start;

        // WHOLE DAY INIT
        jq_whole_day = a_or_b($('#formfield-form-widgets-IEventBasic-whole_day input'), $('form[name="edit_form"] input#wholeDay'));
        jq_time = a_or_b($('#formfield-form-widgets-IEventBasic-start .pattern-pickadate-time-wrapper, #formfield-form-widgets-IEventBasic-end .pattern-pickadate-time-wrapper'),
                         $('#archetypes-fieldname-startDate .pattern-pickadate-time-wrapper, #archetypes-fieldname-endDate .pattern-pickadate-time-wrapper'));
        if (jq_whole_day.length > 0) {
            jq_whole_day.bind('change', function (e) { show_hide_widget(jq_time, e.target.checked, true); });
            show_hide_widget(jq_time, jq_whole_day.get(0).checked, false);
        }

        // OPEN END INIT
        jq_open_end = a_or_b($('#formfield-form-widgets-IEventBasic-open_end input'), $('form[name="edit_form"] input#openEnd'));
        jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));
        if (jq_open_end.length > 0) {
            jq_open_end.bind('change', function (e) { show_hide_widget(jq_end, e.target.checked, true); });
            show_hide_widget(jq_end, jq_open_end.get(0).checked, false);
        }

        // START/END SETTING/VALIDATION
        jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
        jq_start.each(function () {
            $(this).on('focus', '.picker__input', initDelta);
            $(this).on('change', '.picker__input', updateEndDate);
        });
        jq_end.each(function () {
            $(this).on('focus', '.picker__input', initDelta);
            $(this).on('change', '.picker__input', validateEndDate);
        });

        // EVENT LISTING CALENDAR POPUP
        event_listing_calendar_init($("#event_listing_calendar"));

    };

    // mockup-core should trigger event once it initiallized all patterns (in
    // mockup-core) but it only sets body class once all patterns were
    // initialized
    var interval = setInterval(function(){
      if ($(document.body).hasClass('patterns-loaded')) {
        clearInterval(interval);
        initilize_event();
      }
    }, 100);
 
});
