var $ = $ || function() {}; // Keeps from throwing ref errors.

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

});
