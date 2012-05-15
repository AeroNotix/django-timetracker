"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime
import simplejson
import random

from django.test import TestCase
from django.http import HttpResponse, Http404

from timetracker.tracker.models import (Tbluser,
                                        TrackingEntry,
                                        Tblauthorization)
from timetracker.utils.calendar_utils import (validate_time, parse_time,
                                              delete_user, useredit,
                                              mass_holidays, ajax_delete_entry,
                                              gen_calendar, ajax_change_entry,
                                              ajax_error)
from timetracker.utils.datemaps import pad, float_to_time, generate_select, ABSENT_CHOICES

class BaseUserTest(TestCase):

    def setUp(self):

        # we create users which will be linked,
        # to test how the automatic retrieval
        # of the links works
        self.linked_manager = Tbluser.objects.create(
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

        self.linked_user = Tbluser.objects.create(
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

        self.linked_teamlead = Tbluser.objects.create(
            user_id="test.teamlead@test.com",
            firstname="test",
            lastname="case",
            password="password",
            user_type="TEAML",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
        )

        # create the links for the linked users
        self.authorization = Tblauthorization.objects.create(admin=self.linked_manager)
        self.authorization.save()
        self.authorization.users.add(self.linked_user, self.linked_teamlead)
        self.authorization.save()

        self.unlinked_manager = Tbluser.objects.create(
            user_id="test.unlinkedmanager@test.com",
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

        self.unlinked_user = Tbluser.objects.create(
            user_id="test.unlinkeduser@test.com",
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

        self.unlinked_teamlead = Tbluser.objects.create(
            user_id="test.unlinkedteamlead@test.com",
            firstname="test",
            lastname="case",
            password="password",
            user_type="TEAML",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
        )

        # create a new_user dict to share among tests
        self.new_user = {
            'mode': "false",
            'user_id': "new_test@user.com",
            'firstname': "New",
            'lastname': "Test",
            'user_type': "RUSER",
            'market': "BK",
            'process': "AR",
            'start_date': "2012-01-01",
            'breaklength': "00:15:00",
            'shiftlength': "08:00:00",
            'job_code': "ABCDE",
            'holiday_balance': 20
        }

        # create some random holiday data
        holidays = {}
        holidays_empty = {}
        for day in range(1, 32):
            holidays[day] = random.choice(ABSENT_CHOICES)[0]
            holidays[day] = "empty"
        self.holiday_data = simplejson.dumps(holidays)
        self.holiday_data_empty = simplejson.dumps(holidays_empty)

        class Request(object):
            def __init__(self, model_id):
                self.session = {
                    'user_id': model_id
                    }

                self.POST = {}


            def is_ajax(self):
                return True

        self.linked_manager_request = Request(self.linked_manager.id)
        self.linked_teamlead_request = Request(self.linked_teamlead.id)
        self.linked_user_request = Request(self.linked_user.id)
        self.unlinked_manager_request = Request(self.unlinked_manager.id)
        self.unlinked_teamlead_request = Request(self.unlinked_teamlead.id)
        self.unlinked_user_request = Request(self.unlinked_user.id)

    def tearDown(self):
        del(self.linked_manager_request)
        [user.delete() for user in Tbluser.objects.all()]
        [holiday.delete() for holiday in TrackingEntry.objects.all()]

class UserTestCase(BaseUserTest):
    '''
    Tests the methods attached to user instances
    '''

    def testIsAdmin(self):
        '''
        Only managers and team leaders are admins
        '''
        self.assertEquals(self.linked_manager.is_admin(), True)
        self.assertNotEquals(self.linked_manager.is_admin(), False)
        self.assertEquals(self.linked_user.is_admin(), False)
        self.assertNotEquals(self.linked_user.is_admin(), True)

    def testName(self):
        '''
        Should return the full name
        '''
        self.assertEquals(self.linked_user.name(), "test case")
        self.assertEquals(self.linked_manager.name(), "test case")

    def testUserType(self):
        '''
        Make sure our types return what we set them up as
        '''
        self.assertEquals(self.linked_manager.display_user_type(), "ADMIN")
        self.assertEquals(self.linked_user.display_user_type(), "RUSER")

    def testHolidayBalance(self):
        '''
        Test to make sure that the holiday balance calculates correctly
        '''
        for day in (("1", "HOLIS"), ("2", "PUWRK"), ("3", "RETRN")):
            entry = TrackingEntry(
                entry_date="2012-01-%s" % day[0],
                user_id=self.linked_user.id,
                start_time="00:00:00",
                end_time="00:00:00",
                breaks="00:00:00",
                daytype=day[1],
            )
            entry.save()

        self.assertEquals(self.linked_user.get_holiday_balance(2012), 20)

        for day in (("1", "HOLIS"), ("2", "HOLIS"), ("3", "HOLIS")):
            entry = TrackingEntry(
                entry_date="2012-01-%s" % day[0],
                user_id=self.linked_user.id,
                start_time="00:00:00",
                end_time="00:00:00",
                breaks="00:00:00",
                daytype=day[1],
            )
            entry.save()
            
        self.assertEquals(self.linked_user.get_holiday_balance(2012), 26)


class AjaxTestCase(BaseUserTest):

    def testValidDeleteUserViaManager(self):
        '''
        Tests a valid delete from a manager
        '''
        self.linked_manager_request.POST['user_id'] = self.linked_user.id
        valid = delete_user(self.linked_manager_request)
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ""})
        self.assertEquals(valid.content, json)

    def testValidDeleteUserViaTeamLeader(self):
        '''
        Tests a valid delete from a teamleader
        '''

        self.linked_teamlead_request.POST['user_id'] = self.linked_user.id
        valid = delete_user(self.linked_teamlead_request)
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ""})
        self.assertEquals(valid.content, json)

    def testInvalidDeleteUser(self):
        '''
        Tests an invalid delete
        '''
        # invalid delete
        self.linked_manager_request.POST['user_id'] = 999
        invalid = delete_user(self.linked_manager_request)
        self.assertIsInstance(invalid, HttpResponse)
        json = simplejson.dumps({'success': False, 'error': "User does not exist"})
        self.assertEquals(invalid.content, json)

    def testValidAddUserViaLinkedManager(self):
        '''
        Tests the ajax add user function for a hopefully valid add
        '''

        # create the post
        self.linked_manager_request.POST = self.new_user

        # test the addition of the user and the response
        valid = useredit(self.linked_manager_request)

        # test if the user is in the database
        # if this fails, this signifies our saving mechanism
        # is borked
        test_user = Tbluser.objects.filter(user_id="new_test@user.com")

        # test if the tblauthorization has been setup
        # if this fails, this signifies our tblauth creation
        # is borked
        tblauth = Tblauthorization.objects.filter(admin=self.linked_manager.id)

        # assert the return codes
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ''})
        self.assertEquals(valid.content, json)

    def testValidAddUserViaUnLinkedManager(self):
        '''
        Tests the ajax add user function for a hopefully valid add
        '''

        # create the post
        self.unlinked_manager_request.POST = self.new_user

        # test the addition of the user and the response
        valid = useredit(self.unlinked_manager_request)

        # test if the user is in the database
        # if this fails, this signifies our saving mechanism
        # is borked
        test_user = Tbluser.objects.filter(user_id="new_test@user.com")

        # test if the tblauthorization has been setup
        # if this fails, this signifies our tblauth creation
        # is borked
        tblauth = Tblauthorization.objects.filter(admin=self.unlinked_manager.id)

        # assert the return codes
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ''})
        self.assertEquals(valid.content, json)

    def testValidAddMassHolidaysManager(self):

        # create the post
        self.linked_manager_request.POST = {
            'form_data': 'mass_holiday',
            'user_id': self.linked_user.id,
            'year': '2012',
            'month': '1',
            'holiday_data': self.holiday_data
            }

        # the first time should be a virgin entry
        valid = mass_holidays(self.linked_manager_request)
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ''})
        self.assertEquals(valid.content, json)

        self.linked_manager_request.POST = {
            'form_data': 'mass_holiday',
            'user_id': self.linked_user.id,
            'year': '2012',
            'month': '1',
            'holiday_data': self.holiday_data_empty
            }

        # the 2nd time should still work, but silently pass
        valid = mass_holidays(self.linked_manager_request)
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ''})
        self.assertEquals(valid.content, json)

        # create the post
        self.linked_manager_request.POST = {
            'form_data': 'mass_holiday',
            'user_id': self.linked_user.id,
            'year': '2012',
            'month': '1',
            'holiday_data': self.holiday_data
            }

        # the last time
        valid = mass_holidays(self.linked_manager_request)
        self.assertIsInstance(valid, HttpResponse)
        json = simplejson.dumps({'success': True, 'error': ''})
        self.assertEquals(valid.content, json)

    def testValidAjaxDeleteHolidayEntry(self):

        # create the entry we want to delete
        TrackingEntry(entry_date="2012-01-01", user_id=self.linked_user.id)

        # create the post
        self.linked_user_request.POST = {
            'hidden-id': self.linked_user.id,
            'entry_date': '2012-01-01'
            }
        valid = ajax_delete_entry(self.linked_user_request)
        self.assertIsInstance(valid, HttpResponse)
        self.assertEquals(simplejson.dumps({
                "success": True,
                "error": '',
                "calendar": gen_calendar(2012, 1, 1, user=self.linked_user.id)
                }),
                valid.content)

    def testValidAjaxChangeHolidayEntry(self):

        # create the entry we want to delete
        TrackingEntry(entry_date="2012-01-01", user_id=self.linked_user.id)

        # create the post
        self.linked_user_request.POST = {
            'entry_date': '2012-01-01',
            'start_time': '09:00',
            'end_time': '17:00',
            'daytype': 'WRKDY',
            'breaks': '00:15:00',
            'hidden-id': self.linked_user.id,
        }
        valid = ajax_change_entry(self.linked_user_request)
        self.assertIsInstance(valid, HttpResponse)
        self.assertEquals(simplejson.dumps({
                "success": True,
                "error": '',
                "calendar": gen_calendar(2012, 1, 1, user=self.linked_user.id)
                }),
                valid.content)

    def testAjaxError(self):

        valid = ajax_error("test string")
        self.assertIsInstance(valid, HttpResponse)

        self.assertEquals(valid.content, simplejson.dumps({
                    'success': False,
                    'error': 'test string'
                    })
                          )

class UtilitiesTest(TestCase):

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
