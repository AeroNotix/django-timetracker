# For the code which builds PDFs we need to give it a directory where
# it can find the custom font.
FONT_DIRECTORY = '/usr/share/fonts/TTF'

# Which accounts are sending approval requests to managers via e-mail.
SENDING_APPROVAL_MANAGERS = {
    "BF": True
}
# Which accounts are sending approval requests via e-mail.
SENDING_APPROVAL = SENDING_APPROVAL_MANAGERS

# Which accounts are sending approval requests to team leaders via
# e-mail.
SENDING_APPROVAL_TL = {
    "BF": True
}

# A map of account short codes to lists of activity codes to allow
# different accounts to have activities assigned to other accounts.
EXTRA_ACTIVITIES = {
    "BF": ["CZAP"]
}

# A list of user_id's which can view job codes. This is used when
# building the holiday page output so that the possibly unique
# identifier used for each employee can not be shown depending on what
# kind of user is viewing that data.
CAN_VIEW_JOBCODES = ["thunder@cats.com"]

# A map of which accounts are zeroing hours each month. This means
# when a new month has come then the balance starts again from 0 for
# undertime/overtime calculations.
ZEROING_HOURS = {
    "CZ": True
}

# If specific accounts need to have individualized ways of calculating
# balances then provide the callback here.
OVERRIDE_CALCULATION = {
    "BF": some_other_calculation,
}

# When certain accounts need to have a different managerial e-mail
# distribution list, override that here.
MANAGER_EMAILS_OVERRIDE = {
    "BF": ["bob@test.com"],
    "CZ": ["bob@test.com"]
}

# When certain accounts need to have a different managerial named
# people list, override that here.
MANAGER_NAMES_OVERRIDE = {
    "BF": ["Bob Test"],
}

# When specific individuals have powers to close approval requests
# even though they may not actually have the level required to do so,
# put their user_id here.
CAN_CLOSE_APPROVALS = [
    "bob@test.com"
]

# Certain accounts track undertime, put those accounts here.
UNDER_TIME_ENABLED = {
    "BF": True,
    "CZ": True
}

# For logging purposes when entries in the past are changed we
# determine how long ago it was and only track past changing entries
# which are older (in days) than this.
SUSPICIOUS_DATE_DIFF = 60 # days

# number of working days in a week
NUM_WORKING_DAYS = 5

# allowance in a single year for someone's days on demand
DAY_ON_DEMAND_ALLOWANCE = 4

# The threshold from an entry to how much over the users scheduled
# working time it needs to be before it's classed as actual
# overtime. This is in hours.
DEFAULT_OT_THRESHOLD = 1.0

# If specific accounts need a different threshold then put that here.
OT_THRESHOLDS = {
    "BF": 0.5
}

# The domain name which will be used for the webpage.
DOMAIN_NAME = "http://localhost:8080/"

# The location where the documentation pages are.
DOCUMENTATION_BASE_URL = DOMAIN_NAME + '/docs/'

# For the purposes of VCS mass upload plugins you need to provide a
# directory where the files should go.
PLUGIN_DIRECTORY = "/home/xeno/dev/timetracker/vcs/plugins/"

# There's a management command provided for easy crontab usage which
# e-mails those in the below map about the numbers of approvals
# pending their notice.
SENDING_APPROVAL_DIGESTS = {
    "BF": True,
    "CZ": True,
    "BG": True,
    "BK": True
}


# For certain accounts it's not enough to simply send the manager a
# notice that an approval is pending and/or has been created. This is
# because there are better suited people for approving that
# request. This is why this map exists.
#
# If you wish to, for example, have all BFHR approval requests go to
# "skeletor@evil.com" then make a map such as:
#
# {"BF": {"HR": ["skeletor@evil.com"]}} and the approval requests will
# reach the correct people.
TL_APPROVAL_CHAINS = {
    "BF": {
        "HR": [
            "skeletor@evil.com",
            "aga.piwnik@testing.com",
            "katar.grusz@testing.com"
        ],
        "TE": ["anna.donska@testing.com"],
        "AP": ["magda.ska-biernat@testing.com", "paulina.whatever@testing.com"],
        "SC": ["magda.ska-biernat@testing.com", "paulina.whatever@testing.com"],
        "AR": ["magda.ska-biernat@testing.com", "paulina.what@testing.com"]
    }
}

# An iterable of which teams have the VCS portion of the site enabled
# for them.
VCS_ENABLED = {"CZ", "BK", "BG"}
