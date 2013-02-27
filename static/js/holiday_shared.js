var previous = 0;
var previous_css = '';
function highlight_row(Row) {
    if (previous) {
        $("#" + previous + "_row").css({
            "border": previous_css
        });
        /* We need to trigger a redraw because WebKit browsers sometimes
           fail to flush the layout changes. */
        $("#" + previous + "_row").hide(0, function() {
            $("#" + previous + "_row").show();
        });
    }
    previous_css  = $("#" + Row + "_row").css("border");
    $("#" + Row + "_row").css({
        "border": "3px solid black"
    });
    previous = Row;
}
