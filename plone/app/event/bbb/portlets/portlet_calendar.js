/*jslint browser: true*/
/*global $, jQuery, plone, portal_url */

(function ($) {

    function load_portlet_calendar(event, elem) {
        // depends on plone_javascript_variables.js for portal_url
        event.preventDefault();
        var pw, elem_data, portlethash, url;
        pw = elem.closest('.portletWrapper');
        elem_data = elem.data();
        portlethash = pw.attr('id');
        portlethash = portlethash.substring(15, portlethash.length);
        url = portal_url +
              '/@@render-portlet?portlethash=' + portlethash +
              '&year=' + elem_data.year +
              '&month=' + elem_data.month;
        $.ajax({
            url: url,
            success: function (data) {
                pw.html(data);
                rebind_portlet_calendar();
            }
        });
    }

    function rebind_portlet_calendar() {
        // ajaxify each portletCalendar
        $('.portletCalendar a.calendarNext').click(function (event) {
            load_portlet_calendar(event, $(this));
        });
        $('.portletCalendar a.calendarPrevious').click(function (event) {
            load_portlet_calendar(event, $(this));
        });
        $('.portletCalendar dd a[title]').tooltip({
            offset: [-10, 0],
            tipClass: 'pae_calendar_tooltip'
        });
    }

    $(document).ready(function () {
        rebind_portlet_calendar();
    });

}(jQuery));
