$("#team, #year, #month").change(function() {
    window.location.assign(window.location.origin
                           + window.location.pathname
                           + "?team="+$("#team").val()
                           + "&year="+$("#year").val()
                           + "&month="+$("#month").val());
});
