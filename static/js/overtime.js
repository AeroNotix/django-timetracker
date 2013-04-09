/*global $,window*/
function onchanger() {
	"use strict";
    if ($("#user_select").val() === "null") {
        return;
    }
    window.location.href = "/overtime/" + $("#user_select").val() + "/" + $("#cmb_yearbox").val() + "/";
}

$(function() {
    $("td").each(function () {
        $(this).click(function (e) {
            var formdata = {};
            if ($(this).hasClass("OVERTIME") ||
                $(this).hasClass("UNDERTIME")) {
                formdata = {
                    "form_type": "tracking_data",
                    "who": $("#hidden_ee").text(),
                    "entry_date": $(this).attr("entry_date")
                };
                $.ajax({
                    url: "/ajax/",
                    type: "POST",
                    data: formdata,
                    dataType: "json",
                    success: function (data) {
                        if (data.success === true) {
                            insert_comment(data);
                        }
                    }});
            }
        });
    });
})

function insert_comment(data) {
    $("#entry_data_field").html(
        ["<ul>",
         "<li>Entry Date: " + data.entry_date + "</li>",
         "<li>Start Time: " + data.start_time + "</li>",
         "<li>End Time: " + data.end_time + "</li>",
         "<li>DayType: " + data.daytype + "</li>",
         "<li>Length: " + data.length + "</li>",
         "<li>Linked Day: " + data.link + "</li>",
         "</ul>"].join(''));
}

$(function () {
	"use strict";
    $("#user_select").change(onchanger);
    $("#cmb_yearbox").change(onchanger);
    $("#cmb_yearbox").val($("#hidden_year").text());
    $("#user_select").val($("#hidden_ee").text());
});
