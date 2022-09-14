/* ***********************************************
    Product date-range picker
*********************************************** */

function datepicker(product_id, product_class, product_booking_day){

    $.ajax({

        type:'GET',
        url : '/product_blocked_dates/',
        data : {
            product_id: product_id,
        },

        success : function(data){

            var x = JSON.parse(data)
            var diff_unit = parseInt(product_booking_day)
            if(x.status)
            {
                diff_unit = x.diff
            }

            console.log("diff"+diff_unit)
            if(product_class == 'Professional'){
                var is_time = true;
                var dt_format = 'YYYY-MM-DD hh:mm A';
                $('#id_booking_start_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD hh:mm A'));
                $('#id_booking_end_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD hh:mm A'));
            }
            else if(product_class == 'Service'){
                var is_time = true;
                var dt_format = 'YYYY-MM-DD hh:mm A';
                diff_unit = 720
                $('#id_booking_start_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD hh:mm A'));
                $('#id_booking_end_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD hh:mm A'));
            }
            else{
                var is_time = false;
                var dt_format = 'YYYY-MM-DD';
                $('#id_booking_start_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD'));
                $('#id_booking_end_date').val(moment().add(diff_unit, 'hour').format('YYYY-MM-DD'));
            }

            var disabledArr = x.date;
            startdate = moment().startOf('minutes').add(diff_unit, 'hour');
            enddate = moment().startOf('minutes').add(diff_unit, 'hour');
            $('input[name="daterange"]').daterangepicker(
                {
                    opens: 'right',
                    timePicker: is_time,
                    startDate : startdate,
                    endDate : enddate,
                    autoApply: true,
                    minDate: moment().startOf('hour').add(diff_unit, 'hour'),

                    isInvalidDate: function(arg){

                        // Prepare the date comparision
                        var thisMonth = arg._d.getMonth()+1;   // Months are 0 based
                        if (thisMonth<10){
                            thisMonth = "0"+thisMonth; // Leading 0
                        }
                        var thisDate = arg._d.getDate();
                        if (thisDate<10){
                            thisDate = "0"+thisDate; // Leading 0
                        }

                        var thisYear = arg._d.getYear()+1900;   // Years are 1900 based
                        var thisCompare = thisMonth +"/"+ thisDate +"/"+ thisYear;

                        if($.inArray(thisCompare,disabledArr)!=-1){
                            return true;
                        }
                    },

                },
                function(start, end, label) {

                    start_date = start.format(dt_format)
                    end_date = end.format(dt_format)
                    $('#id_booking_start_date').val(start_date);
                    $('#id_booking_end_date').val(end_date);
                },
            );

            //from_input = jQuery('<div class="form-group form-group-dp"> <label for="from_date_display" class="label_dp">From</label> <input type="text" class="form-control form-control-dp" id="from_date_display"> </div>');
            //to_input = jQuery('<div class="form-group form-group-dp"> <label for="to_date_display" class="label_dp">To</label> <input type="text" class="form-control form-control-dp" id="to_date_display"> </div>');
            //jQuery('.drp-buttons').append(from_input);
            //jQuery('.drp-buttons').append(to_input);
        },
        failure : function(result){},
    });
}