var $j = jQuery.noConflict();

function wholeDayHandler(e) {
    if (e.target.checked)
        $j('.datetimewidget-time').fadeOut();
    else
        $j('.datetimewidget-time').fadeIn();
}

function updateEndDate() {
    var start = $j('#archetypes-fieldname-startDate');
    var end = $j('#archetypes-fieldname-endDate');
    var fields = ['month','day','year','hour','min'];
    jq.each(fields,function(){
        var val = jq(start).find("."+this).val();
        jq(end).find("."+this).val(val);
    });
}

function validateEndDate() {
    var start = $j('#archetypes-fieldname-startDate');
    var end = $j('#archetypes-fieldname-endDate');
    var fields = ['year','month','day','hour','min'];
    var sdate = {};
    var edate = {};
    jq.each(fields,function(){
        sdate[this] = parseInt( jq(start).find("."+this).val());
    });
    jq.each(fields,function(){
        edate[this] = parseInt(jq(end).find("."+this).val());
    });

    var startdate = new Date(sdate.year,sdate.month,sdate.day,sdate.hour,sdate.min);
    var enddate = new Date(edate.year,edate.month,edate.day,edate.hour,edate.min);

    if(enddate < startdate){
        $j('#archetypes-fieldname-endDate').addClass("error");
    }else{
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
    $j('[id^=startDate]').change(updateEndDate);
    $j('[id^=endDate]').change(validateEndDate);

})
