function onOptionChange() {
    /* 
       When the select box is changed the form needs to 
       be updated with the employees data, so we grab the
       value and make an ajax request to the database to
       pull the data

       Returns undefined and takes no parameters
    */
    
    var user_id = $("#user_select").val();
    alert(user_id);
}

$(function () {
    $("#user_select").attr("onchange", "onOptionChange()");
    onOptionChange();
});