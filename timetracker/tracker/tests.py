"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import unittest
import datetime
from timetracker.tracker.models import (Tbluser,
                                        TrackingEntry,
                                        Tblauthorization)
from timetracker.utils.calendar_utils import validate_time, parse_time
from timetracker.utils.datemaps import pad, float_to_time, generate_select

class UserModelTest(unittest.TestCase):

    def setUp(self):
        self.manager = Tbluser.objects.create(
            user_id="test.manager@test.com",
            firstname="test",
            lastname="case",
            password="password",
            user_type="ADMIN",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
        )

        self.user = Tbluser.objects.create(
            user_id="test.user@test.com",
            firstname="test",
            lastname="case",
            password="password",
            user_type="RUSER",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
        )

    def tearDown(self):
        self.manager.delete()
        self.user.delete()

    def testIsAdmin(self):
        self.assertEquals(self.manager.is_admin(), True)
        self.assertNotEquals(self.manager.is_admin(), False)
        self.assertEquals(self.user.is_admin(), False)
        self.assertNotEquals(self.user.is_admin(), True)

    def testName(self):
        self.assertEquals(self.user.name(), "test case")
        self.assertEquals(self.manager.name(), "test case")

    def testUserType(self):
        self.assertEquals(self.manager.display_user_type(), "ADMIN")
        self.assertEquals(self.user.display_user_type(), "RUSER")

class UtilitiesTest(unittest.TestCase):
    def testValidateTime(self):
        self.assertEquals(validate_time("00:00", "00:01"), True)
        self.assertEquals(validate_time("00:00", "23:00"), True)
        self.assertEquals(validate_time("00:00", "00:00"), False)
        self.assertEquals(validate_time("23:00", "00:00"), False)
        self.assertEquals(validate_time("00:01", "00:00"), False)

    def testPaseTime(self):
        self.assertEquals(parse_time("00:01"), [0,1])
        self.assertEquals(parse_time("23:57"), [23,57])
        self.assertEquals(parse_time("12:12"), [12,12])

    def testPad(self):
        self.assertEquals(pad("teststring"), "teststring")
        self.assertEquals(pad("t"), "0t")
        self.assertEquals(pad("teststring", amount=20),
                          "0000000000teststring")
        self.assertEquals(pad("teststring", padchr='1', amount=20),
                          "1111111111teststring")
        self.assertEquals(pad("t", padchr="1" ),
                          "1t")

    def testFloat_to_time(self):
        self.assertEquals(float_to_time(0.1), "00:06")
        self.assertEquals(float_to_time(0.2), "00:12")
        self.assertEquals(float_to_time(0.3), "00:18")
        self.assertEquals(float_to_time(0.4), "00:24")
        self.assertEquals(float_to_time(0.5), "00:30")
        self.assertEquals(float_to_time(1.0), "01:00")
        self.assertEquals(float_to_time(5.0), "05:00")

    def testGenerateSelect(self):

        output = generate_select((
            ('val1', 'Value One'),
            ('val2', 'Value Two'),
            ('val3', 'Value Three')
        ))

        string = '''<select id="">
\t<option value="val1">Value One</option>
\t<option value="val2">Value Two</option>
\t<option value="val3">Value Three</option>
</select>'''
        self.assertEquals(output, string)
