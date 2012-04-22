/*
  all functions dealing with the calendar that aren't
  automatically created server-side.
*/


function ajaxCall(form) {
    /*
      Creates an ajax call depending on what
      called the function.
      
      Server-side there is a view at domain/ajax/
      which is designed to intercept all ajax
      calls.
      
      The idea is that you define a function,
      add it to the ajax view's dict of functions
      along with a tag denoting it's name, and
      then pass the string to the 'form_type'
      json you sent to that view.
      
      In this particular ajax request function
      we're pulling out form data depending on
      what form calls the ajaxCall
    */

    "use strict";

    $.ajaxSetup({type: 'POST'});
    
    var pre = '';

    if (form === "delete") {
        pre = "#change_";
    } else {
        pre = "#" + form + "_";
    }

    var formData = {
        "form_type" : form,
        "entry_date" : $(pre + 'entrydate').val(),
        "start_time" : $(pre + 'starttime').val(),
        "end_time" : $(pre + 'endtime').val(),
        "daytype" : $(pre + 'daytype').val(),
        "hidden-id" : $('#hidden_id').val()
    };

    // no point in making invalid ajax requests
    if (!formData.entry_date || !formData.start_time || !formData.end_time) {
        return false;
    }

    $.ajax({
        url: "/ajax/",
        data: formData,
        dataType: "json",
        success: function (data) {
            if (data.success === true) {
                $("#calendar-entry").fadeToggle("slow", function() {
                          $("#calendar-entry").html(data.calendar);
                });
                $("#calendar-entry").fadeToggle("slow");
            } else {
                alert(data.error);
            }
        }
    }
          );
    
    return false; // so the form doesn't do it's regular action
}

function onOptionChange(element) {

    /*
      When specific options are selected
      there is no need to give working times
      considering that the person wasn't at
      work
    */

    "use strict";

    var pre = "#" + element + "_";
    var optionBox = pre + "daytype";
   
    if ($(optionBox).val() === "SICKD" ||
        $(optionBox).val() === "HOLIS") {

        $(pre + "starttime").val('00:00');
        $(pre + "endtime").val('00:01');
        
        // disable the boxes because there's no need to
        // use them since we've put the values in for them
        $(pre + "starttime").attr("disabled", "disabled");
        $(pre + "endtime").attr("disabled", "disabled");
    } else {
        // otherwise, we clear the box in case the values
        // were filled previously
        $(pre + "starttime").val('');
        $(pre + "endtime").val('');

        // and remove the disabled attribute
        $(pre + "starttime").removeAttr("disabled");
        $(pre + "endtime").removeAttr("disabled");
    }

}


function addTimePicker(element, state) {
    
    /*
adds a jQuery TimePicker to `element`
with an initial state of `state`.
this is an impure function and returns
undefined.
*/

    "use strict";
    
    $(element).timepicker({});
    $(element).val('');
    
    if (!state) {
        $(element).timepicker("disable");
    }

}

function addDatePicker(element, state) {
    
    /*
      adds a jQuery datePicker to `element`
      with an initial state of `state`.
      this is an impoure function and returns
      undefined.
    */

    "use strict";

    $(element).datepicker().val('');
    $(element).datepicker("option", "dateFormat", 'yy-mm-dd');
    
    if (!state) {
        $(element).datepicker("disable");
    }

}

$(function () {

    /*
      jQuery onload function which adds a
      few widgets to the page along with
      their initial state.
    */

    "use strict";

    addTimePicker("#change_starttime", false);
    addTimePicker("#change_endtime", false);
    addTimePicker("#add_starttime", true);
    addTimePicker("#add_endtime", true);
    addDatePicker("#change_entrydate", false);
    addDatePicker("#add_entrydate", true);
    $("#add_daytype").attr("onchange", "onOptionChange('add')");
    $("#change_daytype").attr("onchange", "onOptionChange('change')");
    onOptionChange('add');
    onOptionChange('change');
});

function deleteEntry() {
    
    /*
      Deletes a calendar entry
    */

    "use strict";

    var answer = confirm("Are you sure?");
    if (answer) {
        return ajaxCall("delete");
    } else {
        return false;
    }
}

function toggleChangeEntries(st_hour, st_min, full_st,
                             fi_hour, fi_min, full_fi,
                             entry_date, daytype,
                             change_id) {

    /*
      When an entry is clicked, it will fill out the
      change form so that the user can enter a new
      set of information instead.
    */
    
    "use strict";
    
    // change the ID field
    $("#hidden_id").val(change_id);
  
    // if we've previously clicked an empty cell
    // the add_entry date will have a date in it
    $("#add_entrydate").val('');
    
    // re-enable the form and enter the times
    $("#change_starttime").timepicker("enable");
    $("#change_endtime").timepicker("enable");
    $("#change_entrydate").val(entry_date);
    $("#change_daytype").val(daytype);
    $("#change_starttime").timepicker("destroy");
    $("#change_endtime").timepicker("destroy");
    
    $("#change_starttime").timepicker({
        hour: st_hour,
        minute: st_min
    });

    $("#change_endtime").timepicker({
        hour: fi_hour,
        minute: fi_min
    });
    
    // it seems programmatically changing the option box
    // doesn't fire the signal, so we just fire it ourselves
    onOptionChange("change");

    // zero out the add form
    $("#add_starttime").val('');
    $("#add_endtime").val('');
    
    // put the dates into the change boxes
    $("#change_starttime").val(full_st);
    $("#change_endtime").val(full_fi);

}

function hideEntries(date) {
    $("#add_entrydate").val(date);
    $("#change_starttime").val('');
    $("#change_entrydate").val('');
    $("#change_endtime").val('');
    $("#add_starttime").val('');
    $("#add_endtime").val('');
    
    $("#add_starttime").timepicker("destroy");
    $("#add_endtime").timepicker("destroy");

    $("#add_starttime").timepicker({
        hour: 0,
        minute: 0
    });

    $("#add_endtime").timepicker({
        hour: 0,
        minute: 0
    });

}

