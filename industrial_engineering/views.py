from django.http import HttpResponse

from timetracker.utils.decorators import permissions

@permissions(["INENG"])
def reporting(request):
    return HttpResponse("What up dawg")
