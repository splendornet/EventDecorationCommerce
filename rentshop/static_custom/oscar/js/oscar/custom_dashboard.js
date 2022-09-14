// method to add image.
function add_image_formset(){
    $('.show:last').nextAll().slice(0, 2).toggleClass('show hide_me');
}

function add_attribute_formset(){
    $('.empty:last').nextAll().slice(0, 2).toggleClass('empty tr_clone');
}

function delete_attribute(counter){
    //alert(counter)
    var attribute_id = 'id_attribute_mapping_set-'+counter+'-id'
    //alert(attribute_id)
    var db_id = $('#'+attribute_id).val();
    if (db_id == ''){
        alert('You can not preform this action.')
        return false;
    }
    var is_confirm = confirm("Do you really want to delete this attribute.");

    if (is_confirm == false){
        return false;
    }
    delete_attribute_ajax(db_id)

}

function get_attributechange(counter){
    var attr_id = 'id_attribute_mapping-'+counter+"-attribute"
    var db_id = $('#'+attr_id).val();
    //alert(db_id);
    if(db_id == '')
    {
    alert("Please select attribute");
    return False;
    }
    //alert(db_id);
    var value_id = 'id_attribute_mapping-'+counter+'-value'

    //alert("hello");
    //alert(db_id)
     $.ajax({
        type:'GET',
        url : '/get_values_of_attribute/',
        data : {
            attribute_id: db_id
        },
        success : function(data){
        //alert("success");
        //alert(value_id);
            $("#"+value_id).html(data);
        },
        failure : function(result){

        },
    });


}

function get_attributechange1(){
    var no = $(this).val();
    //alert(no);
    //var value_id = 'id_attribute_mapping-'+counter+'-value'


}
function delete_attribute_ajax(id){
    $.ajax({
        type:'GET',
        url : '/delete_product_attribute/',
        data : {
            attribute_id: id
        },
        success : function(data){
            if (data == '503'){
                window.location.replace("/dashboard/catalogue/");
            }
            if (data == '200'){
                window.location.reload();
            }
        },
        failure : function(result){

        },
    });
}
// method to get user confirmation before deleting vendor.
function delete_confirmation_vendor(){
    var is_confirm = confirm("Do you really want to delete this asp.");
    if (is_confirm == false){
        return false;
    }else{
        $('#vendor_delete_form').submit()
    }
}



// method to get user confirmation before deleting product images.
function delete_image(counter){

    var image_id = 'id_images-'+counter+'-id'
    var db_id = $('#'+image_id).val();
    if (db_id == ''){
        alert('You can not preform this action.')
        return false;
    }
    var is_confirm = confirm("Do you really want to delete this image.");

    if (is_confirm == false){
        return false;
    }
    delete_image_ajax(db_id)

}

