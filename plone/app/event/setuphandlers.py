from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implements


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        """Prevents profiles, which should not be user-installable from showing
        up in the profile list when creating a Plone site.

        plone.app.event:default .. Necessary, if you plan to use a custom type
        and not install the provided ones. But not necessary when creating a
        Plone site.

        plone.app.event.ploneintegration:prepare .. Called by
        plone.app.event.ploneintegration:default and used to upgrade from older
        Plone sites.

        """
        return [u'plone.app.event:default',
                u'profile-plone.app.event.ploneintegration:prepare']
