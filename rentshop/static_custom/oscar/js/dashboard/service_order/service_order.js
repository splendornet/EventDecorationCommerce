// method to export service order
function export_service(url, name){

    var checked_id = [];
    $.each($("input[class='checked_service']:checked"), function(){
        checked_id.push($(this).val());
    });
    var _url = url+'?&name='+name+'&checked_id='+checked_id;
    document.location.href = _url;
}

$('#master_service_checkbox').change(function (){

    $('.checked_service:checkbox').not(this).prop('checked', this.checked);

    var service_ids = $('.checked_service:checked').map(function(){
        return $(this).val();
    });

    if (service_ids.length == 0){
        $('#service_mark').html('')
    }else{
        $('#service_mark').html('Total '+service_ids.length+ ' service order selected.')
    }

});

$('.checked_service').change(function (){

    $('#master_service_checkbox').prop('checked', false);

    var service_ids = $('.checked_service:checked').map(function(){
        return $(this).val();
    });

    if (service_ids.length == 0){
        $('#service_mark').html('')
    }else{
        $('#service_mark').html('Total '+service_ids.length+ ' service order selected.')
    }

});

