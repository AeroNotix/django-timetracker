/* 
   Functions to deal with the client-side
   actions of the administrator view
*/

function onOptionChange(date) {
    $.ajaxSetup({type: 'POST'});

    var eeid = $("#user_select").val();

    $.ajax({
        url: "/ajax/",
        data: {
            'form_type': 'admin_get',
            'eeid': eeid
        },
        dataType: "json",
        success: function (data) {
            alert(data);
        }
    });
}
    
    