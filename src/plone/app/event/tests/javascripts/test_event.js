
$(document).ready(function () {
	
	/* TESTS */
	
	test("End date change when the start date change", function(){
            var start_date = $('#startDate').data('dateinput').getValue('yyyy-mm-dd');
            var end_date = $('#endDate').data('dateinput').getValue('yyyy-mm-dd');
            equals(start_date, end_date, "end date should be equals to start date");
            initDelta();
	    $('#startDate').data('dateinput').setValue(2011, 1, 22);
            start_date = $('#startDate').data('dateinput').getValue('yyyy-mm-dd');
            end_date = $('#endDate').data('dateinput').getValue('yyyy-mm-dd');
            equals(start_date, end_date, "end date should be equals to start date");
	});

});


