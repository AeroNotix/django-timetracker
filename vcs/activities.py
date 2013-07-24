import os
import imp

from django.conf import settings
from django.db import IntegrityError

from timetracker.vcs.models import Activity


def serialize_activityentry(entry):
    '''Serializes a single ActivityEntry into a JSON format.'''
    return { # pragma: no cover
        "id": entry.id,
        "date": str(entry.creation_date),
        "text": entry.activity.groupdetail,
        "amount": int(entry.amount)
    }

def defaultplugins(acc=None):
    '''Returns the plugins in the default location for either all accounts
    or a single account.'''
    return listplugins(settings.PLUGIN_DIRECTORY, acc=acc) # pragma: no cover

def pluginbyname(name, acc=None):
    '''Returns the named plugin for either all accounts or a single
    account.'''
    return defaultplugins(acc=acc).get(name) # pragma: no cover

def listplugins(directory, acc=None): # pragma: no cover
    '''Iterates through the passed-in directory, looking for raw Python
    modules to import, when it imports the modules we specifically
    look for several module-level attributes of which we make no
    error-checking to see if they are there or not.

    We check no errors since this will be a very early warning trigger
    if there is a programmatic warning.

    A more efficient version of this would be to load the module by
    name whenever the user requests a specific report. However, this
    presents a serious security risk and thus; instead of loading the
    report processor which the user asks for, we find the available
    reports and *then* filter that list by what the user is allowed to
    access and *then* give them the report they requested in there if
    it is available.

    Otherwise, we could end up with a directory traversal attack. This
    is somewhat mitigated by the fact that imp.load_module requires an
    explicit load path and thus. I far much prefer the filtered
    approach versus a whimsical dynamic lookup method.

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

def createuseractivities():
    activities = [
        Activity(None, "CZAR", "Autorun", "Autorun", "# of autorun transaction launched", True, 1.52),
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
        Activity(None, "ALL", "Avoidable Losses", "No Load", "enter time in min", True, 1, "COUAL"),
        Activity(None, "ALL", "Avoidable Losses", "System Downtime / System issues", "enter time in min", True, 1, "COUAL"),
        Activity(None, "ALL", "Avoidable Losses", "Technical maintenance", "enter time in min", True, 1, "COUAL"),
        Activity(None, "ALL", "Non Transaction Time", "Celebration", "enter time in min", True, 1, "COUTT"),
        Activity(None, "ALL", "Non Transaction Time", "Documentation/ ISO Audits", "enter time in min", True, 1, "QPR"),
        Activity(None, "ALL", "Non Transaction Time", "Escalations", "enter time in min", True, 1, "QEF"),
        Activity(None, "ALL", "Non Transaction Time", "Green Star", "enter time in min", True, 1, "QAPP"),
        Activity(None, "ALL", "Non Transaction Time", "Helping Others", "enter time in min", True, 1, "QIF"),
        Activity(None, "ALL", "Non Transaction Time", "IE tool updation", "enter time in min", True, 1, "QAPP"),
        Activity(None, "ALL", "Non Transaction Time", "Meetings", "enter time in min", True, 1, "QAPP"),
        Activity(None, "ALL", "Non Transaction Time", "Projects", "enter time in min", True, 1, "QPR"),
        Activity(None, "ALL", "Non Transaction Time", "Special/Management Requests", "enter time in min", True, 1, "COUTT"),
        Activity(None, "ALL", "Non Transaction Time", "Training", "enter time in min", True, 1, "QPR"),
        Activity(None, "ALL", "Unavoidable losses", "Absenteeism", "enter time in min", True, 1, "COUUL"),
        Activity(None, "BGAP", "Blocked invoices_with email", "Blocked invoices_with email", "# of invoices", True, 5.1, "QEF"),
        Activity(None, "BGAP", "Blocked invoices_without email", "Blocked invoices_without email", "# of invoices", True, 2.69, "QEF"),
        Activity(None, "BGAP", "Check for DFU duplicates -paper doc", "Check for DFU duplicates -paper doc", "# of invoices checked", True, 0.63, "QIF"),
        Activity(None, "BGAP", "Consignment", "Consignment direct posting SAP", "# of consignements posted", True, 0.65, "PVA"),
        Activity(None, "BGAP", "Consignment", "Consignment_incoming mail with price discrepancies", "# of consignements posted", True, 5.4, "QEF"),
        Activity(None, "BGAP", "Consignment", "Consignment_preparing forms_price discrepancies", "# of consi formulars prepared", True, 13.47, "QEF"),
        Activity(None, "BGAP", "Consignment", "Consignment_price discrepancy_issue received from vendor via email", "# of consi formulars prepared", True, 12.34, "QEF"),
        Activity(None, "BGAP", "CRC", "Call", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGAP", "CRC", "Mail", "# of emails", True, 7.32, "PVA"),
        Activity(None, "BGAP", "Dunning Letters", "Dunning Letters", "# of invoices checked", True, 5.84, "QEF"),
        Activity(None, "BGAP", "Emails with no answer", "Emails with no answer", "# of emails", True, 0.24, "PNVA"),
        Activity(None, "BGAP", "IC", "FI  invoices with many positions", "# of line items", True, 0.32, "PVA"),
        Activity(None, "BGAP", "IC", "FI_WF kick off - IC", "# invoices", True, 1.89, "PVA"),
        Activity(None, "BGAP", "IC", "Netting table update", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGAP", "IC", "Netting/parked inv. Tracker update_without posting", "# of invoices updated", True, 0.31, "PVE"),
        Activity(None, "BGAP", "Parked invoices", "Parked invoices_with mail", "# of invoices", True, 4.91, "QEF"),
        Activity(None, "BGAP", "Parked invoices", "Parked invoices_without mail", "# of invoices", True, 3.06, "QEF"),
        Activity(None, "BGAP", "Posting invoices", "Posting invoices", "# of invoices", True, 2.42, "PVA"),
        Activity(None, "BGAP", "Printing documents", "Printing documents", "# of docs", True, 1.65, "PNVA"),
        Activity(None, "BGAP", "QC", "QC", "# of invoices", True, 1.92, "QPR"),
        Activity(None, "BGAP", "Reversal", "Reversal_correction&booking", "# of invoices corrected", True, 11.35, "QIF"),
        Activity(None, "BGAP", "Reversal tracking", "Reversal tracking", "# of invoices tracked", True, 3.15, "QAPP"),
        Activity(None, "BGAP", "RTV", "RTV_Recheck", "# of invoices", True, 1.12, "QPR"),
        Activity(None, "BGAP", "RTV", "RTV_SAP", "# of invoices", True, 4.79, "QPR"),
        Activity(None, "BGAP", "Smartfix", "Consignment verification", "# of invoices", True, 0.61, "PVA"),
        Activity(None, "BGAP", "Smartfix", "SAP-batch verification", "# of batches checked", True, 0.54, "PVA"),
        Activity(None, "BGAP", "Smartfix", "SAP-invoice verification+note", "# of invoices", True, 1.32, "QPR"),
        Activity(None, "BGAP", "Smartfix", "Smartfix", "# of invoices", True, 0.9, "QEF"),
        Activity(None, "BGAP", "Special Client Request", "Special Client Request", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGAP", "Speedi", "Speedi_check/change invoice", "# of invoices", True, 2.34, "PVE"),
        Activity(None, "BGAP", "Speedi", "Speedi_DFU", "# of invoices", True, 0.22, "PVA"),
        Activity(None, "BGAP", "Speedi", "Speedi_DFU_check additional information-MIRO", "# of invoices", True, 2.11, "PVE"),
        Activity(None, "BGAP", "Speedi", "Speedi_DFU_check order number/details", "# of invoices", True, 0.58, "PVE"),
        Activity(None, "BGAP", "Speedi", "Speedi_DFU_left items_need to be clarified with client", "# of emails", True, 3.05, "QEF"),
        Activity(None, "BGAP", "Trackers", "Parked/blocked report update", "# of minutes", True, 1, "QPR"),
        Activity(None, "BGAP", "Trackers", "QC report update", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGAP", "Trackers", "Reminder report update", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGAP", "Vendor account maintanence", "Vendor account maintanence", "# of minutes", True, 1, "PNVA"),
        Activity(None, "BKAP", "Blocked invoices", "Blocked invoices_with email", "# of invoices", True, 4.17, "QEF"),
        Activity(None, "BKAP", "Blocked invoices", "Blocked invoices_without email", "# of invoices", True, 2.23, "QEF"),
        Activity(None, "BKAP", "Consignment", "Consignment_preparing forms_price discrepancies", "# of consi formulars prepared", True, 13.47, "QEF"),
        Activity(None, "BKAP", "Consignment posting", "Consignment posting", "# of invoices", True, 7.04, "PVA"),
        Activity(None, "BKAP", "CRC", "Call", "# of minutes", True, 1, "PVA"),
        Activity(None, "BKAP", "CRC", "Mail", "# of emails", True, 7.32, "PVA"),
        Activity(None, "BKAP", "Dunning Letters", "Dunning Letters", "# of invoices checked", True, 5.84, "QEF"),
        Activity(None, "BKAP", "Emails with no answer", "Emails with no answer", "# of emails", True, 0.24, "PNVA"),
        Activity(None, "BKAP", "Parked invoices", "Parked invoices_with email", "# of invoices", True, 4.47, "QEF"),
        Activity(None, "BKAP", "Parked invoices", "Parked invoices_without email", "# of invoices", True, 1.13, "QEF"),
        Activity(None, "BKAP", "Posting invoices", "Posting invoices", "# of invoices", True, 2.42, "PVA"),
        Activity(None, "BKAP", "Printing documents", "Printing documents", "# of docs", True, 1.65, "PNVA"),
        Activity(None, "BKAP", "QC", "QC", "# of invoices", True, 1.92, "QPR"),
        Activity(None, "BKAP", "Reversal", "Reversal_correction&booking", "# of invoices corrected", True, 11.35, "QIF"),
        Activity(None, "BKAP", "Reversal tracking", "Reversal tracking", "# of invoices tracked", True, 3.15, "QAPP"),
        Activity(None, "BKAP", "RTV", "RTV_Recheck", "# of invoices", True, 1.12, "QPR"),
        Activity(None, "BKAP", "RTV", "RTV_SAP", "# of invoices", True, 4.79, "QPR"),
        Activity(None, "BKAP", "Smartfix", "Smartfix", "# of invoices", True, 1.42, "PVA"),
        Activity(None, "BKAP", "Special Client Request", "Special Client Request", "# of minutes", True, 1, "PVE"),
        Activity(None, "BKAP", "Speedi", "Speedi_check/change invoice", "# of invoices", True, 2.34, "PVA"),
        Activity(None, "BKAP", "Speedi", "Speedi_DFU", "# of invoices", True, 0.22, "PVE"),
        Activity(None, "BKAP", "Speedi", "Speedi_DFU_change order number", "# of invoices", True, 1.16, "QEF"),
        Activity(None, "BKAP", "Speedi", "Speedi_DFU_left items_need to be clarified with client", "# of emails", True, 3.62, "PVE"),
        Activity(None, "BKAP", "Vendor account maintanence", "Vendor account maintanence", "# of minutes", True, 1, "PNVA"),
        Activity(None, "BGAR", "AR List", "AR List", "# of AR lists done", True, 5.64, "PVA"),
        Activity(None, "BGAR", "AR List", "AR List check", "# of AR lists done", True, 3, "QPR"),
        Activity(None, "BGAR", "Autorun", "Autorun", "# of payments cleared manually", True, 0.19, "PVA"),
        Activity(None, "BGAR", "Call", "Call", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGAR", "CiR List", "Check CiR Lists", "# of lists checked", True, 3.81, "PVA"),
        Activity(None, "BGAR", "CiR List", "Check CiR Lists - big lists", "# of lists checked", True, 0.0, "PVA"),
        Activity(None, "BGAR", "CiR List", "Check CiR Lists - small lists", "# of lists checked", True, 0.0, "PVA"),
        Activity(None, "BGAR", "CiR List", "CiR List_big amounts", "# of amounts ", True, 1.35, "PVA"),
        Activity(None, "BGAR", "CiR List", "CiR List_differences-mail", "# of emails", True, 8.24, "QEF"),
        Activity(None, "BGAR", "CiR List", "CiR Lists", "# of lists", True, 13.1, "PVA"),
        Activity(None, "BGAR", "CiR List", "Investigation of differences", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGAR", "Download Bank Statement from Bellin", "Download Bank Statement from Bellin", "# of attachments", True, 1.03, "PVE"),
        Activity(None, "BGAR", "Emails sent", "Emails sent", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGAR", "GL to treasury reconciliation FSL10N", "GL to treasury reconciliation FSL10N", "# of reports", True, 8.76, "PVE"),
        Activity(None, "BGAR", "Load Mappen into SAP", "Load Mappen into SAP", "# of mapp loadings", True, 2.94, "PVA"),
        Activity(None, "BGAR", "Load Mappen into SAP", "Load Mappen into SAP - Kreditoren", "# of payments", True, 0.0, "PVA"),
        Activity(None, "BGAR", "Load Mappen into SAP", "Load Mappen into SAP - Leasing", "# of payments", True, 0.0, "PVA"),
        Activity(None, "BGAR", "Mapp loading/end of mapp", "Mapp loading/end of mapp", "# of mapps", True, 0.29, "PVA"),
        Activity(None, "BGAR", "Netting investigation", "Netting investigation", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGAR", "Payment advice_extract page_describe", "Payment advice_extract page_describe", "# of payment advices described", True, 1.45, "PVE"),
        Activity(None, "BGAR", "Post non standard payments-daimler etc", "Post non standard payments-daimler etc", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGAR", "Post payments", "Post payments", "# of payments ", True, 0.57, "PVA"),
        Activity(None, "BGAR", "Post payments", "Post payments differences", "# of positions posted", True, 1.33, "PVA"),
        Activity(None, "BGAR", "Post payments", "Post payments_reposting", "# of payments", True, 1.52, "PVA"),
        Activity(None, "BGAR", "Post payments_Netting (check tracker)", "Post payments_Netting (check tracker)", "# of payments ", True, 1.47, "PVA"),
        Activity(None, "BGAR", "Reminders (sending out) part I", "Reminders (sending out) part I", "# of times process was done", True, 25, "PVA"),
        Activity(None, "BGAR", "Reminders (sending out) part II", "Reminders (sending out) part II", "# of documents", True, 3.42, "PVE"),
        Activity(None, "BGAR", "Research remittances", "Research remittances_email/fax", "# of remittances", True, 0.55, "PVE"),
        Activity(None, "BGAR", "Research remittances", "Research remittances_portal", "# of remittances", True, 1.95, "PVE"),
        Activity(None, "BGAR", "Research remittances", "Research remittances_speedi", "# of remittances", True, 1.09, "PVE"),
        Activity(None, "BGAR", "Save documents on Quick Place", "Save documents on Quick Place", "# of documents", True, 1.41, "PNVA"),
        Activity(None, "BGAR", "Tracker", "Sharepoint tracker", "# of line items", True, 0.59, "QAPP"),
        Activity(None, "BKAR", "Add posting/clearing number on pdf file", "Add posting/clearing number on pdf file", "# of payments described", True, 0.55, "PVE"),
        Activity(None, "BKAR", "AR Aging report ", "AR Aging report ", "# of positions checked", True, 3.59, "PVA"),
        Activity(None, "BKAR", "AR List", "AR List ckeck", "# of AR lists done", True, 3, "QPR"),
        Activity(None, "BKAR", "Autorun", "Autorun", "# of payments cleared", True, 0.19, "PVA"),
        Activity(None, "BKAR", "Call", "Call", "# of minutes", True, 1, "PVE"),
        Activity(None, "BKAR", "Cashflowdata in Bellin (abgleich)", "Cashflowdata in Bellin (abgleich)", "# of positions changed", True, 0.82, "PVA"),
        Activity(None, "BKAR", "Download Bank Statement from Bellin", "Download Bank Statement from Bellin", "# of attachments", True, 1.03, "PVE"),
        Activity(None, "BKAR", "Emails sent", "Emails sent", "# of minutes", True, 1, "PVE"),
        Activity(None, "BKAR", "GL to treasury reconciliation FSL10N", "GL to treasury reconciliation FSL10N", "# of reports", True, 8.76, "PVE"),
        Activity(None, "BKAR", "Load Mappen into SAP", "Load Mappen into SAP", "# of mapp loadings", True, 2.94, "PVA"),
        Activity(None, "BKAR", "Load Mappen into SAP", "Load Mappen into SAP - Kreditoren", "# of payments", True, 0.0, "PVA"),
        Activity(None, "BKAR", "Load Mappen into SAP", "Load Mappen into SAP - Leasing", "# of payments", True, 0.0, "PVA"),
        Activity(None, "BKAR", "Mapp loading/end of mapp", "Mapp loading/end of mapp", "# of mapps", True, 0.29, "PVA"),
        Activity(None, "BKAR", "Netting investigation", "Netting investigation", "# of minutes", True, 1, "PVE"),
        Activity(None, "BKAR", "Payment advice-describing", "Payment advice-describing", "# of payment advices described", True, 1.52, "PVE"),
        Activity(None, "BKAR", "Post payments", "Post payments", "# of payments posted", True, 1.49, "PVA"),
        Activity(None, "BKAR", "Post payments", "Post payments differences", "# of positions posted", True, 1.33, "PVA"),
        Activity(None, "BKAR", "Post payments_Netting (check tracker)", "Post payments_Netting (check tracker)", "# of payments ", True, 1.47, "PVA"),
        Activity(None, "BKAR", "Reminders (sending out) part I", "Reminders (sending out) part I", "# of times process was done", True, 25, "PVA"),
        Activity(None, "BKAR", "Reminders (sending out) part II", "Reminders (sending out) part II", "# of documents", True, 3.42, "PVE"),
        Activity(None, "BKAR", "Remittance advices_mail/fax", "Remittance advices_mail/fax", "# of remittances", True, 0.55, "PVE"),
        Activity(None, "BKAR", "Research remittances_portal", "Research remittances_portal", "# of remittances", True, 1.95, "PVE"),
        Activity(None, "BKAR", "Research remittances_speedi", "Research remittances_speedi", "# of remittances", True, 1.09, "PVE"),
        Activity(None, "BKAR", "Save documents on Quick place", "Save documents on Quick place", "# of documents", True, 1.41, "PNVA"),
        Activity(None, "BKAR", "Tracker", "Sharepoint tracker", "# of line items", True, 0.59, "QAPP"),
        Activity(None, "BGSC", "Archiving", "Archiving", "# of documents", True, 0.21, "PNVA"),
        Activity(None, "BGSC", "Export invoices via BGSC tool on client sharepiont", "Export invoices via BGSC tool on client sharepiont", "# of times process was done", True, 3.12, "PNVA"),
        Activity(None, "BGSC", "Mahnungs tracking", "Mahnungs tracking", "# of mahnungs", True, 0.96, "QPR"),
        Activity(None, "BGSC", "Printing", "Printing deckblats", "# of times process was done", True, 2, "PVE"),
        Activity(None, "BGSC", "Printing", "Printing invoices from e-mail", "# of invoices", True, 0.52, "PVE"),
        Activity(None, "BGSC", "Repatriation", "Repatriation", "# of minutes", True, 1, "PNVA"),
        Activity(None, "BGSC", "Repatriation", "Repatriation - fracht", "# of minutes", True, 1, "PNVA"),
        Activity(None, "BGSC", "RTV tracking", "RTV tracking", "# of rtv's", True, 0.98, "QPR"),
        Activity(None, "BGSC", "BGSC", "BGSC regular documents", "# of pages", True, 0.14, "PVA"),
        Activity(None, "BGSC", "BGSC", "Scannning attachments", "# of attachments", True, 0.14, "PVA"),
        Activity(None, "BGSC", "Sorting documents", "Sorting documents", "# of documents", True, 0.06, "PVE"),
        Activity(None, "BGSC", "Sticking barcodes", "Sticking barcodes", "# of documents", True, 0.12, "PVE"),
        Activity(None, "BGTE", "Activate employees", "Activate employees", "# of employees activated", True, 0.88, "PVA"),
        Activity(None, "BGTE", "Add an employee to a assistant", "Add an employee to a assistant", "# of employees added", True, 0.88, "PVA"),
        Activity(None, "BGTE", "Archiving", "Archiving", "# of docs", True, 0.2, "PNVA"),
        Activity(None, "BGTE", "Archiving - prepare new binder", "Archiving - prepare new binder", "# of times process was done", True, 7.03, "PNVA"),
        Activity(None, "BGTE", "Archiving wrong trips", "Archiving wrong trips", "# of trips", True, 0.45, "PNVA"),
        Activity(None, "BGTE", "Call", "Call", "# of minutes", True, 1, "PVA"),
        Activity(None, "BGTE", "Correcting trip after getting an e-mail", "Correcting trip after getting an e-mail", "# of docs", True, 3.54, "QEF"),
        Activity(None, "BGTE", "Cost center checking Reisenstrage for posted trips", "Cost center checking Reisenstrage for posted trips", "# of trips", True, 3.34, "QIF"),
        Activity(None, "BGTE", "Emails with no answer", "Emails with no answer", "# of emails", True, 0.24, "PNVA"),
        Activity(None, "BGTE", "Open/ log on into Wintrip", "Open/ log on into Wintrip", "# of times process was done", True, 1.36, "PVE"),
        Activity(None, "BGTE", "Payment in cash", "Payment in cash", "# of docs", True, 2.63, "PNVA"),
        Activity(None, "BGTE", "Posting trips", "Posting trips", "# of docs", True, 0.46, "PVA"),
        Activity(None, "BGTE", "Processing trips", "Check KM on internet", "# of destinations", True, 0.89, "PVA"),
        Activity(None, "BGTE", "Processing trips", "Processing big trips", "# of trips", True, 0.0, "PVA"),
        Activity(None, "BGTE", "Processing trips", "Processing trips", "# of trips", True, 1.78, "PVA"),
        Activity(None, "BGTE", "Processing trips", "Processing trips with KM", "# of trips", True, 2.32, "PVA"),
        Activity(None, "BGTE", "Repatriation (1xmonth)", "Repatriation (1xmonth)", "# of boxes", True, 17.23, "PNVA"),
        Activity(None, "BGTE", "Reset the password", "Reset the password", "# of passwords", True, 0.67, "PVA"),
        Activity(None, "BGTE", "Reverse trip", "Reverse trip", "# of reversals", True, 1.96, "QEF"),
        Activity(None, "BGTE", "Searching for an email", "Searching for an email", "# of emails", True, 0.0, ""),
        Activity(None, "BGTE", "Sorting Trips after entering into the system (Wintrip,SAP,Archiv)", "Sorting Trips after entering into the system (Wintrip,SAP,Archiv)", "# of trips", True, 1.84, "PNVA"),
        Activity(None, "BGTE", "Sorting Trips before enter into the system (by PersNo)", "Sorting Trips before enter into the system (by PersNo)", "# of trips", True, 0.2, "PVE"),
        Activity(None, "BGTE", "Special Client Request", "Special Client Request", "# of minutes", True, 1, "PVE"),
        Activity(None, "BGTE", "Trackers", "Mail tracker", "# of line items/emails", True, 0.32, "QAPP"),
        Activity(None, "BGTE", "Trackers", "Packet tracker", "# of times process was done", True, 0.32, "QAPP"),
        Activity(None, "BGTE", "Trackers", "Volume tracker", "# of times process was done", True, 1.57, "QAPP"),
        Activity(None, "BGTE", "Trip with error_check bills and write email", "Trip with error_check bills and write email", "# of trips", True, 2.61, "QEF"),
        Activity(None, "BGTE", "Unpack post", "Unpack post", "# of trips", True, 0.47, "PVE"),
        Activity(None, "BGTE", "Writing emails", "Writing emails", "# of emails", True, 1.74, "PVE"),
        Activity(None, "BGTE", "Writing emails", "Writing emails with attachment scanned", "# of emails", True, 2.66, "PVE"),
        Activity(None, "BGTE", "Writing emails", "Writing non standard emails", "# of emails", True, 0.0, "PVE"),
    ]
    for activity in activities:
        try:
            activity.save()
        except IntegrityError as e:
            print e


