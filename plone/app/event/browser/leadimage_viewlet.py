from Acquisition import aq_parent
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.layout.viewlets import ViewletBase


class LeadImageViewlet(ViewletBase):
    """plone.app.contenttypes LeadImageViewlet for Occurrence contexts, where
    the image might be defined on the parent object.
    """
    def update(self):
        parent = aq_parent(self.context)
        self.available = ILeadImage.providedBy(parent) and\
            True if getattr(parent, 'image', False) else False
