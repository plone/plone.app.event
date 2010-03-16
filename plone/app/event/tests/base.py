from Products.Five.zcml import load_config
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

ptc.installPackage('plone.app.event')

@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import plone.app.event
    load_config('configure.zcml', plone.app.event)
    ptc.installPackage('plone.app.event')
    fiveconfigure.debug_mode = False

setupPackage()

ptc.setupPloneSite(extension_profiles=['plone.app.event:default'])

class EventTestCase(ptc.PloneTestCase):
    """ Base class for plone.app.event tests """

class EventTypeTestCase(atcttestcase.ATCTTypeTestCase):
    """ """

class EventFieldTestCase(atcttestcase.ATCTFieldTestCase):
    """ """

class EventIntegrationTestCase(atctftestcase.ATCTIntegrationTestCase):
    """ """
