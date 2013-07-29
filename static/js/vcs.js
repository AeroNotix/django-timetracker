var $ = $ || function() {}; // Keeps from throwing ref errors.
var CONFIG = {};

function swapselected(from, to) {
	$(to).html(options[$(from).val()]);
}

function detailselected(from, to) {
	$(to).text(details[$(from).val()]);
}

function updateentry(which, value) {
    $.ajax({
        method: "POST",
        url: CONFIG.AJAX_UPDATE_URL,
        async: false, // to prevent multiple in-flight requests.
        data: {
            volume: value(),
            id: which.substring("entry_".length, which.length)
        },
        success: function() {
            if (value() == 0) {
                location.reload(false);
            }
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
                // Store a reference to this so that future
                // invocations of the dynamically created functions
                // are able to use the old `this`.
                var el = this;
                $(el).spinner(
                    {
                        spin: function (event, ui) {
                            updateentry($(el).attr("id"), function() {
                                return ui.value;
                            });
                        },
                        min: 0
                    });
                // We create a function which can be ran at
                // the right time since there are many objects
                // which can call the updateentry function and
                // their bindings are generated dynamically so
                // the objects which they reference need to be
                // closed over in a closure.
                $(el).change(function () {
                    updateentry($(el).attr("id"), function() {
                        return $(el).val();
                    });
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
