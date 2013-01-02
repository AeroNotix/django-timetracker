Client-side Javascript modules
==============================

Calendar Module
---------------

.. function:: ajaxCall(form)

Creates an ajax call depending on what called the function. Server-side there
is a view at domain/ajax/ which is designed to intercept all ajax calls.

The idea is that you define a function, add it to the ajax view's dict of
functions along with a tag denoting it's name, and then pass the string to
the 'form_type' json you sent to that view.

In this particular ajax request function we're pulling out form data
depending on what form calls the ajaxCall.

    :paramemter form: This argument is the string identifier of the form from
                      which you wish to send the data from. The possible
                      choices are the Add Form and the Change Form.
    :returns: This function returns false so that the form doesn't try to
              carry on with it's original function.

.. function:: onOptionChange(element)

Specific selections determine which elements of the form are disabled. For
example there is no need to allow people to change their working time for a
vacation day. Similarly, if they have previously selected a vacation day, then
we need to re-enable the form else they will no longer be able to enter the
time into the fields.

    :paramemter element: This argument is the string identifier of the form
                         from which you wish to send the data from. The
                         possible choices are the Add Form and the Change
                         Form.
    :returns: True. This always returns true to signify to any programmatic
              callers that we have finished the function. There are no error
              codes or errors thrown.
