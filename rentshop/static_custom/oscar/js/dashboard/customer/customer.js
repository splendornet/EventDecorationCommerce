
// customer js

$('document').ready(function(){
    $("#master_user_checkbox").click(function () {
        $('.selected_user:checkbox').not(this).prop('checked', this.checked);
    });
})


function export_customer(url, email, name, search,status){

    var checked_id = [];
    $.each($("input[class='selected_user']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?email='+email+'&name='+name+'&search='+search+'&status='+status+'&checked_id='+checked_id
    document.location.href = _url;

}

function delete_bulk_user(){

    $('#ids_list_user').val('');
    var new_array = []

    var user_ids = $('.selected_user:checked').map(function(){
        return $(this).val();
    });

    if (user_ids.length == 0){
        alert('Please select user');
        return false;
    }else{
        for(i=0; i<user_ids.length; i++){
            new_array.push(user_ids[i])
        }
    }

    $('#ids_list_user').val(new_array);

    var is_confirm = confirm("Do you really want to delete the users.");

    if (is_confirm == false){
        return false;
    }

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_user/',
        data : {
            user_id: $('#ids_list_user').val(),
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

$('#master_user_checkbox').change(function (){

    var user_ids = $('.selected_user:checked').map(function(){
        return $(this).val();
    });


    if (user_ids.length == 0){
        $('#user_mark').html('')
    }else{
        $('#user_mark').html('Total '+user_ids.length+ ' user selected.')
    }

});

$('.selected_user').change(function (){

    $('#master_user_checkbox').prop('checked', false);

    var user_ids = $('.selected_user:checked').map(function(){
        return $(this).val();
    });


    if (user_ids.length == 0){
        $('#user_mark').html('')
    }else{
        $('#user_mark').html('Total '+user_ids.length+ ' user selected.')
    }

});