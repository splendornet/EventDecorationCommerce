// Dashboard partner

function export_vendor_url(url, search_type, all_search, pincode, status){

    var checked_id = [];
    $.each($("input[class='vendor_checkbox']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?search_type='+search_type+'&all_search='+all_search+'&pincode='+pincode+'&status='+status+'&checked_id='+checked_id

    document.location.href = _url;

}

$('#id_select_all_vendor').change(function (){

    var vendor_ids = $('.vendor_checkbox:checked').map(function(){
        return $(this).val();
    });


    if (vendor_ids.length == 0){
        $('#vendor_mark').html('')
    }else{
        $('#vendor_mark').html('Total '+vendor_ids.length+ ' vendor selected.')
    }

});


$('.vendor_checkbox').change(function (){

    $('#id_select_all_vendor').prop('checked', false);

    var vendor_ids = $('.vendor_checkbox:checked').map(function(){
        return $(this).val();
    });


    if (vendor_ids.length == 0){
        $('#vendor_mark').html('')
    }else{
        $('#vendor_mark').html('Total '+vendor_ids.length+ ' vendor selected.')
    }

});