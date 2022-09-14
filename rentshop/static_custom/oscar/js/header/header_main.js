// header js

function mega_button() {

    document.getElementById("mega_id").classList.toggle("mega_show");

    if($('#mega_id').hasClass('mega_show')){
        $('html').addClass('overflowHidden');
    }else{
        $('html').removeClass('overflowHidden');
    }

    masonary_grid()
}

function masonary_grid(){
    $('.masonary-grid').masonry({
        itemSelector: '.masonary-grid-item',
        percentPosition: true
    });
}

function header_search(){
    var path = window.location.href;
    var q = $('#q').val();
    var q1 = $('#mobileq').val();

    if (q == 'Search'){
        q = ''
    }
    else if (q1)
    {
        q=q1
    }
    search_url = '/catalogue/?mega_search=' + q
//    if(path.includes("/category")){
//        var search_url = path + '?mega_search='+q
//    }
//    else{
//        var search_url = '/catalogue/?mega_search=' + q
//    }
    window.open(search_url, '_blank');
}


$('#q').keypress(function(e) {
    var key = e.which;
    if (key == 13){
        header_search()
        return false;
    }
});

window.onclick = function(event) {

    if (!event.target.matches('.xcollapse-menu')) {
        var dropdowns = document.getElementsByClassName("menu-sub");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('mega_show')) {
                openDropdown.classList.remove('mega_show');
            }
        }
    }
    if($('#mega_id').hasClass('mega_show')){
        $('html').addClass('overflowHidden');
    }else{
        $('html').removeClass('overflowHidden');
    }
}

$(document).ready(function(event) {
    $('form[name=search_sudo]').submit(function(event){
        event.preventDefault();
        //add stuff here
    });
});
