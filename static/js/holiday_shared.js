var previous = 0;
function highlight_row(Row) {
    if (previous) {
        $("#" + previous + "_row").removeClass("highlighted-row")
        /* We need to trigger a redraw because WebKit browsers sometimes
           fail to flush the layout changes. */
        $("#" + previous + "_row").hide(0, function() {
            $("#" + previous + "_row").show();
        });
    }
    $("#" + Row + "_row").addClass("highlighted-row");
    previous = Row;
}
