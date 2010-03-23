import zope.interface
from Products.CMFDefault.formlib.vocabulary import SimpleVocabulary
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from Products.ATContentTypes import ATCTMessageFactory as _

def reccurencevocabulary(context):
    return SimpleVocabulary.fromTitleItems([(-1, -1, _('None')),
                             (YEARLY, YEARLY, _('Yearly')),
                             (MONTHLY, MONTHLY, _('Monthly')),
                             (WEEKLY, WEEKLY, _('Weekly')),
                             (DAILY, DAILY, _('Daily')),
                             ])

