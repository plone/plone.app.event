import unittest
import doctest
from interlude import interact

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    '../recurrence.txt',
]
DOCMODS = [
    'plone.app.event.timezone',
]

from zope.configuration import xmlconfig
import zope.component
import plone.app.event
def load_zcml(doctest_context):
    context = xmlconfig.file('meta.zcml', zope.component)
    xmlconfig.file('configure.zcml', zope.component, context=context)
    xmlconfig.file('configure.zcml', plone.app.event, context=context)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            globs={#'interact': interact,
                },
        ) for docfile in DOCFILES
    ])
    suite.addTests([
        doctest.DocTestSuite(docmod,
                             setUp=load_zcml,
                             optionflags=OPTIONFLAGS,
                             globs={'interact': interact, }
                             ) for docmod in DOCMODS
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
