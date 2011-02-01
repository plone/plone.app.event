function wholeDayHandler(e) {
    if (e.target.checked) {
        jQuery('.datetimewidget-time').fadeOut();
    } else {
        jQuery('.datetimewidget-time').fadeIn();
    }
}

function updateEndDate() {
    var start_date = jQuery('#startDate').data('dateinput').getValue();
//    var start_date = getDateTime('#archetypes-fieldname-startDate');
    var new_end_date = new Date();
    new_end_date.setDate(start_date.getDate() + end_start_delta);
    jQuery('#endDate').data('dateinput').setValue(new_end_date);
//    var end = jQuery('#archetypes-fieldname-endDate');
//    jQuery(end).find(".hour").val(new_end_date.getHours());
//    jQuery(end).find(".min").val(new_end_date.getMinutes());
}

function getDateTime(datetimewidget_id) {
    var datetimewidget = jQuery(datetimewidget_id);
    var fields = ['year', 'month', 'day', 'hour', 'min'];
    var parts = {};
    jQuery.each(fields, function(){
        parts[this] = parseInt(jQuery(datetimewidget).find("."+this).val());
    });
    var date = new Date(parts.year, parts.month - 1, parts.day,
                        parts.hour, parts.min);
    return date;
}

function validateEndDate() {
    var start_datetime = getDateTime('#archetypes-fieldname-startDate');
    var end_datetime = getDateTime('#archetypes-fieldname-endDate');

    if(end_datetime < start_datetime) {
        jQuery('#archetypes-fieldname-endDate').addClass("error");
    } else {
        jQuery('#archetypes-fieldname-endDate').removeClass("error");
    }
}

function initDelta(e) {
    var start_datetime = getDateTime('#archetypes-fieldname-startDate');
    var end_datetime = getDateTime('#archetypes-fieldname-endDate');
    // delta in days
    end_start_delta = (end_datetime - start_datetime) / 1000 / (3600 * 24);
}

var end_start_delta;

jQuery(document).ready(function() {

    jQuery('#wholeDay').bind('change', wholeDayHandler);
    jQuery('[id^=startDate]').bind('focus', initDelta);
    jQuery('[id^=endDate]').bind('focus', initDelta);
    jQuery('#startDate').data('dateinput').onShow(initDelta);
    jQuery('#endDate').data('dateinput').onShow(initDelta);
    jQuery('[id^=startDate]').change(updateEndDate);
    jQuery('[id^=endDate]').change(validateEndDate);

});
