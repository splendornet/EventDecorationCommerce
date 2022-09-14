// category js


// event to select all checkboxes.
$("#master_category_checkbox").click(function () {
    $('.selected_category:checkbox').not(this).prop('checked', this.checked);

    var category_ids = $('.selected_category:checked').map(function(){
        return $(this).val();
    });

    if (category_ids.length == 0){
        $('#category_mark').html('')
    }else{
        $('#category_mark').html('Total '+category_ids.length+ ' category selected.')
    }

});


$('.selected_category').change(function (){

    $('#master_category_checkbox').prop('checked', false);

    var category_ids = $('.selected_category:checked').map(function(){
        return $(this).val();
    });

    if (category_ids.length == 0){
        $('#category_mark').html('')
    }else{
        $('#category_mark').html('Total '+category_ids.length+ ' category selected.')
    }

})


function bulk_category_delete(){

    var new_array = []

    var category_ids = $('.selected_category:checked').map(function(){
        return $(this).val();
    });

    if (category_ids.length == 0){
        alert('Please select category.');
        return false;
    }else{
        for(var i=0; i<category_ids.length; i++){
            new_array.push(category_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the category.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_category_list').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_category/',
        data : {
            category_id: $('#ids_category_list').val(),
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


function download_category(url){

    var checked_id = [];
    $.each($("input[class='selected_category']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?&checked_id='+checked_id
    document.location.href = _url;

}