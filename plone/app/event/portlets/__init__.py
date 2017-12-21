# -*- coding: utf-8 -*-
from plone.app.event.base import find_ploneroot
from plone.app.event.base import find_site


def get_calendar_url(context, search_base):
    # search_base is always from the portal_root object. We won't include
    # the path from the portal root object, so we traverse to the calendar
    # object and call it's url then.
    calendar_url = None
    if search_base:
        portal = find_ploneroot(context)
        if isinstance(search_base, unicode):
            search_base = search_base.encode('utf8')
        calendar_url = portal.unrestrictedTraverse(
            search_base.lstrip('/')  # start relative, first slash is omitted
        ).absolute_url()
    else:
        site_url = find_site(context, as_url=True)
        calendar_url = '%s/event_listing' % site_url

    return calendar_url
