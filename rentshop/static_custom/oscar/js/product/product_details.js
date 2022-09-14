var attr_select = [];

function trigger_attr_select(e, type){

    if (e.value && type){
        var has_added = attr_select.some(e => e.hasOwnProperty(type));
        if(has_added){
            for(var i in attr_select){
                for(var j in attr_select[i]){
                    if(j == type){
                       delete attr_select[i][type]
                    }
                }
            }
        }
        attr_select.push(
            {[type]: e.value}
        )
    }

    var newArray = attr_select.filter(value => Object.keys(value).length !== 0);
    $('#id_product_attributes').val(JSON.stringify(newArray));

}

$(document).ready(function () {

    $("#add_to_basket_form").submit(function(e){
        var has_attribute = $('.has_attribute').val();
        var arry = []

        if (has_attribute){
            $('select[name="control-attr"]').each(function(){
                if(this.value == ''){
                    arry.push('NO_RECORD')
                }
            });
            if ($('.color_el').length != 0){
                if($('.color_el').is(':checked')) {

                }else{
                    arry.push('NO_RECORD')
                }
            }
        }


        if(arry != ''){
            alert('Please select product attributes.')
            return false;
        }
        var id_product_class = $('.add-to-cart').val();
        if(id_product_class == 'Rent' || id_product_class == 'Professional')
        {

        var startDate = $('#id_booking_start_date').val();
        var endDate = $('#id_booking_end_date').val();
        const oneDay = 24 * 60 * 60 * 1000;
        startDate = new Date(startDate);
        endDate = new Date(endDate);
        var diffDays = Math.round(Math.abs((endDate - startDate) / oneDay));
        diffDays = diffDays+1

        if(diffDays >= 2)
        {
        var r = confirm("You selected "+diffDays+" days for the event");
        if (r == false) {

        return false;
        }
        }
}

    });
$(window).load(function() {
        $('html, body').animate({scrollTop: $('#id_review_div').offset().top}, 1000);
    });
});

function trigger_filter_select(e, type){

    var final_array = []

    $('[name=control_att]').map(function() {
        var text = this.value;
        var text_attr = jQuery(this).data('original-title');

        if (text){
            final_array.push( { [text_attr]: text } )
        }


    });

//    if (e.value && type){
//        var has_added = attr_select.some(e => e.hasOwnProperty(type));
//        if(has_added){
//            for(var i in attr_select){
//                for(var j in attr_select[i]){
//                    if(j == type){
//                       delete attr_select[i][type]
//                    }
//                }
//            }
//        }
//        attr_select.push(
//            {[type]: e.value}
//        )
//    }
//    var newArray = attr_select.filter(value => Object.keys(value).length !== 0);
    $('#id_filter_list').val(JSON.stringify(final_array));

}
function successCallBack(returnData){
    // the main process have to be here
    confirm('Are you sure you want to delete');
}
function find_blocked_date()
{
            var product_type = $('#id_product_type').val()
        //alert("product type"+product_type)
        //var order_type = $('#id_order_type').val();
        //console.log("order type"+order_type);
        var status = true;
        if(product_type == 'Rent Or Sale')
        {
            var startDate = $('#id_booking_start_date').val();
            var product_id = $('#id_product_id').val();
             $.ajax({
            type:'GET',
            url : '/product_blocked_dates_onsubmit/',
            data : {
                product_id: product_id,
                booking_start_date : startDate,
            },

            success : function(data){
                console.log("data"+data+typeof data);
                if(data == 'True')
                {
                alert('Daily limit is over for this date please select another date and book product');
                status = false;
                }

            },
            async:false

            });
            if(status == false)
            {
            return false;
            }
            else{
            return true;
            }
        }

}