function bulk_vendor_delete(){

    var new_array = []

    var vendor_ids = $('.vendor_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (vendor_ids.length == 0){
        alert('Please select vendors');
        return false;
    }else{
        for(i=0; i<vendor_ids.length; i++){
            new_array.push(vendor_ids[i])
        }
    }

    $('#ids_list_vendor').val(new_array);

    var is_confirm = confirm("Do you really want to delete the vendors.");

    if (is_confirm == false){
        return false;
    }

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_vendor/',
        data : {
            vendor_id: $('#ids_list_vendor').val(),
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


function delete_image_ajax(id){
    $.ajax({
        type:'GET',
        url : '/delete_product_image/',
        data : {
            image_id: id
        },
        success : function(data){
            if (data == '503'){
                window.location.replace("/dashboard/catalogue/");
            }
            if (data == '200'){
                window.location.reload();
            }
        },
        failure : function(result){

        },
    });
}


function bulk_delete(){

    var new_array = []

    var product_ids = $('.product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (product_ids.length == 0){
        alert('Please select products');
        return false;
    }else{
        for(i=0; i<product_ids.length; i++){
            new_array.push(product_ids[i])
        }
    }

    $('#ids_list').val(new_array);

    var is_confirm = confirm("Do you really want to delete the products.");

    if (is_confirm == false){
        return false;
    }

    // ajax method
    $.ajax({
        type:'GET',
        url : '/delete_bulk_product/',
        data : {
            product_id: $('#ids_list').val(),
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

function bulk_update(){

    var new_array = []

    var product_ids = $('.product_checkbox:checked').map(function(){
        return $(this).val();
    });

    if (product_ids.length == 0){
        alert('Please select products');
        return false;
    }else{
        for(i=0; i<product_ids.length; i++){
            new_array.push(product_ids[i])
        }

    }

    var is_confirm = confirm("Do you really want to update the products.");

    if (is_confirm == false){
        return false;
    }

    var status = $('#new_status').val()
    if (status){
        $('#ids_list').val(new_array);

        // ajax method
        $.ajax({
            type:'GET',
            url : '/update_product/',
            data : {
                product_id: $('#ids_list').val(),
                status: status
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



    }else{
        alert('Please select status');
        return false;
    }

}

$( function() {

    $('.hide_me').hide();
    $('#mceu_20-body').hide();


    var numItems = $('.has_image').length
    if(numItems == 1){
        $('.btn-image-delete').attr("disabled", true);
    }else{
        $('.btn-image-delete').attr("disabled", false);
    }

    var numItems1 = $('.has_attribute').length
    if(numItems1 == 1){
        $('.btn-attribute-delete').attr("disabled", true);
    }else{
        $('.btn-attribute-delete').attr("disabled", false);
    }

    $("#master_checkbox").click(function () {
        $('.product_checkbox:checkbox').not(this).prop('checked', this.checked);
    });

    $("#id_select_all_vendor").click(function () {
        $('.vendor_checkbox:checkbox').not(this).prop('checked', this.checked);
    });

    $('.seq-class').on('change', function(){
        if(this.value == 0){
            this.value = '';
            alert('Sequence number cannot be zero');
        }
    });

    $('.admin_form').submit(function( event ) {
        var values = [];
        var is_dp_image = $('.is_dp_class:checkbox:checked').length > 0;
        if (is_dp_image == false){
            alert('Please select DP image.')
            return false;
        }
        var product_cost_type = $('#id_product_cost_type').val();
        var product_type = $('#id_product_type').val();
        var is_transportation = $('input[name="is_transporation_available"]:checkbox:checked')

        var rent_transportation_price = $('#id_stockrecords-0-rent_transportation_price').val()
        if((product_type != 'Service') && ( product_cost_type == 'Single') && ($('input[name="is_transporation_available"]').prop('checked')==true))
        {
	        if((product_type == 'Rent') || (product_type == 'Professional'))
            {
               var rent_transportation_price = $('#id_stockrecords-0-rent_transportation_price').val()

                   if (!rent_transportation_price)
                   {
                        alert("Please enter rent transportation cost.");
                        return false;
                   }
             }
             else if(product_type == 'Sale')
            {
               var sale_transportation_price = $('#id_stockrecords-0-sale_transportation_price').val()

                    if (!sale_transportation_price)
                   {
                        alert("Please enter sale transportation cost.");
                        return false;
                   }
             }
             else if(product_type == 'Rent Or Sale')
            {
               var rent_transportation_price = $('#id_stockrecords-0-rent_transportation_price').val()
               var sale_transportation_price = $('#id_stockrecords-0-sale_transportation_price').val()

                   if ((!rent_transportation_price) && (!sale_transportation_price))
                   {
                        alert("Please enter sale and rent transportation cost");
                        return false;
                   }
                   else if((!rent_transportation_price) && (sale_transportation_price))
                   {
                        alert("Please enter rent transportation cost");
                        return false;
                   }
                   else if ((rent_transportation_price) && (!sale_transportation_price))
                   {
                        alert("Please enter sale transportation cost");
                        return false;
                   }

             }
        }
        if((product_type != 'Service') && ( product_cost_type == 'Single'))
        {
	        if((product_type == 'Rent') || (product_type == 'Professional'))
            {
               var rent_price = $('#id_stockrecords-0-rent_price').val()
               var art_rent_price = $('#id_stockrecords-0-art_rent_price').val()
               if(($('#id_is_real_flower').is(':checked')) && ($('#id_is_artificial_flower').is(':checked')))
               {
                   if(!rent_price && !art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real and artificial flower");
                        return false;
                   }
                   else if(!rent_price && art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for artificial flower");
                        return false;
                   }
                   else if(rent_price && !art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_real_flower').is(':checked'))
               {
                   if (!art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_artificial_flower').is(':checked'))
               {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax for artificial flower");
                        return false;
                   }
               }
               else
               {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax.");
                        return false;
                   }
               }
             }
             else if(product_type == 'Sale')
            {
               var sale_price = $('#id_stockrecords-0-price_excl_tax').val()
               var art_sale_price = $('#id_stockrecords-0-art_sale_price').val()

               if(($('#id_is_real_flower').is(':checked')) && ($('#id_is_artificial_flower').is(':checked')))
               {
                   if(!sale_price && !art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real and artificial flower");
                        return false;
                   }
                   else if(!sale_price && art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for artificial flower");
                        return false;
                   }
                   else if(sale_price && !art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_real_flower').is(':checked'))
               {
                   if (!art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_artificial_flower').is(':checked'))
               {
                   if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax for artificial flower");
                        return false;
                   }
               }
               else
               {
                    if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax.");
                        return false;
                   }
               }

             }
             else if(product_type == 'Rent Or Sale')
            {
               var rent_price = $('#id_stockrecords-0-rent_price').val()
               var art_rent_price = $('#id_stockrecords-0-art_rent_price').val()
               var sale_price = $('#id_stockrecords-0-price_excl_tax').val()
               var art_sale_price = $('#id_stockrecords-0-art_sale_price').val()

               if(($('#id_is_real_flower').is(':checked')) && ($('#id_is_artificial_flower').is(':checked')))
               {
                    if(!rent_price && !art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real and artificial flower");
                        return false;
                   }
                   else if(!rent_price && art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for artificial flower");
                        return false;
                   }
                   else if(rent_price && !art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real flower");
                        return false;
                   }
                   if(!sale_price && !art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real and artificial flower");
                        return false;
                   }
                   else if(!sale_price && art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for artificial flower");
                        return false;
                   }
                   else if(sale_price && !art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_real_flower').is(':checked'))
               {
                   if (!art_rent_price)
                   {
                        alert("Please enter rent price excluding tax for real flower");
                        return false;
                   }
                   if (!art_sale_price)
                   {
                        alert("Please enter sale price excluding tax for real flower");
                        return false;
                   }
               }
               else if($('#id_is_artificial_flower').is(':checked'))
               {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax for artificial flower");
                        return false;
                   }
                   if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax for artificial flower");
                        return false;
                   }
               }
               else
               {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax.");
                        return false;
                   }
                   if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax.");
                        return false;
                   }
               }
             }
        }
        if((product_type != 'Service') && (product_cost_type == 'Multiple'))
        {
            var rent_price = $('#id_stockrecords-0-rent_price').val()
            var sale_price = $('#id_stockrecords-0-price_excl_tax').val()
            if((product_type == 'Rent') || (product_type == 'Professional'))
            {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax.");
                        return false;
                   }
            }
            else if(product_type == 'Sale')
            {
                    if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax.");
                        return false;
                   }
            }
            else if(product_type == 'Rent Or Sale')
            {
                   if (!rent_price)
                   {
                        alert("Please enter rent price excluding tax.");
                        return false;
                   }
                   if (!sale_price)
                   {
                        alert("Please enter sale price excluding tax.");
                        return false;
                   }
            }
        }



        $('.seq-class').each(function() {
            if (this.value != ''){
                if (values.indexOf(this.value) >= 0) {
                    alert('Sequence number '+this.value+ ' is already exist.')
                    event.preventDefault();
                    return false;
                }else{
                    values.push(this.value);
                }
            }
        });
    });

    $(".form-stacked").submit(function( event ) {


    });


})



$( function() {

    // A-Z sort for category

    var sortSelect = function (select, attr, order) {
        if(attr === 'text'){
            if(order === 'asc'){
                $(select).html($(select).children('option').sort(function (x, y) {
                    return $(x).text().toUpperCase() < $(y).text().toUpperCase() ? -1 : 1;
                }));
                $(select).get(0).selectedIndex = 0;
               // e.preventDefault();
            }// end asc
            if(order === 'desc'){
                $(select).html($(select).children('option').sort(function (y, x) {
                    return $(x).text().toUpperCase() < $(y).text().toUpperCase() ? -1 : 1;
                }));
                $(select).get(0).selectedIndex = 0;
               // e.preventDefault();
            }// end desc
        }
    };

    var sel = $('#id_productcategory_set-0-category');
    var selected = sel.val(); // cache selected value, before reordering
    var opts_list = sel.find('option');
    opts_list.sort(function(a, b) { return $(a).text().toUpperCase() < $(b).text().toUpperCase() ? -1 : 1;});
    sel.html('').append(opts_list);
    sel.val(selected);

    // A-Z sort for category end

    // Tiny Mce

    $("#id_name").attr('minlength','2');
    $("#id_name").attr('maxlength','50');

    tinyMCE.init({
        selector: 'textarea',
        indentation : '60pt',
        plugins: 'textcolor print preview importcss searchreplace autolink autosave save directionality visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists wordcount imagetools textpattern noneditable',
        paste_as_text:true,
        //menubar: false,
        toolbar: 'bold italic underline strikethrough superscript subscript | fontselect fontsizeselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor',
        //nonbreaking_force_tab: true,
        init_instance_callback: function(editor) {
            editor.on('keydown', function(e) {
                if(e.keyCode == 9){
                    e.preventDefault();
                    tinymce.activeEditor.execCommand('mceInsertContent', false, "&nbsp;&nbsp;&nbsp;&nbsp;");
                }
            });
        },

    });

    // Tiny Mce end

    // ajax for state city

    function matchStart (term, text) {
        if (text.toUpperCase().indexOf(term.toUpperCase()) == 0) {
            return true;
        }
        return false;
    }

    $('#id_state').change(function(){
        //console.log('state called');

        $.ajax({
            type:'GET',
            url : '/city_ajax',
            data : {
                state_name:this.value
            },
            success : function(city_data){
                if(city_data=='Ajax_City_Error'){
                    $('#id_city').find('option').remove().end().append("<option value=''>Select City</option>");
                   // $("#id_city").html('').select2({'val':'sss'});
                }
                else{
                    $(".select2-container").css("width","200px");
                    //$("#id_city").html('').select2({data: city_data});

                    $.fn.select2.amd.require(['select2/compat/matcher'], function (oldMatcher) {
                        $("#id_city").find('option').remove().end().append("<option value=''>Select City</option>").select2({
                            matcher: oldMatcher(matchStart),
                            data: city_data,
                        })
                    });
                }
            },
            failure : function(result){
                //$('#id_system_error').modal('show');
            },
        });
    });

    // ajax for state city end

    // regex for category name

    $('#id_name').bind('keypress', function (event) {
        var regex = new RegExp("^[a-zA-Z0-9\b\\s]+$");
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    });

    // regex for category name end


    // slider image update regex

    $('#id_update_submit').prop('disabled', true);

    $("#id_update_image").change(function () {
    //Get reference of FileUpload.
        var fileUpload = $("#id_update_image")[0];

        //Check whether the file is valid Image.
        var regex = new RegExp("([a-zA-Z0-9\s_\\.\-:])+(.jpg|.png)$");
        if (regex.test(fileUpload.value.toLowerCase())) {
            if (typeof (fileUpload.files) != "undefined") {
                var reader = new FileReader();
                reader.readAsDataURL(fileUpload.files[0]);
                reader.onload = function (e) {
                    var image = new Image();
                    image.src = e.target.result;
                    image.onload = function () {
                    //Determine the Height and Width.
                    var height = this.height;
                    var width = this.width;
                    if (height < 1200 && width < 800) {
                        $('#id_update_submit').prop('disabled', true);
                            alert("Enter valid image size.");
                            return false;
                        }
                        $('#id_update_submit').prop('disabled', false);
                        //alert("Uploaded image has valid Height and Width.");
                        return true;
                    };
                }
            }
            else {
                $('#id_update_submit').prop('disabled', true);
                alert("This browser does not support HTML5.");
                return false;
            }
        }
        else {
            $('#id_update_submit').prop('disabled', true);
            alert("Please select a valid Image file.");
            return false;
        }
    });

    // slider image update regex end

    // slider image upload regex

    $('#id_save_btn').prop('disabled', true);
    $("#id_slider_image").change(function () {
        //Get reference of FileUpload.
        var fileUpload = $("#id_slider_image")[0];

        //Check whether the file is valid Image.
        var regex = new RegExp("([a-zA-Z0-9\s_\\.\-:])+(.jpg|.png)$");
        if (regex.test(fileUpload.value.toLowerCase())) {
            if (typeof (fileUpload.files) != "undefined") {
                var reader = new FileReader();
                reader.readAsDataURL(fileUpload.files[0]);
                reader.onload = function (e) {
                    var image = new Image();
                    image.src = e.target.result;
                    image.onload = function () {
                    //Determine the Height and Width.
                        var height = this.height;
                        var width = this.width;
                        if (height < 1200 && width < 800) {
                            $('#id_save_btn').prop('disabled', true);
                            alert("Enter valid image size.");
                            return false;
                        }
                        $('#id_save_btn').prop('disabled', false);
                        //alert("Uploaded image has valid Height and Width.");
                        return true;
                    };
                }
            }
            else {
                $('#id_save_btn').prop('disabled', true);
                alert("This browser does not support HTML5.");
                return false;
            }
        }
        else {
            $('#id_save_btn').prop('disabled', true);
            alert("Please select a valid Image file.");
            return false;
        }
    });

    // slider image upload regex end

    // initlizing classes for input element
    $('#id_alternate_mobile_number,#id_business_name,#id_contact_person_name,#id_name,#id_email,#id_telephone_number,#id_address_line_1,#id_address_line_2,#id_country,#id_state,#id_city,#id_pincode,#id_email_id').addClass("form-control wpcf7-text wpcf7-validates-as-required");
    $("#id_state").select2();
    $("#id_city").select2();

    var vendCat = JSON.stringify($("#vendorCategories").val());
    $("#id_categories").select2('val',vendCat);


});




function inti_function(){
    $("html,body").animate({ scrollTop: 0 });
}

function category_auto_select(){

    $('#id_category').on('change', function(){

        $('#id_sub_category').select2({placeholder: 'Select Sub Category'});
        $("#id_sub_category").empty();

        $.ajax({
            type:'GET',
            url : '/dashboard/accounts/get-sub-category/',
            data : {
                category: this.value,
            },
            success : function(data){
                var sub_category = JSON.parse(data);
                $("#id_sub_category").select2('data', sub_category);
                var toAppend = ''
                toAppend += "<option value=''>Select Sub Category</option>"
                $.each(sub_category, function(i,o){
                    toAppend += '<option value='+o.id+'>'+o.text+'</option>';
                });
                $('#id_sub_category').append(toAppend);
            },
            failure : function(result){
            },
        });
    });
}

$(document).ready(function () {

 cat_value = $('#id_category').val();
 sub_cat_value = $('#id_sub_category').val();

 if(cat_value){

 category_auto_select1(cat_value,sub_cat_value)
 }

});
function category_auto_select1(value,sub_cat_value){

        $('#id_sub_category').select2({placeholder: 'Select Sub Category'});
        $("#id_sub_category").empty();

        $.ajax({
            type:'GET',
            url : '/dashboard/accounts/get-sub-category/',
            data : {
                category: value,
            },
            success : function(data){
                var sub_category = JSON.parse(data);
                $("#id_sub_category").select2('data', sub_category);
                var toAppend = ''
                toAppend += "<option value=''>Select Sub Category</option>"
                $.each(sub_category, function(i,o){
                    if(sub_cat_value == o.id)
                    {
                    toAppend +='<option value='+o.id+' selected>'+o.text+'</option>';
                    console.log("sub_cat_value"+sub_cat_value)
                    }
                    else{
                    toAppend += '<option value='+o.id+'>'+o.text+'</option>';
                    }
                });
                $('#id_sub_category').append(toAppend);
            },
            failure : function(result){
            },
        });

}


/* ------------------------------------------------  */
/* extra code */

/*

$(window).scroll(function() {
                var scroll = $(window).scrollTop();
                if (scroll >= 10){
                    $(".header-content").addClass("darkHeader");
                }
                else{
                    $(".header-content").removeClass("darkHeader");
                }

            });

*/