$(function() {

    // method to update cart line quantity
    $('.quantity_update').on('change', function(){
        setTimeout(
        function(){
            $('.btn-update').click();
        }, 1000);
    })

    // method to fade-out error message after 5secs
    setTimeout(function() {
        $(".error-div").hide('blind', {}, 500)
    }, 5000);



});

// hide loader
$(window).load(function() {
   $('.loader_master').hide();
});


// method to apply date selection
function date_apply_btn(){

    var modal = document.getElementById('date_picker_modal');
    var span = document.getElementsByClassName("close")[0];

    var start_date_obj = $('#id_start_date').val();
    var end_date_obj = $('#id_end_date').val();

    if(start_date_obj == '' || end_date_obj == ''){
        alert("Please select start and end date");
        return false;
    }

    var start_date_strip = moment(start_date_obj, "MM-DD-YYYY");
    var end_date_strip = moment(end_date_obj, "MM-DD-YYYY");
    var total_days = end_date_strip.diff(start_date_strip,'days') + 1;
    var dtLabelTxt = 'From '+formatDate(start_date_obj)+' To '+formatDate(end_date_obj);
    var fieldCounter = $('#field_counter').val();

    $('#date_btn_above_label_'+fieldCounter).text(dtLabelTxt);
    $('#date_btn_'+fieldCounter).text('For '+total_days+' Days');

    $('#id_form-'+fieldCounter+'-booking_start_date').val(start_date_obj);
    $('#id_form-'+fieldCounter+'-booking_end_date').val(end_date_obj);

    $('#id_start_date').val('');
    $('#id_end_date').val('');

    modal.style.display = "none";
    $('.btn-update').click();


}