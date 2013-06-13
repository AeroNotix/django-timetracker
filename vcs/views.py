import datetime
import os
import imp

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from timetracker.utils.decorators import loggedin, json_response
from timetracker.vcs.models import ActivityEntry, Activity
from timetracker.tracker.models import Tbluser

@loggedin
def vcs(request):
    user = request.session.get("user_id")
    user = Tbluser.objects.get(id=user)
    return render_to_response(
        "vcs.html",
        {
            "todays_date": datetime.datetime.today().strftime("mm-dd-yyyy"),
            "plugin_list": filter(
                lambda p: user.market in p["accounts"],
                listplugins(settings.PLUGIN_DIRECTORY),
            )
        },
        RequestContext(request)
    )

@loggedin
def vcs_add(request):
    activity_key = request.POST.get("activity_key")
    amount = request.POST.get("amount")
    date = request.POST.get("date")
    user_id = request.session.get("user_id")

    if not all([date, user_id, activity_key, amount]):
        raise Http404

    activity = Activity.objects.get(id=activity_key)
    user = Tbluser.objects.get(id=user_id)
    ActivityEntry(user=user, activity=activity, amount=amount, creation_date=date).save()

    return render_to_response(
        "vcs.html",
        {},
        RequestContext(request)
    )

@loggedin
@json_response
def entries(request):
    user_id = request.session.get("user_id")
    user = Tbluser.objects.get(id=user_id)
    date = request.GET.get("date")
    if not date:
        raise Http404
    entries = ActivityEntry.objects.filter(creation_date=date)
    if not len(entries):
        raise Http404
    return {"entries": map(serialize_activityentry, entries)}

@loggedin
@json_response
def update(request):
    '''Update is the handler for when an ActivityEntry is to be updated by
    the front-end. We're simply changing the Volume field on the
    ActivityEntry.
    '''

    volume = request.POST.get("volume")
    entryid = request.POST.get("id")
    if not volume or not entryid:
        raise Http404
    entry = ActivityEntry.objects.get(id=entryid)
    entry.amount = int(volume)
    entry.save()
    return {"success": True}

def serialize_activityentry(entry):

    '''Serializes a single ActivityEntry into a JSON format.'''
    return {
        "id": entry.id,
        "date": str(entry.creation_date),
        "text": entry.activity.groupdetail,
        "amount": int(entry.amount)
    }

def listplugins(directory):
    '''Iterates through the passed-in directory, looking for raw Python
    modules to import, when it imports the modules we specifically
    look for several module-level attributes of which we make no
    error-checking to see if they are there or not.

    We check no errors since this will be a very early warning trigger
    if there is a programmatic warning.

    :param directory: :class:`str`, the name of the directory to
                      search for plugins.

    :return: List of dictionaries containing both the module and the
             module-level attributes for that module.
    '''

    plugins = []
    for f in os.listdir(directory):
        # ignore irrelevant files and compiled python modules.
        if f == "__init__.py" or f.endswith(".pyc"):
            continue
        g = f.replace(".py", "")
        info = imp.find_module(g, [directory])
        # dynamically import our module and extrapolate the callback
        # along with the attributes.
        m = imp.load_module(g, *info)
        plugins.append({
            "name": m.PLUGIN_NAME,
            "accounts": m.ACCOUNTS,
            "callback": getattr(m, m.CALLBACK),
            "module": m,
        })
    return plugins
