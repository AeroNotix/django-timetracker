import datetime
from timetracker.tracker.models import Tbluser, Tblauthorization


def create_users(cls):
    '''we create users which will be linked to test how the automatic,
    retrieval of the links works'''

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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
            shiftlength="07:45:00",
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
            shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
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
        shiftlength="07:45:00",
        job_code="00F20G",
        holiday_balance=20
        )

def delete_users(cls):
    '''Deletes all the users on a Tbluser instance.'''
    [user.delete() for user in Tbluser.objects.all()]
