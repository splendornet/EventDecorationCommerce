// order list js

function export_orders(url, order_number, status, product, category, sub_category, name){

    var checked_id = [];
    $.each($("input[class='order_selected']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url + '?order_number='+order_number+'&status='+status+'&product='+product+'&checked_id='+checked_id+'&category='+category+'&sub_category='+sub_category+'&name='+name;
    document.location.href = _url;

}

$('#order_master_selected').change(function (){
    $('.order_selected:checkbox').not(this).prop('checked', this.checked);

    var order_ids = $('.order_selected:checked').map(function(){
        return $(this).val();
    });

    if (order_ids.length == 0){
        $('#order_mark').html('')
    }else{
        $('#order_mark').html('Total '+order_ids.length+ ' order selected.')
    }

});

$('.order_selected').change(function (){

    $('#order_master_selected').prop('checked', false);

    var order_ids = $('.order_selected:checked').map(function(){
        return $(this).val();
    });

    if (order_ids.length == 0){
        $('#order_mark').html('')
    }else{
        $('#order_mark').html('Total '+order_ids.length+ ' order selected.')
    }

});