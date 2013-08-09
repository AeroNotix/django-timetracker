import datetime
import simplejson
from decimal import Decimal

from django.http import Http404, HttpResponseRedirect
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from timetracker.utils.datemaps import MARKET_CHOICES_LIST

from timetracker.tests.basetests import create_users, delete_users, login
from timetracker.vcs.models import Activity, ActivityEntry
from timetracker.vcs.activities import createuseractivities
from timetracker.vcs.views import vcs_add, update

from timetracker.tracker.models import Tbluser


class BaseVCS(TestCase):
    class Req:
        pass
    req = Req()

    def setUp(self):
        self.req.session = {
            "user_id": self.linked_user.id
        }

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        create_users(cls)
        createuseractivities()

    @classmethod
    def tearDownClass(cls):
        delete_users(cls)
        Activity.objects.all().delete()


class VCSAddTestCase(BaseVCS):

    def test_add_entry(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": "100",
            "date": "2012-01-01",
        }
        self.assertIsInstance(vcs_add(self.req), HttpResponseRedirect)

    def test_add_entry_no_date(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": "100",
        }
        self.assertRaises(Http404, vcs_add, self.req)

    def test_add_entry_no_amount(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "date": "2012-01-01",
        }
        self.assertRaises(Http404, vcs_add, self.req)

    def test_add_entry_no_activity(self):
        self.req.POST = {
            "date": "2012-01-01",
            "amount": "100",
        }
        self.assertRaises(Http404, vcs_add, self.req)


class VCSUpdateTestCase(BaseVCS):

    def test_update_entry(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": 100,
            "date": "2012-01-01",
        }
        vcs_add(self.req)
        self.req.POST = {
            "volume": 1,
            "id": str(ActivityEntry.objects.all()[0].id)
        }
        entry = ActivityEntry.objects.all()[0]
        prevol = entry.amount
        id = entry.id
        update(self.req)
        self.assertEqual(ActivityEntry.objects.get(id=id).amount, 1)

    def test_update_delete(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": 100,
            "date": "2012-01-01",
        }
        vcs_add(self.req)
        self.req.POST = {
            "id": str(ActivityEntry.objects.all()[0].id),
            "volume": "0",
        }
        entry_id = ActivityEntry.objects.all()[0].id
        update(self.req)
        self.assertEqual(ActivityEntry.objects.filter(id=entry_id).count(), 0)

    def test_update_fail_no_volume(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": 100,
            "date": "2012-01-01",
        }
        vcs_add(self.req)
        self.req.POST = {
            "id": str(ActivityEntry.objects.all()[0].id)
        }
        self.assertRaises(Http404, update, self.req)

    def test_update_fail_no_id(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": 100,
            "date": "2012-01-01",
        }
        vcs_add(self.req)
        self.req.POST = {
            "volume": 1,
        }
        self.assertRaises(Http404, update, self.req)

    def test_update_fail_no_data(self):
        self.req.POST = {
            "activity_key": str(Activity.objects.all()[0].id),
            "amount": 100,
            "date": "2012-01-01",
        }
        vcs_add(self.req)
        self.req.POST = {}
        self.assertRaises(Http404, update, self.req)


class VCSActivityEntryTestCase(BaseVCS):

    def test_filterforyearmonth(self):
        td = datetime.timedelta(days=999)
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today() + td
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today() + td
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today() + td
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today() + td
        ).save()
        entries, _ = ActivityEntry.filterforyearmonth(
            [self.linked_user.market],
            year=(datetime.datetime.today() + td).year,
            month=(datetime.datetime.today() + td).month
        )
        self.assertEqual(4, entries.count())

    def test_filternoyearmonth(self):
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        entries, _ = ActivityEntry.filterforyearmonth([self.linked_user.market])
        self.assertEqual(4, entries.count())

    def test_costbucket_count(self):
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        self.assertEquals(ActivityEntry.costbucket_count(MARKET_CHOICES_LIST)[''], 4)

    def test_utilization(self):
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        ActivityEntry.objects.create(
            user=self.linked_user,
            activity=Activity.objects.all()[0],
            amount=1,
            creation_date=datetime.datetime.today()
        ).save()
        self.assertEquals(ActivityEntry.utilization_calculation(MARKET_CHOICES_LIST),
                          {
                              'util': {
                                  'percent': Decimal('0.005553525758129338691998538546'),
                                  'target': 65
                              },
                              'effi': {
                                  'percent': Decimal('0.005553525758129338691998538546'),
                                  'target': 85
                              },
                              'avai': {
                                  'percent': Decimal('100'),
                                  'target': 80
                              },
                              'FTE': 1
                          })

class VCSFrontEndTestCase(BaseVCS):
      def test_activityfailure_noid(self):
          user = Tbluser.objects.all()[0]
          login(self, user)
          response = self.client.post(reverse("timetracker.vcs.views.update"), {"volume": 1, "id": -1})
          self.assertEquals(response.status_code, 200)
          self.assertEquals(simplejson.loads(response.content), {"success": False})