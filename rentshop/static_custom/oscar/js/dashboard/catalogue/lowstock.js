$('#id_select_all_lowstock').change(function (){

    $('.selected_lowstock:checkbox').not(this).prop('checked', this.checked);

    var lowstock_ids = $('.selected_lowstock:checked').map(function(){
        return $(this).val();
    });

    if (lowstock_ids.length == 0){
        $('#stock_mark').html('')
    }else{
        $('#stock_mark').html('Total '+lowstock_ids.length+ ' stock selected.')
    }

});

$('.selected_lowstock').change(function (){

    $('#id_select_all_lowstock').prop('checked', false);

    var lowstock_ids = $('.selected_lowstock:checked').map(function(){
        return $(this).val();
    });

    if (lowstock_ids.length == 0){
        $('#stock_mark').html('')
    }else{
        $('#stock_mark').html('Total '+lowstock_ids.length+ ' stock selected.')
    }

});

function export_low_stock(url, product, status){

    var checked_id = [];
    $.each($("input[class='selected_lowstock']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url;
    document.location.href = _url+'?&product='+product+'&checked_id='+checked_id+'&status='+status;
}