// Dashboard product js.

// function to download product.
function download_product(url, upc, title, status, product_type, is_image, vendor_name, vendor_pincode, category, sub_category){
    console.log(vendor_pincode)
    var checked_id = [];
    $.each($("input[class='product_checkbox']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?upc='+upc+'&title='+title+'&status='+status+'&product_type='+product_type+'&is_image='+is_image+'&vendor_name='+vendor_name+'&vendor_pincode='+vendor_pincode+'&checked_id='+checked_id+'&category='+category+'&sub_category='+sub_category;
    document.location.href = _url;
}

$('#master_checkbox').change(function (){

    var product_ids = $('.product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (product_ids.length == 0){
        $('#product_mark').html('')
    }else{
        $('#product_mark').html('Total '+product_ids.length+ ' product selected.')
    }

})

$('.product_checkbox').change(function (){

    $('#master_checkbox').prop('checked', false);

    var product_ids = $('.product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (product_ids.length == 0){
        $('#product_mark').html('')
    }else{
        $('#product_mark').html('Total '+product_ids.length+ ' product selected.')
    }

})
