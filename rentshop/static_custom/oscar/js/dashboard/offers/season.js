// delete confirmation
function delete_confirmation(){

    var is_confirm = confirm("Do you really want to delete the coupon season.");

    if (is_confirm == false){
        return false;
    }

    $('#season_form').submit();
}

// method to delete season
function delete_season(){

    var new_array = []

    var season_ids = $('.selected_season:checked').map(function(){
        return $(this).val();
    });

    if (season_ids.length == 0){
        alert('Please select coupon season.');
        return false;
    }else{
        for(var i=0; i<season_ids.length; i++){
            new_array.push(season_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the coupon season.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_season_list').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_season/',
        data : {
            season_id: $('#ids_season_list').val(),
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

// method to export season
function export_season(url, season_name){

    var checked_id = [];
    $.each($("input[class='selected_season']:checked"), function(){
        checked_id.push($(this).val());
    });

    var _url = url+'?&season_name='+season_name+'&checked_id='+checked_id;
    document.location.href = _url;
}

// change method to select master checkbox.
$('#master_season').change(function (){

    $('.selected_season:checkbox').not(this).prop('checked', this.checked);

    var season_ids = $('.selected_season:checked').map(function(){
        return $(this).val();
    });

    if (season_ids.length == 0){
        $('#season_mark').html('')
    }else{
        $('#season_mark').html('Total '+season_ids.length+ ' coupon season selected.')
    }

});

// single checkbox select change method
$('.selected_season').change(function (){

    $('#master_season').prop('checked', false);

    var season_ids = $('.selected_season:checked').map(function(){
        return $(this).val();
    });

    if (season_ids.length == 0){
        $('#season_mark').html('')
    }else{
        $('#season_mark').html('Total '+season_ids.length+ ' coupon season selected.')
    }

});