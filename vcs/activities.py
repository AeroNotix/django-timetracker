import os
import imp

from django.conf import settings

from timetracker.vcs.models import Activity


def serialize_activityentry(entry):
    '''Serializes a single ActivityEntry into a JSON format.'''
    return {
        "id": entry.id,
        "date": str(entry.creation_date),
        "text": entry.activity.groupdetail,
        "amount": int(entry.amount)
    }

def defaultplugins(acc=None):
    '''Returns the plugins in the default location for either all accounts
    or a single account.'''
    return listplugins(settings.PLUGIN_DIRECTORY, acc=acc)

def pluginbyname(name, acc=None):
    '''Returns the named plugin for either all accounts or a single
    account.'''
    return defaultplugins(acc=acc).get(name)

def listplugins(directory, acc=None):
    '''Iterates through the passed-in directory, looking for raw Python
    modules to import, when it imports the modules we specifically
    look for several module-level attributes of which we make no
    error-checking to see if they are there or not.

    We check no errors since this will be a very early warning trigger
    if there is a programmatic warning.

    :param directory: :class:`str`, the name of the directory to
                      search for plugins.

    :return: List of dictionaries containing both the module and the
             module-level attributes for that module.
    '''

    plugins = {}
    for f in os.listdir(directory):
        # ignore irrelevant files and compiled python modules.
        if f == "__init__.py" or f == "example.py" or f.endswith(".pyc"):
            continue
        g = f.replace(".py", "")
        info = imp.find_module(g, [directory])
        # dynamically import our module and extract the callback along
        # with the attributes.
        m = imp.load_module(g, *info)
        if acc and acc not in m.ACCOUNTS:
            continue
        plugins[m.PLUGIN_NAME] = {
            "name": m.PLUGIN_NAME,
            "accounts": m.ACCOUNTS,
            "callback": getattr(m, m.CALLBACK),
            "module": m,
        }
    return plugins

