function confirm_event_delete(url){

    var is_confirm = confirm("Do you really want to delete the event.");

    if (is_confirm == false){
        return false;
    }

    document.location.href = url;
}

function delete_event(){

    var new_array = []

    var event_ids = $('.selected_event:checked').map(function(){
        return $(this).val();
    });

    if (event_ids.length == 0){
        alert('Please select event.');
        return false;
    }else{
        for(var i=0; i<event_ids.length; i++){
            new_array.push(event_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the event.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_ev_list').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_event/',
        data : {
            ev_id: $('#ids_ev_list').val(),
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


function export_event(url, product, category, sub_category){

    var checked_id = [];
    $.each($("input[class='selected_event']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?&product='+product+'&checked_id='+checked_id+'&category='+category+'&sub_category='+sub_category;
    document.location.href = _url;

}



$('#master_event').change(function (){

    $('.selected_event:checkbox').not(this).prop('checked', this.checked);

    var selected_ids = $('.selected_event:checked').map(function(){
        return $(this).val();
    });

    if (selected_ids.length == 0){
        $('#selected_mark').html('')
    }else{
        $('#selected_mark').html('Total '+selected_ids.length+ ' event selected.')
    }

});

$('.selected_event').change(function (){

    $('#master_event').prop('checked', false);

    var selected_ids = $('.selected_event:checked').map(function(){
        return $(this).val();
    });

    if (selected_ids.length == 0){
        $('#selected_mark').html('')
    }else{
        $('#selected_mark').html('Total '+selected_ids.length+ ' event selected.')
    }

});