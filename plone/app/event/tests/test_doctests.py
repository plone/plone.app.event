import doctest
from interlude import interact

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    '../recurrence.txt',
]

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact,}
        ) for docfile in DOCFILES
    ])
    return suite