var $ = $ || function() {}; // Keeps from throwing ref errors.
var CONFIG = {};

function swapselected(from, to) {
	$(to).html(options[$(from).val()]);
}

function detailselected(from, to) {
	$(to).text(details[$(from).val()]);
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

    $("#which-date").change(
        function() {
            $.ajax({
                method: "GET",
                url: CONFIG.AJAX_ENTRIES_URL,
                data: {
                    "date": $("#which-date").val()
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
                                           "</td><td><input value=\"",
                                           data.entries[i].amount,
                                           "\"/></td></tr>"].join(""));
                    }
                    $("#entries").find("input").each(function() {
                        $(this).spinner({spin:
                                         function () {
                                             console.log("sup");
                                             console.log($(this).id);
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
        });

    $(function() {
        $("#amount-box").spinner({"min": 0});
        $("#which-date").datepicker().datepicker("option", "dateFormat", "yy-mm-dd");
        $("#which-date").datepicker("setDate", "{{ todays_date}}");
    });
});
