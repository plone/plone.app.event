if (typeof(plone) === 'undefined') {
    // Make sure, plone global exists
    var plone = {};
}

(function ($, plone) {

    plone.paevent = plone.paevent || {};
    plone.paevent.end_start_delta = 1 / 24;  // Delta in days

    function initDelta(e) {
        var start_datetime = getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate')));
        var end_datetime = getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate')));
        // delta in days
        plone.paevent.end_start_delta = (end_datetime - start_datetime) / 1000 / 60;
    }

    function getDateTime(datetimewidget) {
        var date = $('input[name="_submit"]:first', datetimewidget).prop('value');
        var time = $('input[name="_submit"]:last', datetimewidget).prop('value') || '00:00';
        var datetime = new Date(date + ' ' + time);
        return datetime;
    }

    function updateEndDate() {
        var jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
        var jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));

        var start_date = getDateTime(jq_start);
        var new_end_date = new Date(start_date);
        new_end_date.setMinutes(start_date.getMinutes() + plone.paevent.end_start_delta);

        $('.pattern-pickadate-date', jq_end).pickadate('picker').set('select', new_end_date);
        $('.pattern-pickadate-time', jq_end).pickatime('picker').set('select', new_end_date);
    }

    function validateEndDate() {
        var jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
        var jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));

        var start_datetime = getDateTime(jq_start);
        var end_datetime = getDateTime(jq_end);

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

    function a_or_b(a, b) {
        var ret;
        if (a.length > 0) {
            ret = a;
        } else {
            ret = b;
        }
        return ret;
    }


    function event_listing_calendar_init(cal) {
        // Dateinput selector for event_listing view
        if ($().dateinput && cal.length > 0) {
            var get_req_param = function (name) {
                // http://stackoverflow.com/questions/831030/how-to-get-get-request-parameters-in-javascript
                if (name === (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search)) {
                    return decodeURIComponent(name[1]);
                }
            };
            // Preselect current date, if exists
            var val = get_req_param('date');
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
            }).unbind('change').bind('onShow', function (event) {
                var trigger_offset = $(this).next().offset();
                $(this).data('dateinput').getCalendar().offset({
                    top: trigger_offset.top + 20,
                    left: trigger_offset.left
                });
            });
        }
    }


    $(document).ready(function () {

        // EDIT FORM

        // WHOLE DAY INIT
        var jq_whole_day = a_or_b($('#formfield-form-widgets-IEventBasic-whole_day input'), $('form[name="edit_form"] input#wholeDay'));
        if (jq_whole_day.length > 0) {
            jq_whole_day.bind('change', function (e) { show_hide_widget('.pattern-pickadate-time-wrapper', e.target.checked, true); });
            show_hide_widget('.pattern-pickadate-time-wrapper', jq_whole_day.get(0).checked, false);
        }

        // OPEN END INIT
        var jq_open_end = a_or_b($('#formfield-form-widgets-IEventBasic-open_end input'), $('form[name="edit_form"] input#openEnd'));
        var jq_end = a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));
        if (jq_open_end.length > 0) {
            jq_open_end.bind('change', function (e) { show_hide_widget(jq_end, e.target.checked, true); });
            show_hide_widget(jq_end, jq_open_end.get(0).checked, false);
        }

        // START/END SETTING/VALIDATION
        var jq_start = a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
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

    });
}(jQuery, plone));
