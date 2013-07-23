var $ = $ || function() {}; // Keeps from throwing ref errors.
var CONFIG = {};

function swapselected(from, to) {
	$(to).html(options[$(from).val()]);
}

function detailselected(from, to) {
	$(to).text(details[$(from).val()]);
}

function updateentry(which, ui) {
    $.ajax({
        method: "POST",
        url: CONFIG.AJAX_UPDATE_URL,
        async: false, // to prevent multiple in-flight requests.
        data: {
            volume: ui.value,
            id: which.substring("entry_".length, which.length)
        }
    });
}

$(function() {
	$("#grp-slct").change(
		function() {
			swapselected("#grp-slct", "#subgrp-slct");
		});
	$("#subgrp-slct").change(
		function() {
			detailselected("#subgrp-slct", "#detail-msg");
			$("#activity_key").attr("value", $("#subgrp-slct").val());
		});

    $("#which-date").change(populatetable);
    $("#amount-box").spinner({"min": 0});
    $("#which-date").datepicker().datepicker("option", "dateFormat", "yy-mm-dd");
    $("#which-date").datepicker("setDate", "{{ todays_date}}");
    $("#plugin_select").change(selectprocessor);
    selectprocessor();
});

function selectprocessor() {
    $("#plugin_processor").attr("value", $("#plugin_select").val());
}

function populatetable() {
    $.ajax({
        method: "GET",
        url: CONFIG.AJAX_ENTRIES_URL,
        data: {
            date: $("#which-date").val()
        },
        success: function (data) {
            var i;
            $("#entries")
                .children()
                .remove();
            $("#entries").append("<th>Type</th><th>Amount</th>");
            for (i = 0; i < data.entries.length; i++) {
                $("#entries").append(["<tr><td>",
                                      data.entries[i].text,
                                      "</td><td><input id=\"entry_",
                                      data.entries[i].id,
                                      "\" ",
                                      "value=\"",
                                      data.entries[i].amount,
                                      "\"/></td></tr>"].join(""));
            }
            $("#entries").find("input").each(function() {
                $(this).spinner({spin:
                                 function (event, ui) {
                                     updateentry($(this).attr("id"), ui);
                                 },
                                 min: 0
                                });
            });
        },
        error: function (a,b,c) {
            $("#entries")
                .children()
                .remove();
        }
    });
}

$(function() {
    populatetable();
})
