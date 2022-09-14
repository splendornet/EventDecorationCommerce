/* JS File. */

function promotion(user, user_id){
    if(user == 'True'){
        $('#offer_modal').modal('show');
        $.ajax({
            type:'GET',
            url : '/update_first_login/',
            data : {
                user_id: user_id
            },
            success : function(data){
                console.log('<--------------------- data ----------------------------->')
                console.log(data)
                console.log('<--------------------- data ----------------------------->')
            },
            failure : function(data){

            },
        });
    }
}