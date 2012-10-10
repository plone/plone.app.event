-*- coding: utf-8 -*-

==========================
 plone.app.event Settings
==========================

For testing, reset the timezone
>>> from plone.app.event.testing import set_timezone
>>> set_timezone(tz="UTC")

Oskar Öhman is a successful CEO of his startup company specialized in
Toys. He's a sharp thinker and an even sharper HTML programmer (he
thinks). His business to build cheap toys in China and sell them as
quality build in Finnland brings him quite a huge turnaround in profit.

With his new venture to throw kids parties where he can sell his toys,
he needs a system to schedule and announce events. One of his developers
installed him a Plone instance the other morning for him to play with.

Oskar open's his browser:

>>> from plone.testing.z2 import Browser
>>> browser = Browser(layer['app'])
>>> portal = layer['portal']
>>> portal_url = portal.absolute_url()

and logs in:

>>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
>>> browser.addHeader('Authorization', 'Basic %s:%s' %(SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
>>> browser.open(portal_url)

He is very happy of what he sees. He creates a new event for this
afternoon: "Kids Toy Party with Big Wins" and announces it in his
newsletter.

The next day he's very angry. No one showed up at the scheduled time.
A few parents showed up 2 hours late with their kids. What could have
gone wrong? He turns to his developers and tells them to fix this
problem. They tell him, that he simply needs to set a default timezone
in the Plone site setup to avoid making those mistakes again.

Default Timezone
----------------

Oskar opens the site setup:

>>> browser.getLink('admin').click()
>>> browser.getLink('Site Setup').click()
>>> browser.getLink('Event Settings').click()

Oskar can clearly see the current default settings:

>>> browser.getControl('Portal default timezone').displayValue
['UTC']

He think's that is not the appropriate timezone the portal has chosen
here. This is absurd. What does UTC stand for anyway? Clearly, timezones
are for chumps and every region on the world should use:

>>> browser.getControl('Portal default timezone').displayValue = ['Atlantic/Bermuda']
>>> browser.getControl('Save').click()

Every event he now creates will be set to the 'Atlantic/Bermuda'
timezone:

>>> browser.getLink('Event Settings').click()
>>> '-03:00' in browser.contents
True
