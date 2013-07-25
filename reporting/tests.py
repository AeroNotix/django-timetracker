from django.test import TestCase
from django.http import Http404

from timetracker.reporting.views import all_team

class PermissionTest(TestCase):
    def testPermissionNoUser(self):
        class Req:
            session = {"user_id": 31337}
        self.assertRaises(Http404, all_team, Req())
