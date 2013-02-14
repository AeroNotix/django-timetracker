import datetime
import simplejson
import random
import functools
import time
from unittest import skipUnless

from django.db import IntegrityError
from django.test import TestCase, LiveServerTestCase
from django.http import HttpResponse, Http404

from tracker.models import (Tbluser,
                            TrackingEntry,
                            Tblauthorization)

from utils.calendar_utils import (validate_time, parse_time,
                                              delete_user, useredit,
                                              mass_holidays, ajax_delete_entry,
                                              gen_calendar, ajax_change_entry,
                                              ajax_error)
from utils.datemaps import pad, float_to_time, generate_select, ABSENT_CHOICES
from utils.error_codes import DUPLICATE_ENTRY

try:
    from selenium.webdriver.firefox.webdriver import WebDriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def create_users(cls):
    # we create users which will be linked,
    # to test how the automatic retrieval
    # of the links works

    cls.linked_super_user = Tbluser.objects.create(
        user_id="test.super@test.com",
        firstname="test",
        lastname="case",
        password="password",
        user_type="SUPER",
        market="BG",
        process="AP",
        start_date=datetime.datetime.today(),
        breaklength="00:15:00",
        shiftlength="08:00:00",
        job_code="00F20G",
        holiday_balance=20
        )


    cls.linked_manager = Tbluser.objects.create(
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

    cls.linked_user = Tbluser.objects.create(
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

    users = [
    Tbluser.objects.create(
            user_id="test.user%d@test.com" % userid,
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
    for userid in range(5)]
    users.append(
        Tbluser.objects.create(
            user_id="test.user7@test.com",
            firstname="test",
            lastname="case",
            password="password",
            user_type="RUSER",
            market="BG",
            process="AO",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
            )
        )

    cls.linked_teamlead = Tbluser.objects.create(
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
    cls.authorization = Tblauthorization.objects.create(admin=cls.linked_manager)
    cls.authorization.save()
    cls.authorization.users.add(cls.linked_user, cls.linked_teamlead)
    [cls.authorization.users.add(user) for user in users]
    cls.authorization.save()

    cls.supauthorization = Tblauthorization.objects.create(admin=cls.linked_super_user)
    cls.supauthorization.users.add(cls.linked_manager, cls.linked_teamlead, cls.linked_user)
    cls.supauthorization.save()

    cls.unlinked_super_user = Tbluser.objects.create(
        user_id="test.unlinkedsuper@test.com",
        firstname="test",
        lastname="case",
        password="password",
        user_type="SUPER",
        market="BG",
        process="AP",
        start_date=datetime.datetime.today(),
        breaklength="00:15:00",
        shiftlength="08:00:00",
        job_code="00F20G",
        holiday_balance=20
        )

    cls.unlinked_manager = Tbluser.objects.create(
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

    cls.unlinked_user = Tbluser.objects.create(
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

    cls.unlinked_teamlead = Tbluser.objects.create(
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

def delete_users(cls):
    [user.delete() for user in Tbluser.objects.all()]

class BaseUserTest(TestCase):

    def setUp(self):

        create_users(self)

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
        holidays = {
            self.linked_manager.id: list(),
            self.linked_user.id: list(),
            }
        holidays_empty = {
            self.linked_manager.id: list(),
            self.linked_user.id: list(),
            }
        for day in range(1, 32):
            holidays[self.linked_manager.id].append(random.choice(ABSENT_CHOICES)[0])
            holidays[self.linked_user.id].append(random.choice(ABSENT_CHOICES)[0])
            holidays_empty[self.linked_manager.id].append("empty")
            holidays_empty[self.linked_user.id].append("empty")
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
        delete_users(self)
        [holiday.delete() for holiday in TrackingEntry.objects.all()]

class UserTestCase(BaseUserTest):
    '''
    Tests the methods attached to user instances
    '''

    def test_Sup_TL_or_Admin(self):
        self.assertEquals(self.linked_super_user.sup_tl_or_admin(), True)
        self.assertEquals(self.linked_manager.sup_tl_or_admin(), True)
        self.assertEquals(self.linked_teamlead.sup_tl_or_admin(), True)
        self.assertEquals(self.linked_user.sup_tl_or_admin(), False)

    def test_IsSuper(self):
        self.assertEquals(self.linked_super_user.is_super(), True)
        self.assertEquals(self.linked_manager.is_super(), False)
        self.assertEquals(self.linked_teamlead.is_super(), False)
        self.assertEquals(self.linked_user.is_super(), False)

    def test_Super_Or_Admin(self):
        self.assertEquals(self.linked_super_user.super_or_admin(), True)
        self.assertEquals(self.linked_manager.super_or_admin(), True)
        self.assertEquals(self.linked_teamlead.super_or_admin(), False)
        self.assertEquals(self.linked_user.super_or_admin(), False)

    def test_IsAdmin(self):
        self.assertEquals(self.linked_super_user.is_admin(), False)
        self.assertEquals(self.linked_manager.is_admin(), True)
        self.assertEquals(self.linked_teamlead.is_admin(), False)
        self.assertEquals(self.linked_user.is_admin(), False)

    def test_Admin_or_TL(self):
        self.assertEquals(self.linked_super_user.admin_or_tl(), False)
        self.assertEquals(self.linked_manager.admin_or_tl(), True)
        self.assertEquals(self.linked_teamlead.admin_or_tl(), True)
        self.assertEquals(self.linked_user.admin_or_tl(), False)

    def test_IsTL(self):
        self.assertEquals(self.linked_super_user.is_tl(), False)
        self.assertEquals(self.linked_manager.is_tl(), False)
        self.assertEquals(self.linked_teamlead.is_tl(), True)
        self.assertEquals(self.linked_user.is_tl(), False)

    def test_IsUSER(self):
        self.assertEquals(self.linked_super_user.is_user(), False)
        self.assertEquals(self.linked_manager.is_user(), False)
        self.assertEquals(self.linked_teamlead.is_user(), False)
        self.assertEquals(self.linked_user.is_user(), True)

    def test_get_subordinates(self):
        self.assertEquals(len(self.linked_super_user.get_subordinates()), 4)
        self.assertEquals(len(self.linked_manager.get_subordinates()), 9)
        self.assertEquals(len(self.linked_teamlead.get_subordinates()), 9)
        self.assertEquals(len(self.linked_user.get_subordinates()), 7)

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
        self.assertEquals(self.linked_super_user.user_type, "SUPER")
        self.assertEquals(self.linked_manager.user_type, "ADMIN")
        self.assertEquals(self.linked_teamlead.user_type, "TEAML")
        self.assertEquals(self.linked_user.user_type, "RUSER")

    def testHolidayBalanceMix(self):
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

    def testHolidayBalanceAdd(self):
        '''
        Test for the holiday additional total works
        '''
        for day in (("1", "PUWRK"), ("2", "PUWRK"), ("3", "PUWRK")):
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

    def testHolidayBalanceDecrement(self):
        '''
        Test for the return decrement total works
        '''
        for day in (("1", "RETRN"), ("2", "RETRN"), ("3", "RETRN")):
            entry = TrackingEntry(
                entry_date="2012-01-%s" % day[0],
                user_id=self.linked_user.id,
                start_time="00:00:00",
                end_time="00:00:00",
                breaks="00:00:00",
                daytype=day[1],
            )
            entry.save()

        self.assertEquals(self.linked_user.get_holiday_balance(2012), 17)


class DatabaseTestCase(BaseUserTest):
    '''
    Class which tests the database for improper settings
    '''

    def testDuplicateError(self):
        '''
        Test which ensures that duplicate e-mail addresses
        cannot be used
        '''
        try:
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
        # we're catching & ignoring duplicate entry
        # because that's what it's supposed to do
        except IntegrityError as error:
            if error[0] == DUPLICATE_ENTRY:
                pass
            else:
                raise

class AjaxTestCase(BaseUserTest):
    '''
    Class which tests the ajax request handler functions
    '''

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
            'mass_data': self.holiday_data
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
            'mass_data': self.holiday_data_empty
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
            'mass_data': self.holiday_data
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

class FrontEndTest(LiveServerTestCase):

    def setUp(self):
        create_users(self)

    def tearDown(self):
        delete_users(self)
        try:
            self.accessURL("/edit_profile/")
            self.driver.get_element_by_id("logout-btn").click()
            self.accessURL("")
        except:
            pass

    @classmethod
    def setUpClass(cls):
        cls.driver = WebDriver()
        super(FrontEndTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FrontEndTest, cls).tearDownClass()
        delete_users(cls)
        cls.driver.quit()

    @skipUnless(SELENIUM_AVAILABLE, "These tests require Selenium to be installed.")
    def test_AccessRights(self):
        self.user_login()

        # selenium doesn't give direct access to the response
        # code so we look for some element.

        for url in ["/admin_view/", "/yearview/", "/user_edit/", "/holiday_planning/"]:
            self.accessURL(url)
            time.sleep(1)
            self.assertRaises(NoSuchElementException, self.driver.find_element_by_id, "logout-btn")

    @skipUnless(SELENIUM_AVAILABLE, "These tests require Selenium to be installed.")
    def test_WeekendButtonHasNoFunction(self):
        '''
        This ensures that the weekend button simply servers to show the
        user what the element represents. We don't want the element to
        have any use other than that, otherwise we could end up with
        weekends ending up being stored in the database.
        '''
        self.manager_login()
        # wait to be logged in
        time.sleep(2)
        self.accessURL("/holiday_planning/")
        holiday_table = self.driver.find_element_by_id("holiday-table")
        cells = holiday_table.find_elements_by_tag_name("td")

        clicked_cells = []
        for cell in cells:
            if cell.get_attribute("usrid") == "1":
                if cell.get_attribute("class") != "WKEND":
                    clicked_cells.append(cell)
                    cell.click()
        holiday_buttons = self.driver.find_element_by_id("holiday-buttons")
        buttons = holiday_buttons.find_elements_by_tag_name("td")
        for button in buttons:
            if "WKEND" in button.get_attribute("class"):
                button.click()
        for cell in clicked_cells:
            self.assertFalse("WKEND" in cell.get_attribute("class"))

    @skipUnless(SELENIUM_AVAILABLE, "These tests require Selenium to be installed.")
    def test_SubmitHolidays(self):
        self.manager_login()
        # wait to be logged in
        time.sleep(2)

        self.accessURL("/holiday_planning/")
        holiday_table = self.driver.find_element_by_id("holiday-table")
        cells = holiday_table.find_elements_by_tag_name("td")
        count = 0
        for cell in cells:
            if cell.get_attribute("usrid"):
                if cell.get_attribute("class") != "WKEND":
                    cell.click()
                    count += 1
                    # we don't need that many to test
                    if count == 30:
                        break
        self.click_daytype("HOLIS")
        self.driver.find_element_by_id("submit_all").click()
        time.sleep(5)
        self.driver.switch_to_alert().accept()
        self.assertEquals(len(TrackingEntry.objects.all()), count)

    @skipUnless(SELENIUM_AVAILABLE, "These tests require Selenium to be installed.")
    def test_HolidayPageStateCheck(self):
        self.manager_login()
        time.sleep(2)

        self.accessURL("/holiday_planning/")
        self.goto_month("2")
        time.sleep(3)
        holiday_table = self.driver.find_element_by_id("holiday-table")
        cells = holiday_table.find_elements_by_tag_name("td")
        count = 0
        for cell in cells:
            if cell.get_attribute("usrid"):
                if cell.get_attribute("class") != "WKEND":
                    cell.click()
                    count += 1
                    # we don't need that many to test
                    if count == 10:
                        break
        self.click_daytype("HOLIS")
        inputs = self.driver.find_elements_by_tag_name("input")
        for input_ in inputs:
            if "button_2" in input_.get_attribute("id"):
                input_.click()
                time.sleep(2)
                self.driver.switch_to_alert().accept()
                break
        self.goto_month("3")
        time.sleep(2)
        inputs = self.driver.find_elements_by_tag_name("input")
        for input_ in inputs:
            if "button_" in input_.get_attribute("id"):
                input_.click()
                time.sleep(2)
                self.driver.switch_to_alert().accept()
                break
        self.assertEquals(len(TrackingEntry.objects.all()), count)

    @skipUnless(SELENIUM_AVAILABLE, "These tests require Selenium to be installed.")
    def test_Logins(self):
        # login
        self.user_login()
        # if this raises it means we're logged in.
        self.assertRaises(NoSuchElementException, self.driver.find_element_by_id, "error")
        self.driver.find_element_by_id("logout-btn").click()
        # once again with a manager
        self.manager_login()
        self.assertRaises(NoSuchElementException, self.driver.find_element_by_id, "error")
        self.driver.find_element_by_id("logout-btn").click()

    def login(self, who):
        self.driver.get(self.live_server_url)
        self.driver.find_element_by_id("login-user").send_keys(who.user_id)
        self.driver.find_element_by_id("login-password").send_keys(who.password)
        self.driver.find_element_by_id("add_button").click()
    def user_login(self):
        self.login(self.linked_user)
    def manager_login(self):
        self.login(self.linked_manager)

    def accessURL(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def click_daytype(self, daytype):
        holiday_buttons = self.driver.find_element_by_id("holiday-buttons")
        buttons = holiday_buttons.find_elements_by_tag_name("td")
        for button in buttons:
            if daytype in button.get_attribute("class"):
                button.click()

    def goto_month(self, num):
        select = self.driver.find_element_by_id("month_select")
        options = select.find_elements_by_tag_name("option")
        for option in options:
            if option.get_attribute("value") == num:
                option.click()
                break

FrontEndTest = None
