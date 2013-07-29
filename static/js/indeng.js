$("#team, #year, #month").change(function() {
    var pattern = new RegExp(/\d+/g);
    if (!pattern.test($("#year").val())) {
        alert("Year value is not a number.");
        return;
    }
    window.location.assign(window.location.origin
                           + window.location.pathname
                           + "?team="+$("#team").val()
                           + "&year="+$("#year").val()
                           + "&month="+$("#month").val());
});
