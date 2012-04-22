function onOptionChange() {
    /* 
       When the select box is changed the form needs to 
       be updated with the employees data, so we grab the
       value and make an ajax request to the database to
       pull the data

       Returns undefined and takes no parameters
    */
    "use strict";

    $.ajaxSetup({type: 'POST'});

    var user_id = $("#user_select").val();
    $.ajax({
        url: '/ajax/',
        dataType: "json",
        data: {
            'user_id': user_id,
            'form_type': 'get_user_data'
        },

        success: function (data) {
            $("#id_user_id").val(data.username);
            $("#id_firstname").val(data.firstname);
            $("#id_lastname").val(data.lastname);
            $("#id_market").val(data.market);
            $("#id_process").val(data.process);
            $("#id_start_date").val(data.start_date);
            $("#id_breaklength").val(data.breaklength);
            $("#id_shiftlength").val(data.shiftlength);

        }
    }
          );
}

$(function () {
    "use strict";

    $("#user_select").attr("onchange", "onOptionChange()");
    onOptionChange();
});