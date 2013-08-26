import datetime

from django.test import TestCase
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from timetracker.overtime.models import PendingApproval
from timetracker.tracker.models import TrackingEntry
from timetracker.tests.basetests import create_users, delete_users
from timetracker.utils.datemaps import MARKET_CHOICES


class ApprovalTest(TestCase):

    @classmethod
    def setUpClass(self):
        create_users(self)
        self.ot_entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today(),
            start_time=datetime.time(0, 0, 0),
            end_time=datetime.time(17, 0, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )

	self.pending_entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today(),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="PENDI",
        )

        self.entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(16, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )

        self.ot_entry.full_clean()
        self.ot_entry.save()
        self.entry.full_clean()
        self.entry.save()

    @classmethod
    def tearDownClass(self):
        delete_users(self)

    def testPendingApprovalDenied(self):
        self.doapprovaltest(False, "Request for Overtime: Denied.", 0)

    def testPendingApprovalApproved(self):
        try:
            # we may be running with a default implementation which
            # doesn't sent e-mails.
            from timetracker.tracker.notifications import (
                send_overtime_notification, send_pending_overtime_notification,
                send_undertime_notification
            )
        except: # pragma: no cover
            return
        self.doapprovaltest(True, "Your recent timetracker actions.", 1)

    @override_settings(UNDER_TIME_ENABLED={M: True for M in MARKET_CHOICES})
    def doapprovaltest(self, status, message, attachments):
        approval = PendingApproval(
            entry=self.ot_entry,
            approver=self.linked_manager
        )
        approval.save()
        approval.close(status)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, message)
        self.assertEqual(len(mail.outbox[0].attachments), attachments)
        
    def doapprovalonpendingtest(self):
        approval = PendingApproval(
            entry=self.pending_entry,
            approver=self.linked_manager
        )
        approval.save()
        approval.close(True)
        self.assertEqual(approval.entry.daytype, "HOLIS")

    def testNoApprovalRequired(self): # pragma: no cover
        if not settings.SENDING_APPROVAL.get(self.linked_manager.market):
            return
        approval = PendingApproval(
            entry=self.entry,
            approver=self.linked_manager
        )
        approval.inform_manager()
        self.assertEqual(len(mail.outbox), 0)

    def testApprovalRequired(self): # pragma: no cover
        if not settings.SENDING_APPROVAL.get(self.linked_manager.market):
            return
        approval = PendingApproval(
            entry=self.ot_entry,
            approver=self.linked_manager
        )
        approval.inform_manager()
        self.assertEqual(len(mail.outbox), 1)

    def testSoftClose(self):
        entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(20, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )
        entry.full_clean()
        entry.save()
        entry.create_approval_request()
        pending = PendingApproval.objects.get(
            entry=entry
        )
        pending.tl_close(True)
        self.assertEqual(pending.tl_approved, True)

    def testDoubleClose(self):
        entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=3),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(20, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )
        entry.full_clean()
        entry.save()
        entry.create_approval_request()
        pending = PendingApproval.objects.get(
            entry=entry
        )
        try:
            # we may be running with a default implementation which
            # doesn't sent e-mails.
            from timetracker.tracker.notifications import (
                send_overtime_notification, send_pending_overtime_notification,
                send_undertime_notification
            )
        except:
            return
        pending.tl_close(True)
        pending.close(True)
        self.assertEqual(len(mail.outbox), 1)
        pending.tl_close(True)
        pending.close(True)
        self.assertEqual(len(mail.outbox), 1)

    def testDeniedClosedMail(self):
        entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=4),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(20, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )
        entry.full_clean()
        entry.save()
        entry.create_approval_request()
        pending = PendingApproval.objects.get(
            entry=entry
        )
        pending.tl_close(False)
        self.assertEqual(len(mail.outbox), 1)

    def testIsHolidayRequest(self):
        entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=5),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(20, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="PENDI",
        )
        entry.full_clean()
        entry.save()
        entry.create_approval_request()
        pending = PendingApproval.objects.get(
            entry=entry
        )
        self.assertEqual(pending.is_holiday_request(), True)

    def testTLDeny(self):
        entry = TrackingEntry(
            user=self.linked_user,
            entry_date=datetime.datetime.today() + datetime.timedelta(days=6),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(20, 45, 0),
            breaks=datetime.time(0, 15, 0),
            daytype="WKDAY",
        )
        entry.full_clean()
        entry.save()
        entry.create_approval_request()
        pending = PendingApproval.objects.get(
            entry=entry
        )
        pending.tl_close(False)
        self.assertEqual(len(mail.outbox), 1)