def createuseractivities(user):
    choices = {
        'CZ': {
            'AR': [
                Activity(None, "CZAR", "Autorun", "Autorun", "# of autorun transaction launched", True, 1.52),
                Activity(None, "CZAR", "Bellin update", "Foreign Exchange", "# of uploads", True, 2.04),
                Activity(None, "CZAR", "Bellin update", "Foreign Exchange", "# of uploads", True, 2.04),
                Activity(None, "CZAR", "Bellin update", "Treasury", "# of uploads", True, 0.98),
                Activity(None, "CZAR", "Bellin update-cash flow", "Cash flow", "# of updates", True, 0.42),
                Activity(None, "CZAR", "Call", "Call", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Cash flow report", "Cash flow report", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Clearing ", "Clearing ", "# of clearings ", True, 3.37),
                Activity(None, "CZAR", "Clearing", "Cash on way (with report)", "# of clearings", True, 1.40),
                Activity(None, "CZAR", "Clearing", "Leasing (with report)", "# of clearings", True, 2.82),
                Activity(None, "CZAR", "Clearing", "Rest liability (with report)", "# of times process was done", True, 3.17),
                Activity(None, "CZAR", "Daily tracker", "Daily tracker", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Discount Report", "Discount Report_with email", "# of reports", True, 16.76),
                Activity(None, "CZAR", "Download Bank Statement from Bank Website", "Download Bank Statement from Bank Website", "# of statements", True, 2.41),
                Activity(None, "CZAR", "Emails sent", "Emails sent", "# of emails sent", True, 2.03),
                Activity(None, "CZAR", "Exchange rate reevaluation for open receivables and payables", "Exchange rate reevaluation for open receivables and payables", "# of reports", True, 13.81),
                Activity(None, "CZAR", "Exchange table rates differences", "Exchange table rates differences with mail", "# of reports", True, 26.45),
                Activity(None, "CZAR", "GL to treasury reconciliation FSL10N", "GL to treasury reconciliation FSL10N", "# of reconciliations", True, 0.17),
                Activity(None, "CZAR", "Investigation of accounts", "Investigation of accounts", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Investments report", "Investments report", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Open payables & receivables report", "Open payables & receivables report_with email", "# of reports", True, 32.86),
                Activity(None, "CZAR", "Post payments", "Dailmler lotus", "# of times process was done", True, 11.34),
                Activity(None, "CZAR", "Post payments", "Dailmler", "# of times process was done", True, 8.61),
                Activity(None, "CZAR", "Post payments", "Post payments", "# of payments", True, 1.85),
                Activity(None, "CZAR", "Prepayment reports", "Prepayment check accounts with reports", "# of accounts checked", True, 5.08),
                Activity(None, "CZAR", "Prepayment reports", "Prepayment check accounts", "# of accounts checked", True, 0.87),
                Activity(None, "CZAR", "Reevaluation", "Bank and cash", "# of times process was done", True, 3.33),
                Activity(None, "CZAR", "Reevaluation", "Cash pooling", "# of times process was done", True, 8.01),
                Activity(None, "CZAR", "Reevaluation", "Loan Behr Stuttgart with report", "# of times process was done", True, 7.43),
                Activity(None, "CZAR", "Reevaluation", "Prepayment", "# of times process was done", True, 3.33),
                Activity(None, "CZAR", "Research remittances", "Research remittances", "# of remittances searched", True, 2.56),
                Activity(None, "CZAR", "Set off agreement", "Set off agreement", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Special Client Request", "Special Client Request", "# of minutes", True, 1.00),
                Activity(None, "CZAR", "Bellin update", "Treasury", "# of uploads", True, 0.98),
            ],
            'AP': [
                Activity(None, "CZAP", "Blocked invoices", "Blocked invoices", "# of invoices", True, 0.49),
                Activity(None, "CZAP", "CRC mail", "Mail links deletion", "# of links/emails", True, 0.18),
                Activity(None, "CZAP", "CRC mail", "Mail", "# of emails", True, 9.21),
                Activity(None, "CZAP", "Call", "Call", "# of minutes", True, 1.00),
                Activity(None, "CZAP", "Clearing f-44 and tracker", "Clearing f-44 and tracker", "# of clearings", True, 2.20),
                Activity(None, "CZAP", "Consignment", "Add reference", "# of customers", True, 0.31),
                Activity(None, "CZAP", "Consignment", "Add reference&check tax", "# of customers", True, 0.47),
                Activity(None, "CZAP", "Consignment", "BASF", "# of minutes", True, 1.00),
                Activity(None, "CZAP", "Consignment", "Booking from email with template", "# of consi booked", True, 10.00),
                Activity(None, "CZAP", "Consignment", "Booking from email_verification of vendor", "# of vendors verified", True, 10.25),
                Activity(None, "CZAP", "Consignment", "Check tax", "# of customers", True, 0.16),
                Activity(None, "CZAP", "Consignment", "Consignment printing docs", "# of consigments printed", True, 0.98),
                Activity(None, "CZAP", "Consignment", "Consignment without printing", "# of consigments posted", True, 2.01),
                Activity(None, "CZAP", "Deleting invoices", "Deleting invoices", "# of invoices", True, 1.38),
                Activity(None, "CZAP", "Invoice correction booking", "Invoice correction booking", "# of invoices", True, 4.14),
                Activity(None, "CZAP", "Parked Invoices", "Parked Invoices", "# of invoices", True, 2.87),
                Activity(None, "CZAP", "Posting invoices", "Posting invoices", "# of invoices", True, 3.48),
                Activity(None, "CZAP", "Prepayment invoices posting", "Prepayment invoices posting", "# of invoices", True, 10.10),
                Activity(None, "CZAP", "QC", "QC", "# of invoices", True, 3.37),
                Activity(None, "CZAP", "Reminder letters", "Verification of invoice", "# of invoices", True, 6.58),
                Activity(None, "CZAP", "Reminder letters", "Verification of letter_send email", "# of reminders", True, 2.47),
                Activity(None, "CZAP", "Reports", "Unresolved parked invoices and debit notes", "# of reports", True, 46.08),
                Activity(None, "CZAP", "Reports", "Volume reports for TL", "# of reports", True, 1.76),
                Activity(None, "CZAP", "Reports", "Volume reports with email_to client", "# of reports", True, 2.97),
                Activity(None, "CZAP", "Reversal", "Reversal", "# of reversals", True, 3.30),
                Activity(None, "CZAP", "Smartfix", "Smartfix", "# of invoices", True, 2.06),
                Activity(None, "CZAP", "Special Client Request", "Special Client Request", "# of minutes", True, 1.00),
                Activity(None, "CZAP", "Speedi", "Speedi", "# of invoices in Speedi", True, 3.56),
                Activity(None, "CZAP", "Telecommunication cost booking", "Telecommunication cost booking", "# of line items posted", True, 0.72),
            ],
        }
    }
    for market in choices:
        for process in choices[market]:
            for activity in choices[market][process]:
                activity.save()
