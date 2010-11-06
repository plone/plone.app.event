var $j = jQuery.noConflict();

function wholeDayHandler(e) {
    if (e.target.checked)
        $j('.datetimewidget-time').fadeOut();
    else
        $j('.datetimewidget-time').fadeIn();
}

function updateEndDate(dateText, inst) {
    var start_date = $j('#startDate').datepicker('getDate');
    var new_end_date = new Date();
    new_end_date.setDate(start_date.getDate() + end_start_delta);
    $j('#endDate').datepicker('setDate', new_end_date);
}

function validateEndDate(dateText, inst) {
    var start_date = $j('#startDate').datepicker('getDate');
    var end_date = $j('#endDate').datepicker('getDate');
    end_start_delta = (end_date - start_date) / 1000 / (3600 * 24);
    if (end_date < start_date) {
        $j('#archetypes-fieldname-endDate').addClass("error");
    } else {
        $j('#archetypes-fieldname-endDate').removeClass("error");
    }
}

function initDelta(e) {
    var start_date = $j('#startDate').datepicker('getDate');
    var end_date = $j('#endDate').datepicker('getDate');
    // delta in days
    end_start_delta = (end_date - start_date) / 1000 / (3600 * 24);
}

var end_start_delta;

$j(document).ready(function() {

    $j('#wholeDay').bind('change', wholeDayHandler);
    $j('#startDate').bind('focus', initDelta);
    $j('#endDate').bind('focus', initDelta);

    $j('#startDate').datepicker({onClose: updateEndDate});
    $j('#endDate').datepicker({onClose: validateEndDate});

})
