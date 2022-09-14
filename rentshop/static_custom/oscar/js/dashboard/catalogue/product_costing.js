function calculate_tax(){
    var rent_price_incl_tax = $('#id_stockrecords-0-rent_price').val();
    console.log(rent_price_incl_tax)
}

$( document ).ready(function() {
    calculate_tax()
});