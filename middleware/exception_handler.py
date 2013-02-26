from django.http import Http404, UnreadablePostError

class UnreadablePostErrorMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, UnreadablePostError):
            raise Http404
        return None
