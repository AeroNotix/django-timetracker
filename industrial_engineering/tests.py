import unittest
import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from timetracker.tests.basetests import create_users, delete_users, login
from timetracker.tracker.models import Tbluser


def cbt(cls, who, code, params={}):
    login(cls, who)
    response = cls.client.get(reverse("timetracker.industrial_engineering.views.costbuckets"), params)
    cls.assertEqual(response.status_code, code)

def utt(cls, who, code, params={}):
    login(cls, who)
    response = cls.client.get(reverse("timetracker.industrial_engineering.views.utilization"), params)
    cls.assertEqual(response.status_code, code)

class BaseIndustrialEngineeringTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        create_users(self)
        self.indeng = Tbluser.objects.create(
            user_id="indeng@test.com",
            firstname="test",
            lastname="case",
            password="password",
            salt="nothing",
            user_type="INENG",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="07:45:00",
            job_code="00F20G",
            holiday_balance=20
        )
        self.indeng.full_clean()
        self.indeng.update_password(self.indeng.password)
        self.indeng.save()
        super(BaseIndustrialEngineeringTestCase, self).setUp()

    def tearDown(self):
        delete_users(self)
        super(BaseIndustrialEngineeringTestCase, self).tearDown()


class PermissionTest(BaseIndustrialEngineeringTestCase):

    def test_costbucket_manager(self):
        cbt(self, self.linked_manager, 404)

    def test_costbucket_user(self):
        cbt(self, self.linked_user, 404)

    def test_costbucket_tl(self):
        cbt(self, self.linked_teamlead, 404)

    def test_costbucket_ineng(self):
        cbt(self, self.indeng, 200)

    def test_utilization_manager(self):
        utt(self, self.linked_manager, 200)

    def test_utilization_user(self):
        utt(self, self.linked_user, 404)

    def test_utilization_tl(self):
        utt(self, self.linked_teamlead, 404)

    def test_utilization_ineng(self):
        utt(self, self.indeng, 200)


class TestQueryOptions(BaseIndustrialEngineeringTestCase):

    def test_yearmonth_cbb(self):
        cbt(self, self.indeng, 200, params={"year": "2012", "month": "7"})

    def test_yearmonth_utt(self):
        utt(self, self.indeng, 200, params={"year": "2012", "month": "7"})

    def test_cbt_with_team(self):
        cbt(self, self.indeng, 200, params={"year": "2012", "month": "7", "team": "CZ"})

    def test_fail_utt(self):
        utt(self, self.indeng, 404, params={"year": "banana", "month": "banana"})

    def test_utt_with_team(self):
        utt(self, self.indeng, 200, params={"year": "2012", "month": "7", "team": "CZ"})

    def test_yearmonth_with_invalid_team(self):
        utt(self, self.indeng, 404, params={"year": "2012", "month": "7", "team": "banana"})
