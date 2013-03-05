'''Exception handling middleware.'''

from django.http import Http404, UnreadablePostError

class UnreadablePostErrorMiddleware(object):
    '''An UnreadablePostError is raised when a POST is aborted part-way
    through. The problem is that it's actually a WSGI error and not a
    Django one. So we can't *really* wrap every view in a try/catch (
    nor would we want to.'''
    def process_exception(self, request, exception):
        '''Catch exceptions.'''
        if isinstance(exception, UnreadablePostError):
            raise Http404
        return None
