// method to export unit.
function export_unit(url, unit){

    var checked_id = [];
    $.each($("input[class='unit_checkbox']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?&unit='+unit+'&checked_id='+checked_id;
    document.location.href = _url;

}

// method to delete unit
function delete_confirmation_unit(){
    var is_confirm = confirm("Do you really want to delete this unit.");
    if (is_confirm == false){
        return false;
    }else{
        $('#unit_delete_form').submit()
    }
}

// method to delete unit in bulk
function bulk_unit_delete(){

    var new_array = []

    var unit_ids = $('.unit_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (unit_ids.length == 0){
        alert('Please select units');
        return false;
    }else{
        for(i=0; i<unit_ids.length; i++){
            new_array.push(unit_ids[i])
        }
    }

    $('#ids_list_unit').val(new_array);

    var is_confirm = confirm("Do you really want to delete the units.");

    if (is_confirm == false){
        return false;
    }

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_units/',
        data : {
            unit_id: $('#ids_list_unit').val(),
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


// method to select all checkboxes

$("#unit_master").click(function () {
    $('.unit_checkbox:checkbox').not(this).prop('checked', this.checked);

    var unit_ids = $('.unit_checkbox:checked').map(function(){
        return $(this).val();
    });


    if (unit_ids.length == 0){
        $('#unit_mark').html('')
    }else{
        $('#unit_mark').html('Total '+unit_ids.length+ ' unit selected.')
    }

});

$('.unit_checkbox').change(function (){

    $('#unit_master').prop('checked', false);

    var unit_ids = $('.unit_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (unit_ids.length == 0){
        $('#unit_mark').html('')
    }else{
        $('#unit_mark').html('Total '+unit_ids.length+ ' unit selected.')
    }

})