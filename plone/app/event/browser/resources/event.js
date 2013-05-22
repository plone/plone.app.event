(function($) {

    var end_start_delta;


    function updateEndDate() {
        var start_date = $('#startDate').data('dateinput').getValue();
    //    var start_date = getDateTime('#archetypes-fieldname-startDate');
        var new_end_date = new Date(start_date);
        new_end_date.setDate(start_date.getDate() + end_start_delta);
        $('#endDate').data('dateinput').setValue(new_end_date);
    //    var end = $('#archetypes-fieldname-endDate');
    //    $(end).find(".hour").val(new_end_date.getHours());
    //    $(end).find(".min").val(new_end_date.getMinutes());
    }

    function getDateTime(datetimewidget_id) {
        var datetimewidget = $(datetimewidget_id);
        var fields = ['year', 'month', 'day', 'hour', 'min'];
        var parts = {};
        $.each(fields, function(){
            parts[this] = parseInt($(datetimewidget).find("."+this).val(), 10);
        });
        var date = new Date(parts.year, parts.month - 1, parts.day,
                            parts.hour, parts.min);
        return date;
    }

    function validateEndDate() {
        var start_datetime = getDateTime('#archetypes-fieldname-startDate');
        var end_datetime = getDateTime('#archetypes-fieldname-endDate');

        if(end_datetime < start_datetime) {
            $('#archetypes-fieldname-endDate').addClass("error");
        } else {
            $('#archetypes-fieldname-endDate').removeClass("error");
        }
    }

    function initDelta(e) {
        var start_datetime = getDateTime('#archetypes-fieldname-startDate');
        var end_datetime = getDateTime('#archetypes-fieldname-endDate');
        // delta in days
        end_start_delta = (end_datetime - start_datetime) / 1000 / (3600 * 24);
    }


    function set_whole_day(target, fade) {
        var widget = $('.datetimewidget-time');
        if (target.checked===true) {
            if (fade===true) { widget.fadeOut(); }
            else { widget.hide(); }
        } else {
            if (fade===true) { widget.fadeIn(); }
            else { widget.show(); }
        }
    }

    function show_hide_widget(widget, hide, fade) {
        if (hide===true) {
            if (fade===true) { widget.fadeOut(); }
            else { widget.hide(); }
        } else {
            if (fade===true) { widget.fadeIn(); }
            else { widget.show(); }
        }
    }

    function a_or_b(a, b) {
        var ret = undefined;
        if (a.length>0) {
            ret = a;
        } else {
            ret = b;
        }
        return ret;
    }

    $(document).ready(function() {

        // EDIT FORM

        // WHOLE DAY INIT
        var jq_whole_day_1 = $('#event-base-edit input#wholeDay');
        var jq_whole_day_2 = $('#formfield-form-widgets-IEventBasic-whole_day input');
        if (jq_whole_day_1.length>0) {
            jq_whole_day_1.bind('change', function (e) { set_whole_day(e.target, true)});
            set_whole_day(jq_whole_day_1.get(0), fade=false);
        }
        if (jq_whole_day_2.length>0) {
            jq_whole_day_2.bind('change', function (e) { set_whole_day(e.target, true)});
            set_whole_day(jq_whole_day_2.get(0), fade=false);
        }


        var jq_open_end = a_or_b($('#event-base-edit input#openEnd'), $('#formfield-form-widgets-IEventBasic-open_end input'));
        var jq_end_date = a_or_b($('#archetypes-fieldname-endDate'), $('#formfield-form-widgets-IEventBasic-end'));
        if (jq_open_end.length>0) {
            jq_open_end.bind('change', function (e) { show_hide_widget(jq_end_date, e.target.checked, true)});
            show_hide_widget(jq_end_date, jq_open_end.get(0).checked, fade=false);
        }



        /*$('[id^=startDate]').bind('focus', initDelta);
        $('[id^=endDate]').bind('focus', initDelta);
        $('#startDate').each(function(){
            $(this).data('dateinput').onShow(initDelta);
        });
        $('#endDate').each(function(){
            $(this).data('dateinput').onShow(initDelta);
        });
        $('[id^=startDate]').change(updateEndDate);
        $('[id^=endDate]').change(validateEndDate);*/

    });

})(jQuery);


(function($) {

    $(document).ready(function() {

        // Dateinput selector for event_listing view
        var event_listing_calendar = $("#event_listing_calendar");
        if ($().dateinput && event_listing_calendar.length > 0) {

            get_req_param = function (name){
                // http://stackoverflow.com/questions/831030/how-to-get-get-request-parameters-in-javascript
                if(name===(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search)) {
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

            event_listing_calendar.dateinput({
                selectors: true,
                trigger: true,
                format: 'yyyy-mm-dd',
                yearRange: [-10, 10],
                firstDay: 1,
                value: val,
                change: function() {
                    var value = this.getValue("yyyy-mm-dd");
                    window.location.href = 'event_listing?mode=day&date=' + value;
                }
            }).unbind('change').bind('onShow', function (event) {
                var trigger_offset = $(this).next().offset();
                $(this).data('dateinput').getCalendar().offset({
                    top: trigger_offset.top+20,
                    left: trigger_offset.left
                });
            });
        }
    });

})(jQuery);
