function onchanger() {
    window.location.href = "/yearview/" + $("#user_select").val() + "/" + $("#cmb_yearbox").val() + "/";
}

$(function() {
    $("#user_select").change(onchanger);
    $("#cmb_yearbox").change(onchanger);
    $("#cmb_yearbox").val($("#hidden_year").text());
});