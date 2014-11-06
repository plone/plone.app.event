if (typeof(plone) === 'undefined') {
    // Make sure, plone global exists
    var plone = {};
}

(function ($, plone) {

    plone.paevent = plone.paevent || {};
    plone.paevent.end_start_delta = 1;  // Delta in hours
    plone.paevent.start_date = function() {
        return a_or_b($('#formfield-form-widgets-IEventBasic-start'), $('#archetypes-fieldname-startDate'));
    };
    plone.paevent.end_date = function() {
        return a_or_b($('#formfield-form-widgets-IEventBasic-end'), $('#archetypes-fieldname-endDate'));
    };

    function initDelta(e) {
        var start_datetime = getDateTime(plone.paevent.start_date());
        var end_datetime = getDateTime(plone.paevent.end_date());
        // delta in hours
        plone.paevent.end_start_delta = (end_datetime - start_datetime) / 1000 / 3600;
        if(plone.paevent.end_start_delta < 1) {
            // prevent saving false deltas
            plone.paevent.end_start_delta = 1;
        }
    }

    function getDateTime(datetimewidget) {
        var fields = ['year', 'month', 'day', 'hour', 'minute'];
        var parts = {};
        $.each(fields, function (idx, fld) {
            parts[fld] = parseInt($("[name$='-" + fld + "']", datetimewidget).val(), 10);
        });
        var date = new Date(parts.year, parts.month - 1, parts.day,
                            parts.hour, parts.minute);
        return date;
    }

    function setDateTime(datetimewidget, new_date) {
        $("[name$='-year']", datetimewidget).val(new_date.getYear());
        $("[name$='-month']", datetimewidget).val(new_date.getMonth());
        $("[name$='-day']", datetimewidget).val(new_date.getDate());
        $("[name$='-hour']", datetimewidget).val(new_date.getHours());
        $("[name$='-minute']", datetimewidget).val(new_date.getMinutes());
    }

    function updateEndDate() {
        // using getDateTime doesn't work for start_date here, since the values
        // are not changed yet, despite docs saying the 'change' event is
        // defered until the element loses focus.
        // TODO: revisit this. Related issue: #105, #130
        var start_date = getDateTime(plone.paevent.start_date());
        var new_end_date = start_date;
        new_end_date.setHours(new_end_date.getHours() + plone.paevent.end_start_delta);
        setDateTime(plone.paevent.end_date(), new_end_date);
        $("input[name$='-calendar']", plone.paevent.end_date()).data('dateinput').setValue(new_end_date);
    }

    function validateEndDate() {
        var start_datetime = getDateTime(plone.paevent.start_date());
        var end_datetime = getDateTime(plone.paevent.end_date());

        if (end_datetime < start_datetime) {
            plone.paevent.end_date().addClass("error");
        } else {
            plone.paevent.end_date().removeClass("error");
        }
    }


    function show_hide_widget(widget, hide, fade) {
        if (hide === true) {
            if (fade === true) { widget.fadeOut(); }
            else { widget.hide(); }
        } else {
            if (fade === true) { widget.fadeIn(); }
            else { widget.show(); }
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


    $(function () {

        // EDIT FORM

        // WHOLE DAY INIT
        var jq_whole_day = a_or_b($('#formfield-form-widgets-IEventBasic-whole_day input'), $('form[name="edit_form"] input#wholeDay'));
        var jq_datetime = a_or_b($('#form-widgets-IEventBasic-start-timecomponents, #form-widgets-IEventBasic-end-timecomponents'),
                                 $('#archetypes-fieldname-startDate .datetimewidget-time, #archetypes-fieldname-endDate .datetimewidget-time'));
        if (jq_whole_day.length > 0) {
            jq_whole_day.bind('change', function (e) { show_hide_widget(jq_datetime, e.target.checked, true); });
            show_hide_widget(jq_datetime, jq_whole_day.get(0).checked, false);
        }

        // OPEN END INIT
        var jq_open_end = a_or_b($('#formfield-form-widgets-IEventBasic-open_end input'), $('form[name="edit_form"] input#openEnd'));
        var jq_end = plone.paevent.end_date();
        if (jq_open_end.length > 0) {
            jq_open_end.bind('change', function (e) { show_hide_widget(jq_end, e.target.checked, true); });
            show_hide_widget(jq_end, jq_open_end.get(0).checked, false);
        }

        // START/END SETTING/VALIDATION
        var jq_start = plone.paevent.start_date();
        $("select", jq_start).on("change", updateEndDate);
        $("input[name$='-calendar']", jq_start).on("onHide", updateEndDate);
        $("select", jq_end).on("change", function () {
            initDelta();
            validateEndDate();
        });
        $("input[name$='-calendar']", jq_end).on("onHide", function() {
            initDelta();
            validateEndDate();
        });

        // EVENT LISTING CALENDAR POPUP
        event_listing_calendar_init($("#event_listing_calendar"));

    });
}(jQuery, plone));
