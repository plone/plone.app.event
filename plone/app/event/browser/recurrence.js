// recurrence (mostly taken from archetypes.recurringdate)
jq(function() {
    function timeComponents(value) {
      var hour = value.getHours();
      var minute = value.getMinutes();
      var ampm = "AM";
      if (hour > 11) ampm = "PM";
      if (hour > 12) hour = hour - 12;
      if (hour < 10) hour = "0" + hour;
      if (minute < 10) minute = "0" + minute;
      return new Array(hour, minute, ampm);
    }

    // Functions to keep date/time synchronized
    function updateRecurrenceStartDate() {
      var start = plone.jscalendar._fields("#edit_form_startDate_0");
      jq("#recurrence_range_start").val(start.year.val()+"/"+start.month.val()+"/"+start.day.val());
    }
    function updateRecurrenceEndDate() {
      var end = plone.jscalendar._fields("#edit_form_endDate_1");
      jq("#recurrence_range_end").val(end.year.val()+"/"+end.month.val()+"/"+end.day.val());
    }

    // Enable the datepicker
    jq("#recurrence_range_start").datepicker({
        format:'Y/m/d',
        starts: 0,
        date: jq(this).val(),
        onBeforeShow: function(){
            var value = Date.parse(jq(this).val());
            if(value) jq(this).DatePickerSetDate(value, true);
        },
        onChange: function(formated, dates){
            jq("#recurrence_range_start").val(formated);
            jq("#recurrence_range_start").DatePickerHide();
            updateEventStartEndTime();
        }
    });
    jq("#recurrence_range_end").datepicker({
        format:'Y/m/d',
        starts: 0,
        date: jq(this).val(),
        onBeforeShow: function(){
            var value = Date.parse(jq(this).val());
            if(value) jq(this).DatePickerSetDate(value, true);
        },
        onChange: function(formated, dates){
            jq("#recurrence_range_end").val(formated);
            jq("#recurrence_range_end").DatePickerHide();
        }
    });

    // Update the date recurrence field when change the event date start fields
    jq("#edit_form_startDate_0_year, #edit_form_startDate_0_month, #edit_form_startDate_0_day").change(function() {
      updateRecurrenceStartDate();
    });

    // Update the start time recurrence field when change the event time start fields
    jq("#edit_form_startDate_0_hour, #edit_form_startDate_0_minute, #edit_form_startDate_0_ampm").change(function() {
      updateRecurrenceStartEndTime();
    });

    // Update the end time recurrence field when change the event time end fields
    jq("#edit_form_endDate_1_hour, #edit_form_endDate_1_minute, #edit_form_endDate_1_ampm").change(function() {
      updateRecurrenceStartEndTime();
    });

    // Toggle the recurrence box and copy event start/end date/time to the recurrence fields
    jq("#recurrence_enabled").click(function() {
      if(jq(this).attr("checked")) {
        updateRecurrenceStartDate();
        updateRecurrenceEndDate();
        jq(".recurrence_box").show();
      } else {
        jq(".recurrence_box").hide();
      }
    });

    // Show/hide the related boxes when the frequency change
    jq(".frequency_options input.frequency_daily").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").show();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_weekly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").show();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_monthly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").show();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_yearly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").show();
      }
    });

    // Display the boxes if enabled
    jq("#recurrence_enabled:checked").parent().find(".recurrence_box").show();
    jq(".frequency_options input.frequency_daily:checked").parents(".field").find(".daily_box").show();
    jq(".frequency_options input.frequency_weekly:checked").parents(".field").find(".weekly_box").show();
    jq(".frequency_options input.frequency_monthly:checked").parents(".field").find(".monthly_box").show();
    jq(".frequency_options input.frequency_yearly:checked").parents(".field").find(".yearly_box").show();

});

