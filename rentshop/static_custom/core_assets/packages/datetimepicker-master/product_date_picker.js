function date_picker(product_id, product_class){

    $.ajax({

        type:'GET',
        url : '/product_blocked_dates/',
        data : {
            product_id: product_id
        },

        success : function(data){

            block_date_array = JSON.parse(data)


            // date pickers

            $.datetimepicker.setDateFormatter({
                parseDate: function (date, format) {
                    var d = moment(date, format);
                    return d.isValid() ? d.toDate() : false;
                },
                formatDate: function (date, format) {
                    return moment(date).format(format);
                },
            });

            if(product_class == 'Professional'){
                var date_format = 'YYYY-MM-DD hh:mm A';
                var time_picker = true;
                $('#id_booking_start_date').val(moment().add(48, 'hour').format('YYYY-MM-DD hh:mm A'));
                $('#id_booking_end_date').val(moment().add(72, 'hour').format('YYYY-MM-DD hh:mm A'));
            }else{
                var date_format = 'YYYY-MM-DD';
                var time_picker = false;
                $('#id_booking_start_date').val(moment().add(48, 'hour').format('YYYY-MM-DD'));
                $('#id_booking_end_date').val(moment().add(72, 'hour').format('YYYY-MM-DD'));
            }

            jQuery('#product_from_date').datetimepicker(
                {
                    format: date_format,
                    timepicker: time_picker,
                    formatTime:'h:mm a',
                    step: 1,
                    autoclose: false,
                    formatDate:'DD.MM.YYYY',
                    minDate: moment().startOf('hour').add(48, 'hour')._d,
                    defaultDate: moment().startOf('hour').add(48, 'hour')._d,
                    onChangeDateTime:function(dp,$input){
                        $('#id_booking_start_date').val($input.val());
                    },
                    beforeShowDay: function(date){
                        var string = jQuery.datepicker.formatDate('mm/dd/yy', date);
                        return [block_date_array.date.indexOf(string) == -1 ]
                    }
                },
            );
            jQuery('#product_to_date').datetimepicker(
                {
                    format: date_format,
                    timepicker: time_picker,
                    formatTime:'h:mm a',
                    step: 1,
                    formatDate:'DD.MM.YYYY',
                    minDate: moment().startOf('hour').add(72, 'hour')._d,
                    defaultDate: moment().startOf('hour').add(72, 'hour')._d,
                    onChangeDateTime:function(dp,$input){
                        $('#id_booking_end_date').val($input.val());
                        var startDate = $("#id_booking_start_date").val();
                        var endDate = $("#id_booking_end_date").val();
                        if(startDate>endDate){
                           $("#product_to_date").val('');
                           alert('Please select correct date');
                        }
                    },
                    beforeShowDay: function(date){
                        var string = jQuery.datepicker.formatDate('mm/dd/yy', date);
                        return [block_date_array.date.indexOf(string) == -1 ]
                    }
                }
            );
            // date pickers

        },
        failure : function(result){
        },
    });
}