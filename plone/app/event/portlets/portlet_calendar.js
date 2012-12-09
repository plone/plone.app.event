(function($) {

    function load_portlet_calendar(event, ele){
        // depends on plone_javascript_variables.js for portal_url
        event.preventDefault();
        var ele_data = ele.data(),
            pw = ele.closest('.portletWrapper');
            pw_data = pw.data();
            url = portal_url + '/@@render-portlet?portlethash=' + pw_data.portlethash + '&year=' + ele_data.year + '&month=' + ele_data.month;
        $.ajax({
          url: url,
          success: function(data) {
            pw.html(data);
            rebind_portlet_calendar();
          }
        });
    }

    function rebind_portlet_calendar() {
        // ajaxify each portletCalendar
        $('.portletCalendar a.calendarNext').click(function() {
            load_portlet_calendar(event, $(this));
        });
        $('.portletCalendar a.calendarPrevious').click(function() {
            load_portlet_calendar(event, $(this));
        });
    }

    $(document).ready(function() {
        rebind_portlet_calendar();
    });

})(jQuery);
