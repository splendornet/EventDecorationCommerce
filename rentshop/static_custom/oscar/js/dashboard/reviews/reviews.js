function export_reviews(url, status, category, date, month, year, rating, title){

    var checked_id = [];
    $.each($("input[class='selected_review']:checked"), function(){
        checked_id.push($(this).val());
    });
    console.log("title"+title)
    var _url = url+'?&status=' +status+ '&category=' +category+ '&date=' +date+ '&month=' +month+ '&year=' +year+ '&rating='+rating+ '&title='+title+ '&checked_id='+checked_id;
    document.location.href = _url;

}

function delete_review(){

    var is_confirm = confirm("Do you really want to delete the review.");

    if (is_confirm == false){
        return false;
    }

    $('#review_delete_form').submit();

}

function review_bulk_delete(){

    var new_array = []

    var review_ids = $('.selected_review:checked').map(function(){
        return $(this).val();
    });

    if (review_ids.length == 0){
        alert('Please select reviews.');
        return false;
    }else{
        for(var i=0; i<review_ids.length; i++){
            new_array.push(review_ids[i])
        }
    }

    var is_confirm = confirm("Do you really want to delete the reviews.");

    if (is_confirm == false){
        return false;
    }

    $('#ids_review_list').val(new_array);

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_reviews/',
        data : {
            review_id: $('#ids_review_list').val(),
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

$('#id_select_all_reviews').change(function (){

    $('.selected_review:checkbox').not(this).prop('checked', this.checked);

    var review_ids = $('.selected_review:checked').map(function(){
        return $(this).val();
    });

    if (review_ids.length == 0){
        $('#review_mark').html('')
    }else{
        $('#review_mark').html('Total '+review_ids.length+ ' review selected.')
    }

});

$('.selected_review').change(function (){

    $('#id_select_all_reviews').prop('checked', false);

    var review_ids = $('.selected_review:checked').map(function(){
        return $(this).val();
    });

    if (review_ids.length == 0){
        $('#review_mark').html('')
    }else{
        $('#review_mark').html('Total '+review_ids.length+ ' review selected.')
    }

});
