(function($) {

    var end_start_delta;

    function wholeDayHandler(e) {
        if (e.target.checked) {
            $('.datetimewidget-time').fadeOut();
        } else {
            $('.datetimewidget-time').fadeIn();
        }
    }

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

    function portletCalendarTooltips() {
        $('.portletCalendar dd a[title]').tooltip({
            offset: [-10,0]
        });
    }

    $(document).ready(function() {

        // CALENDAR PORTLET
        // bind tooltips
        portletCalendarTooltips();
        // rebind tooltips after month-change  
        $('.portletWrapper').bind('DOMNodeInserted', function(event) {
            portletCalendarTooltips();
        });

        // EDIT FORM
        $('#wholeDay').bind('change', wholeDayHandler);
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
