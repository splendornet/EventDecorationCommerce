function master_check(e, child, label_class){

    $('.'+child).not(e).prop('checked', e.checked);

    var selected_record = $('.'+child+':checked').map(function(){
        return $(this).val();
    });

    if (selected_record.length == 0){
        $('.'+label_class).html('')
    }else{
        $('.'+label_class).html('Total '+selected_record.length+ ' record selected.')
    }
}

//$('#_id_select_all_product').change(function (){
//
//    $('._rate_card_product_checkbox:checkbox').not(this).prop('checked', this.checked);
//
//    var rt_ids = $('._rate_card_product_checkbox:checked').map(function(){
//        return $(this).val();
//    });
//
//    if (rt_ids.length == 0){
//        $('#_rate_card_product_mark').html('')
//    }else{
//        $('#_rate_card_product_mark').html('Total '+rt_ids.length+ ' record selected.')
//    }
//
//});

$('._rate_card_product_checkbox').change(function (){

    $('#_id_select_all_product').prop('checked', false);

    var rt_ids = $('._rate_card_product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (rt_ids.length == 0){
        $('#_rate_card_product_mark').html('')
    }else{
        $('#_rate_card_product_mark').html('Total '+rt_ids.length+ ' record selected.')
    }

});

$('#id_select_all_product').change(function (){

    //$('.rate_card_product_checkbox:checkbox').not(this).prop('checked', this.checked);

//    var rt_ids = $('.rate_card_product_checkbox:checked').map(function(){
//        return $(this).val();
//    });
//
//    if (rt_ids.length == 0){
//        $('#rate_card_product_mark').html('')
//    }else{
//        $('#rate_card_product_mark').html('Total '+rt_ids.length+ ' product selected.')
//    }

});

$('.rate_card_product_checkbox').change(function (){

    $('#id_select_all_product').prop('checked', false);

    var rt_ids = $('.rate_card_product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (rt_ids.length == 0){
        $('#rate_card_product_mark').html('')
    }else{
        $('#rate_card_product_mark').html('Total '+rt_ids.length+ ' product selected.')
    }

});

function bulk_rate_card_product_delete(){
    var new_array = []

    var rc_ids = $('.rate_card_product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (rc_ids.length == 0){
        alert('Please select products.');
        return false;
    }else{
        for(var i=0; i<rc_ids.length; i++){
            new_array.push(rc_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the products.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_list_rate_card_product').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_costing_product/',
        data : {
            product_id: $('#ids_list_rate_card_product').val(),
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

function _bulk_rate_card_product_delete(){

    var new_array = []

    var rc_ids = $('._rate_card_product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (rc_ids.length == 0){
        alert('Please select items.');
        return false;
    }else{
        for(var i=0; i<rc_ids.length; i++){
            new_array.push(rc_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the selected records.");

    if (is_confirm == false){
        return false;
    }

    $('#_ids_list_rate_card_product').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_costing_product_items/',
        data : {
            items: $('#_ids_list_rate_card_product').val(),
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

function rate_card_product_download(url, product_id){

    var checked_id = [];
    $.each($("input[class='_rate_card_product_checkbox']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?checked_id='+checked_id+'&product_id='+product_id

    document.location.href = _url;

}

function export_rate_card_product(url, product, product_upc, category, sub_category){
            var checked_id = [];
            $.each($("input[class='rate_card_product_checkbox']:checked"), function(){
                checked_id.push($(this).val());
            });
            var _url = url+'?&checked_id='+checked_id+'&category='+category+'&sub_category='+sub_category+'&product='+product+'&product_upc='+product_upc;
            document.location.href = _url;
}

function add_product_card(){
    $('#create_rate_card').modal('show');
}

function create_rate_product(){

    var product = $('#rate_product').val();
    if (product == ''){
        alert('Please select valid product.')
        return false;
    }

    var url = '/dashboard/catalogue/rate-card/products/create/'
    var _url = url+'?product='+product;
    document.location.href = _url;
}

$(document).ready(function(){
    $('#id_product').select2({width: '150px'});
    $('#id_category').select2({width: '150px'});
    $('#id_sub_category').select2({width: '150px'});
    $('#rate_product').select2({
        width: '100%',
        minimumInputLength: 2,
        ajax: {
            url: '/get_event_products_rate_card',
            dataType: 'json',
            type: "GET",
            data: function (term) {
                return {
                    term: term
                };
            },
            processResults: function (response) {
                return {
                    results: $.map(response, function (item) {

                        return {
                            text: item.itemName,
                            id: item.id
                        }
                    })
                };
            },

        }
    });
});

category_auto_select();
