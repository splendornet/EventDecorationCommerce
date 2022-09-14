$('document').ready(function (){




});

var icons = {
        time: "fa fa-clock-o",
        date: "fa fa-calendar",
        up: "fa fa-arrow-up",
        down: "fa fa-arrow-down",
        previous: "fa fa-chevron-left",
        next: "fa fa-chevron-right",
        today: "fa fa-clock-o",
        clear: "fa fa-trash-o"
}

function trigger_datepicker(product_class, product_id){

    if(product_class == 'Professional'){
        var date_format = 'YYYY-MM-DD hh:mm A';
        $('#id_booking_start_date').val(moment().add(48, 'hour').format('YYYY-MM-DD hh:mm A'));
        $('#id_booking_end_date').val(moment().add(72, 'hour').format('YYYY-MM-DD hh:mm A'));
    }else{
        var date_format = 'YYYY-MM-DD';
        $('#id_booking_start_date').val(moment().add(48, 'hour').format('YYYY-MM-DD'));
        $('#id_booking_end_date').val(moment().add(72, 'hour').format('YYYY-MM-DD'));
    }

    $('#product_from_date').datetimepicker(
        {
            icons: icons,
             weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		forceParse: 0,
        showMeridian: 1
//            format: date_format,
//            minDate: moment().add(48, 'hour').format('YYYY-MM-DD hh:mm A'),
//            keepOpen: true
        }
    );
}