$('document').ready(function(){

    // change method to toggle is dp image checkboxes.
    $('input.is_dp_class').on('change', function() {
        $('input.is_dp_class').not(this).prop('checked', false);
    });

    for (i=0; i<=100; i++){
        //console.log(i)
        //$(".main_"+i+":not(:last)").remove();

//        ​$('.className').not(':last')​.remove();​​​​​​​​​​​​​
    }



});