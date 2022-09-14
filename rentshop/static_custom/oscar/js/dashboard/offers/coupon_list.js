function delete_coupon_confim(){

    var is_confirm = confirm("Do you really want to delete the coupon.");

    if (is_confirm == false){
        return false;
    }

    $('#coupon_delete').submit();

}

function delete_coupon(){

    var new_array = []

    var coupon_ids = $('.coupon_selected:checked').map(function(){
        return $(this).val();
    });

    if (coupon_ids.length == 0){
        alert('Please select coupon.');
        return false;
    }else{
        for(var i=0; i<coupon_ids.length; i++){
            new_array.push(coupon_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the coupons.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_coupon_list').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_coupon_data/',
        data : {
            coupon_id: $('#ids_coupon_list').val(),
        },
        success : function(data){
            if(data == 'IN_SERVER'){
                window.location.replace("/dashboard");
            }
            if (data == 'TRUE'){
                window.location.reload();
            }
        },
        failure : function(result){
        },
    });

}

function export_coupon(url, name, code){

    var checked_id = [];
    $.each($("input[class='coupon_selected']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?&name='+name+'&code='+code+'&checked_id='+checked_id;
    document.location.href = _url;
}

$('#master_coupon').change(function (){

    $('.coupon_selected:checkbox').not(this).prop('checked', this.checked);

    var coupon_ids = $('.coupon_selected:checked').map(function(){
        return $(this).val();
    });

    if (coupon_ids.length == 0){
        $('#coupon_mark').html('')
    }else{
        $('#coupon_mark').html('Total '+coupon_ids.length+ ' coupon selected.')
    }

});

$('.coupon_selected').change(function (){

    $('#master_coupon').prop('checked', false);

    var coupon_ids = $('.coupon_selected:checked').map(function(){
        return $(this).val();
    });

    if (coupon_ids.length == 0){
        $('#coupon_mark').html('')
    }else{
        $('#coupon_mark').html('Total '+coupon_ids.length+ ' coupon selected.')
    }

});