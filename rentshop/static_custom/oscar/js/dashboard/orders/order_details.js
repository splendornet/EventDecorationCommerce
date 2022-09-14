function confirm_order_status(){
    var is_confirm = confirm("Do you really want to change the order status ?");
    if (is_confirm == false){
        return false;
    }else{
        $('.order_st').submit()
    }
}

function add_line_formset(){
    $('.empty:last').nextAll().slice(0, 2).toggleClass('empty tr_clone');
}
