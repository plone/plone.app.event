# -*- coding: utf-8 -*-
from plone.app.event.base import find_navroot
from plone.app.event.base import find_ploneroot

import six


def get_calendar_url(context, search_base):
    # search_base is always from the portal_root object. We won't include
    # the path from the portal root object, so we traverse to the calendar
    # object and call it's url then.
    calendar_url = None
    if search_base:
        portal = find_ploneroot(context)
        if six.PY2 and isinstance(search_base, six.text_type):
            search_base = search_base.encode('utf8')
        search_base = '/'.join(search_base.split('/')[2:])
        calendar_url = portal.unrestrictedTraverse(
            search_base.lstrip('/')  # start relative, first slash is omitted
        ).absolute_url()
    else:
        site_url = find_navroot(context, as_url=True)
        calendar_url = '%s/event_listing' % site_url

    return calendar_url
