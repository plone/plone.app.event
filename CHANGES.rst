Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.2.8 (2020-09-07)
------------------

Bug fixes:


- Fixed deprecation warning for ``setDefaultRoles``.
  [maurits] (#3130)


3.2.7 (2020-04-20)
------------------

Bug fixes:


- Change markup for structured data schemas from ``data-vocabulary.org`` to ``schema.org``.
  Because google supports only schema.org - based definitions
  [1letter] (#312)


3.2.6 (2019-11-25)
------------------

Bug fixes:


- Fix Python2 vs. Python3 text and bytes handling in the calendar portlet. (#308)


3.2.5 (2019-10-12)
------------------

Bug fixes:


- Load zcml of ``plone.resource`` for our use of the ``plone:static`` directive.
  [maurits] (#2952)


3.2.4 (2019-06-27)
------------------

Bug fixes:


- Add regression-test for allowed_attributes. See https://github.com/zopefoundation/Zope/issues/397
  [pbauer] (#306)


3.2.3 (2019-03-21)
------------------

Bug fixes:


- fix SearchableText indexer for Python 3
  [petschki] (#302)


3.2.2 (2019-03-03)
------------------

New features:


- - Add title in view definition, to allow translations. [cekk] (#298)


Bug fixes:


- Close files in tests (#300)


3.2.1 (2018-10-30)
------------------

Bug fixes:

- Fixed searchable text indexer to avoid breaking when there is no text.
  [davisagli]
- iCalendar categories are exepected as a comma separated string, not as multiple entries.
  See https://www.kanzaki.com/docs/ical/categories.html
  Needs fixed iCalendar >4.0.2
  [jensens]


3.2.0 (2018-09-23)
------------------

New features:

- Remove ``Pragma: no-cache`` header for icalendar exports.
  The ``Pragma`` header is HTTP 1.0 and the caching strategy on icalendar exports should better be defined by integrators.
  [thet]

Bug fixes:

- Python 3 compatibility.
  [pbauer]

- Make sure to include the 'Content-Length' header for ical exports
  [frapell]

- Update plone.app.event resources. Requires plonetheme.barceloneta >= 1.9.
  [agitator]


3.1.1 (2018-06-04)
------------------

Breaking changes:

- Introduce ``spell_date`` and deprecate ``date_speller`` in ``plone.app.event.base``.
  spell_date does only optionally accept an context where date_speller the context was required.
  [thet]

- Use plone i18n domain.
  [gforcada]

Bug fixes:

- Remove obsolete event_icon.png and corresponding css rule.
  Fixes: #283.
  [thet]

- Fix CSS syntax error in event.css
  [robbuh]

- Fix icalendar export for folderish events which are containers with a ``__getitem__`` method.
  [thet]

- Python 3 compatibility.
  [pbauer]

- Fix future_events French translation.
  [vincentfretin]

3.1 (2018-02-04)
----------------

New features:

- When setting start and end via the IEventAccessor, convert it to a Python datetime with timezone information.
  [thet]

- iCal export:
  - More response headers.
  - Support property parameters.
  - Add ``geo`` for (lat, lng) geolocation coordinates. This method is not implemented and can be used by addons to provide that feature.
  - Factor-out all event components from ``ICalendarEventComponent.to_ical`` method into separate properties, so that individual properties can be easier overloaded in subclasses.
  - Check, if event is really an event before ical-exporting. Fixes a problem when a collection mixes event and non-event like result objects.
  - Add ``rel="nofollow"`` to ical export links for robots to not download them.
  [thet]

- add full danish translation
  [tmog]

Bug fixes:

- Add Python 2 / 3 compatibility.
  [pbauer]
- Language independence for fields: `start`, `end`, `whole_day`, `open_end`
  [agitator]

- iCalendar import: Fix usage of ``sync_uid``, which wasn't correctly implemented since plone.app.event 2.0.
  [thet]

- Raise ``AttributeError`` when attempting to index an empty location attribute value.
  [thet]

- Fix portlet get_calendar_url with unicode search_base.
  [bsuttor]

- fallback search base URL for calendar/event portlets to NavigationRoot [petschki]


3.0.7 (2017-11-24)
------------------

Bug fixes:

- Fixed check for events iterable in Zope 4. [davisagli]


3.0.6 (2017-09-05)
------------------

Bug fixes:

- Improve the JavaScript to wait for the PickADate pattern to be initialized.
  Follow better JS practices.
  [thet]

- Remove broken floating layout of start, end, whole_day and open_end fields.
  [thet]


3.0.5 (2017-07-03)
------------------

New features:

- option to override thumb /icon behavior individually for portlet (suppress thumbs, thumb size)
  https://plone/Products.CMFPlone#1734 [fgrcon]
  applied https://github.com/plone/Products.CMFPlone/issues/1483
  [fgrcon]

Bug fixes:

- fixed css-classes for thumb scales ...
  https://github.com/plone/Products.CMFPlone/issues/2077
  [fgrcon]


3.0.4 (2017-02-12)
------------------

Bug fixes:

- Fix views should show the next upcoming recurrence of event.
  Fixes: https://github.com/plone/plone.app.event/issues/185
  [allusa]


3.0.3 (2016-11-17)
------------------

Bug fixes:

- Remove requirement of ``collective.elephantvocabulary`` which is no longer used.
  [davisagli]


3.0.2 (2016-10-05)
------------------

Breaking changes:

- Really remove Plone 4 compatibility code.
  [thet]

Bug fixes:

- Fix format of tooltip in calendar portlet.
  Fixes: https://github.com/plone/Products.CMFPlone/issues/1046
  [fgrcon]

- Fix bug when creating indexes on install. It was not detecting existing indexes correctly.
  [vangheem]

- Do not index `sync_uid`, `start` and `end` fields if they are empty.
  [bsuttor]

- Update french translations.
  [bsuttor]

- Fixing a typo in dutch translations.
  [andreesg]



3.0.1 (2016-09-16)
------------------

Bug fixes:

- Update Traditional Chinese Translations.
  [l34marr]


3.0 (2016-08-12)
----------------

Breaking changes:

.. note::
    This release depends on ``plone.app.z3cform >= 2.0.1``, which is only available for Plone 5.1.
    This is a backwards incompatible change, which satisfy a major version change for plone.app.event.
    Consequently, Plone 4 compatibility code will be removed in this release.

New features:

- Use ``schema.URI`` instead of ``schema.TextLine`` for ``event_url`` field.
  [thet]

- Make JavaScript date/time update work with optional start/end dates.
  [thet]

- Make use of more generic selectors in JavaScript, so that JavaScript works also for derived classes.
  [thet]

- Configure custom css classes for all event behavior fields.
  This makes it easier to use same selectors also for derived behaviors.
  Needs ``plone.app.z3cform >= 2.0.1``.
  [thet]

- Use ``plone.autoform.directives`` for manipulating field widgets instead of overriding the default Fieldwidget adapters.
  [thet]

Bug fixes:

- Fixed possible cross site scripting (XSS) attack in location field.  [maurits]

- Remove Archetypes based JavaScript code.
  [thet]

- Don't validate the ``validate_start_end`` invariant, if start or end are ``None``.
  This can happen on non-required, default empty start or end fields during editing.
  [thet]


2.0.9 (2016-05-15)
------------------

New features:

- Changed the color of the navigation in the calendar widget to grey(from blue) using inherit.
  see https://github.com/plone/Products.CMFPlone/issues/1445
  [janga1997]


2.0.8 (2016-04-29)
------------------

New:

- Added short-names for behaviors.
  [jensens]

Fixes:

- Don't break ``base.dates_for_display`` and the ``formatted_date`` content provider, if event object has no start or end dates.
  It might come from a potential event.
  [thet]


2.0.7 (2016-03-31)
------------------

New:

- Translation locales of plone.app.event to Russian [serge73]

Fixes:

- When trying to access an occurrence in the future outside the range of indexed occurrences, do not raise ``StopIteration``.
  Instead fall back to raise ``AttributeError``.
  [frapell]

- Ensure that unittests reset the timezone information
  [do3cc]


2.0.6 (2016-01-08)
------------------

Fixes:

- Change the behaviors text getter to use ``output_relative_to`` with the
  current context. This correctly transforms relative links. See:
  https://github.com/plone/plone.app.textfield/pull/17
  [thet]


2.0.5 (2015-11-25)
------------------

New:

- Show thumbs when leadimage behavior enabled for eventtype:
  see  https://github.com/plone/Products.CMFPlone/issues/1226
  [fgrcon]

Fixes:

- Cleanup tasks: Only install the plone.app.widgets profile for Plone 4.3.
  Remove the unnecessary ``plone50`` setup.py extra section. Fix
  plone.app.event to also work with plone.app.z3cform versions below < 1.0.
  [thet]

- Cleanup buildout: Remove sources.cfg, versions.cfg, test.cfg, test-43.cfg and
  test.cfg. Since this package is merged, it doesn't make much sense to
  maintain separate version and sources files to extend from. Tests and
  development environment is built in the buildout.cfg and buildout-43.cfg
  files. Remove bootstrap.py - use ``virtualenv .; ./bin/pip install
  zc.buildout`` instead.
  [thet]

- In tests, use ``selection.any`` in querystrings.
  Issue https://github.com/plone/Products.CMFPlone/issues/1040
  [maurits]


2.0.4 (2015-10-28)
------------------

Fixes:

- Fixed the occurrences calculation to reliably return an Event instead of
  Occurrence object for the originating event. There was a bug introduced by a
  newer pytz version.
  [thet]


2.0.3 (2015-09-27)
------------------

- Plone 4 compatibility for ``get_default_page`` import.
  [thet]


2.0.2 (2015-09-21)
------------------

- Update French translations
  [enclope]

- Resolve deprecation warning for getDefaultPage.
  [jensens]

- Fix word break on event linsting template
  [sneridagh]


2.0.1 (2015-09-20)
------------------

- Enable event-portlet by default.
  Fixes https://github.com/plone/Products.CMFPlone/issues/760
  [pbauer]

- Prevent negative number of items in event-portlet.
  [pbauer]

- Remove unittest2 dependency.
  [gforcada]

- Resolve deprecation warning for getDefaultPage.
  [fulv]


2.0 (2015-09-11)
----------------

- Updated basque translation
  [erral]


2.0b2 (2015-08-20)
------------------

- Unified event_listing style with plonetheme.barceloneta styles and added svg
  icons.
  [agitator]

- initialize events.js javascript after all patterns are initialized.
  [garbas]

- removing dependency on plone.app.contenttypes that introduce with latest
  changes to portlets code.
  [garbas]


2.0b1 (2015-07-18)
------------------

- Make configlets titles consistent across the site, first letter capitalized.
  [sneridagh]


2.0a13 (2015-07-15)
-------------------

- Fix some design issues in ``event_listing``.
  [pbauer]

- Remove superfluous ``for`` in behavior registrtions, which do not have a
  ``factory``.
  [fulv]

- For event listings, view-cache the ``events`` method, which is directly used
  in templates and also caches collection results instead of the
  ``_get_events`` method.
  [thet]

- Show only upcoming occurrences in the for ``@@event_summary`` for events with
  occurrences. On the last occurrence, only a link to all occurrences via
  ``@@event_listing`` is shown.
  [thet]

- Translation updates (num_more_occurrences).
  [thet]

- For event listings on collections, use the collection's ``item_count``
  attribute to limit the batch size.
  [thet]

- For the event portlet, don't cache the list of events on memoize instance,
  which creates a write transaction. Remove the caching until a solid cache key
  is found, which also works for multiple portlet instances.
  [thet]

- BBB portlets: do the version comparison with LooseVersion, so that
  Plone-style development version numbers like ``2.5.4.dev0`` also work.
  [thet]

- Let ``date_speller`` return the short, 2-letter weekday abbreviation instead
  of a 3-letter one.
  [thet]

- Remove inconsistency in date_speller and rename ``month`` and ``wkday`` keys
  to ``month_name`` and ``wkday_name``. Introduce ``month``, the non-zero
  padded numeric value of the current month, ``month2``, the zero-padded one,
  ``wkday``, the weekday number and ``week``, the weeknumber of the current
  year.
  [thet]

- Make configlets titles consistent across the site, first letter capitalized
  [sneridagh]


2.0a12 (2015-06-05)
-------------------

- Unwrap search_base for portlets, as it might be wrapped by the portlet
  renderer class. Fixes an error with getting the events to display.
  [thet]

- Import BBB superclasses from  plone.app.portlets.portlets.base so it works
  with plone.app.portlets 3.0 and up
  [frapell]


2.0a11 (2015-05-13)
-------------------

- Rerelease, because one of our test servers complains about the
  previous release.
  [maurits]


2.0a10 (2015-05-13)
-------------------

- For ``event_listing`` on Collections, ignore the Collection's sorting and use
  what the event listing's mode defines for sorting.
  [thet]

- Add support for Collections as data source for calendar and event portlets.
  [thet]

- Extend Collection support on ``event_listing`` for content items providing
  ``ISyndicatableCollection``.
  [thet]


2.0a9 (2015-05-04)
------------------

- Support for ``contentFilter`` on request for ``event_listing``.
  [thet]

- Fix ``ImageScalingViewFactory`` and add a custom ILeadImage viewlet for
  Occurrences. Fixes the display of ILeadImage images from the originating
  event in event views of occurrences by delegating to the parent object.
  [thet]

- Fix Plone 4.3 BBB z3c.form portlets to show their fields in Add/Edit Forms.
  [thet]

- Update Japanese translation.
  [terapyon]

2.0a8 (2015-03-26)
------------------

- Remove ``get_location`` view helper method. This was used to allow external
  addons (specifically ``collective.venue``) to override it and return a html
  link to a location object instead. Instead of this hack, which also only
  works for the location use case, override the necessary templates in your
  addons. In case of doubt, simplicity outweight extensibility options.
  [thet]

- Change ``adapts`` and ``implements`` to their decorator equivalents
  ``adapter`` and ``implementer``.
  [thet]

- Change ``event_listing`` to search only in current context and below, not the
  whole portal by default. Remove the setting ``current_folder_only``, which
  was annotated to the context. Since the collection support is much better now,
  use them for custom searches.
  [thet]

- Fix a bug in displaying the ``event_listing`` on Collections. Show the date
  filter on Collections, if no start/end critierias are given in the
  Collection's query.
  [thet]

- Add a CSS class for the timezone in the events portlet and the
  ``event_summary`` view.
  [mitakas]

- In the ``event_summary`` view, change the ``event-timezone`` list-item class
  to ``event-date``.
  [thet]


2.0a7 (2015-03-13)
------------------

- In the event_view, use the ``#parent-fieldname-text`` wrapper for text
  output, because of consistency.
  [thet]


2.0a6 (2015-03-04)
------------------

- Some Plone 5 related js improvements
  [vangheem]

- Use Plone 5 imports from plone.app.z3cform and make plone.app.widgets a soft
  dependency.
  [vangheem]

- Remove support for ``plone.app.collection`` and ``ATTopic`` - plone.app.event
  2.x is Dexterity only.
  [thet]

- Fix ``construct_calendar`` in plone.app.event.base to also return events for
  the first day in the calendar month.
  [thet]

- Remove ``data_postprocessing`` logic, which was handling ``open_end`` and
  ``whole_day`` events and was manipulating the object on form submission.
  Instead, just adapt start/end dates on indexing and when accessing them via
  ``IEventAccessor``.
  [thet]

- Remove the ``plone.app.event.EventTypes`` vocabulary, which relied on
  temporaily creating types. It's used for importing ical files. It should be
  possible to figure out, which types might suitable for creating events from
  ical VEVENT entries.
  [thet]

- No need to return DateTime objects for the indexer.
  Products.DateRecurringIndex works with Python datetime objects.
  [thet]

- Whole day setting doesn't hide effective range anymore. Fixes issue #167.
  [thet]


2.0a5 (2014-10-23)
------------------

- Fix German translation for Monat.
  [thet]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project.
  [albertcasado, sneridagh]

- Update markup for portlets and change dt dl for ul li tags.
  [albertcasado]

- Added locales for Catalan and Spanish
  [sneridagh]


2.0a4 (2014-07-22)
------------------

- Restore Plone 4.3 compatibility.
  [datakurre]

- Fix event.js Javascript, which produced Javascript date parsing errors when
  changing the start date in Firefox. Firefox does not parse date string, which
  are only nearly ISO 8601 compatible, without a "T" between the date and time
  part. Chrome on the other hand interprets timezone naive date/time strings as
  UTC and returns it localized to the user's timezone, which leads to shifting
  date/time values. For more info see this Bug report:
  https://code.google.com/p/chromium/issues/detail?id=145198
  [thet]

- Do not set the simple_publication_workflow in the p.a.event test fixture.
  [timo]

- Add ``location`` indexer. ``location`` is a default metadata field in
  portal_catalog so we should provide that information by default.
  [saily]


2.0a3 (2014-05-06)
------------------

- Fix a rare issue with event_summary, where a object's UID cannot be found in
  the catalog.
  [thet]

- Update plone.formwidget.recurrence version dependency for plone.app.widgets
  support.
  [thet]


2.0a2 (2014-04-19)
------------------

- Re-add some BBB Assignment class attributes for calendar and event portlets
  to not break Plone upgrades.
  [thet]


2.0a1 (2014-04-17)
------------------

- Make use of new z3c.form DataExtractedEvent and register the
  data_postprocessing_handler for this event. This adjusts the start and end
  date according to whole_day and open_end.

- Use default_timezone DatetimeWidget property. All datetime objects from
  plone.app.widgets' DatetimeWidget now have this timezone, if not otherwise
  set by the user.

- Move controlpanel to Products.CMFPlone.controlpanel.

- Move vocabularies to plone.app.vocabularies and use plone.* instead of
  plone.app.event.* prefix for registry keys.

- Use default and defaultFactory properties for behavior schema definitions to
  provide sane defaults for z3c.form *and* programmatically created Dexterity
  types (e.g. via plone.dextterity.utils.createContentInContainer). For that to
  work, remove the Behavior factory classes, use the default AttributeStorage
  and let IEventBasic and IEventRecurrence behaviors derive from IDXEvent resp.
  IDXEventRecurrence.

- Remove data_postprocessing event subscriber.

- Remove Timezone field from IEventBasic behavior. Instead, store timezone
  information directly in the tzinfo object on start and end datetime objects.

- Remove Archetypes subpackage.

[thet, yenzenz, garbas]


1.2.3 (2014-04-17)
------------------

- Remove DL's from portlet templates, replacing it with semantically correct
  tags. Ref: https://github.com/plone/Products.CMFPlone/issues/163
  [khink]


1.2.2 (2014-04-15)
------------------

.. note::

    Methods used for the ``event_summary`` view have has been moved from the
    ``event_view`` to ``plone.app.event.browser.event_summary``. The
    ``occurrence_parent_url`` method has been removed.

- Simplify buildout infrastructure: Move base-test.cfg to test.cfg, move
  base.cfg to buildout.cfg, remove test-43.cfg, sources-dev.cfg and
  jenkins.cfg.
  [thet]

- Disable the edit bar on Occurrence objects. They are transient and cannot be
  edited. Remove the visual distinction between IEvent and IOccurrences in the
  event_summary view. The user is likely not interested, if a Occurrence or the
  original Event is shown.
  [thet]

- Add a portal_type attribute to Occurrence objects and set it to 'Occurrence',
  so they can be easily identified without looking up interfaces.
  [thet]

- Add an event_listing view for IEvent objects to show all of it's occurrences.
  [thet]

- Change the occurrence listing in the @@event_summary view to directly link
  to the occurrence objects, rename the label to 'All dates' and also include
  the first date of the original event. The event_summary's max_occurrences
  attribute now also includes the starting event.
  [thet]


1.2.1 (2014-04-05)
------------------

- Changes in the Dexterity IRichText behavior migration: don't fail, if no
  Event type is found in the Dexterity FTI and remove the old IEventSummary
  behavior, if found.
  [thet]

- Don't use spamProtect script to render email address; it doesn't do much.
  [davisagli]

- Add an @@event_summary view, which provides the event summary listing in the
  event view for the purpose of reuse elsewhere. Allow the exclusion of
  information via an excludes list. The relevant methods are moved from
  event_view to event_summary.
  [thet]

- Improve markup of ``event_listing.pt`` in order to not break on IE 8.
  [rafaelbco]

- Use z3c.form for portlet forms.
  [bosim, davisagli]


1.2 (2014-03-01)
----------------

- Don't use spamProtect script to render email address; it doesn't do much.
  [davisagli]

- Drop usage of plone.formwidget.datetime and use plone.app.widgets instead.
  [garbas, davisagli]

- Fix label of 'Dates' fieldset.
  [esteele]


1.1b1 (2014-02-17)
------------------

.. note::

    The ``ploneintegration`` setuptools extra and GenericSetup profile have
    been removed for this version. This makes an integration into Plone and
    ``plone.app.contenttypes`` easier. Please remove them also in your setup
    and be sure to depend on ``plone.app.portlets>=2.5a1``!

.. note::

    In the event_view template, the event summary has changed from a table to a
    definition list layout. The event_view's next_occurrences method does not
    return a dictionary anymore, but only a list of next events. Also, the
    index_html template for Occurrences is renamed to event_view.  If you have
    custom view templates for IEvent or IOccurrence objects, you have to update
    them.

.. note::

    The plone.app.event.dx.event type has been moved to the
    plone.app.event:testing profile and the plone.app.event.dx:default profile
    has been removed. Use plone.app.contenttypes for a Dexterity based Event
    type, which utilizes plone.app.event's Dexterity behaviors.


- Remove Plone 4.2 compatibility. For more information see installation.rst in
  the docs.
  [thet]

- Move the plone.app.event.dx.event example type to the plone.app.event:testing
  profile and remove the plone.app.event.dx:default profile. Use the Event type
  from plone.app.contenttypes instead. Fixes #99.
  [thet]

- Remove the IEventSummary behavior and use the generic IRichText from
  plone.app.contenttypes instead. Fixes #140, Closes #142.
  [pysailor]

- Change the event detail listing in the event_view to be a definition list
  instead of a table, making it semantically more correct and the code less
  verbose. Fixes #141.
  [thet]

- For recurring events, don't show the last recurrence in the event view but
  the number of occurrences, queried from the catalog. Together with the
  previous generator-change this looping over the whole occurrnce list.
  [thet]

- Change the IRecurrenceSupport adapter's occurrence method to return again a
  generator, fixing a possible performance issue. Fixes #60.
  [thet]

- Replace RecurrenceField with plain Text field in the dx recurrence behavior.
  This reverts the change from 1.0rc2. We don't use form schema hints but an
  adapter to configure the widget. Closes #137, Fixes #131.
  [pysailor]

- Use attribute storage instead of annotation storage in all Dexterity
  behaviors. Closes #136, #95, Refs #20.
  [pysailor]

- Rename the Occurrence's 'index_html' view to 'event_view' for better
  consistency. This also fixes an issue with Solgema.fullcalendar.
  Closes #123.
  [tdesvenain]

- Fix get_events recurring events sorting, where it was only sorted by the
  brain's start date, which could easily be outside the queried range.
  [gyst]

- Avoid failing to create an event when zope.globalrequest.getRequest returns
  None on the post create event handler. This happens when creating an event
  during test layer setup time.
  [rafaelbco]

- iCalendar import: Also import objects, when the "last-modified" property was
  not changed. This conforms to the RFC5545:
  http://tools.ietf.org/search/rfc5545#section-3.8.7.3
  [jone]


1.1.a1 (2013-11-14)
-------------------

- Don't fail, if first_weekday isn't set in registry.
  [thet]

- plone.app.widgets compatibility
  [garbas]

- Set the first_weekday setting based on the site's locale when the default
  profile is activated.
  [davisagli]

- Allow query parameters for timezone vocabularies for filtering. Create the
  "Timezones" vocabulary from SimpleTerm objects with a value and title set
  for better support with plone.app.widgets AjaxSelectWidget.
  [thet]

- Remove "ploneintegration" from setuptools extra section and GenericSetup
  profile. PLEASE UPDATE YOUR INSTALLTIONS, to use Archetypes or Dexterity
  instead and to use plone.app.portlets 2.5a1! This change makes it easier for
  Plone to integrate plone.app.event.
  [thet]


1.0.5 (2014-02-11)
------------------

- For ical exports, remove X-WR-CALNAME, X-WR-CALID and X-WR-CALDESC.
  X-WR-CALNAME caused Outlook to create a new calendar on every import. These
  properties are not neccessary and not specified by RFC5545 anyways.
  Fixes #109, closes #132.
  [tomgross, thet]

- Add Traditional Chinese Translation. Closes #129.
  [l34marr]

- Changed `dates_for_display` and `get_location` to accept IEvent, IOccurrence
  and IEventAccessor objects and avoid confusion on using these methods.
  [thet]

- Added basque translation.
  [erral]

- Completed italian translation.
  [giacomos]


1.0.4 (2013-11-23)
------------------

- Register event.js Javascript as "cookable" to allow merging with other files
  and provide the "plone" global if it wasn't already defined.
  [thet]


1.0.3 (2013-11-19)
------------------

- Remove unnecessary data parameter on urllib2.urlopen, which caused a 404
  error on some icalendar imports from external resources (E.g. Google).
  [thet]

- Avoid "FileStorageError: description too long" on large icalendar imports by
  doing a transaction commit instead of a savepoint.
  [thet]

- Protect ical imports with the newly created plone.app.event.ImportIcal
  permission.
  [thet]

- plone.app.widgets compatibility.
  [garbas]

- Fix UnicodeDecodeError with special characters in body text. Fixes #108
  [zwork][agitator]


1.0.2 (2013-11-07)
------------------

- Fix the path for catalog search in ical importer. This fixes an issue, where
  no existing events could be found when importing a ical file again in virtual
  hosting environments. Also, search for any existing events, not only what the
  user is allowed to see.
  [thet]

- Fix Plone 4.2 buildout and test environment.
  [thet]


1.0.1 (2013-11-07)
------------------

- Fix ical import form import error. Translation string wasn't properly
  formatted. Also be forgiving about missing LAST-MODIFIED properties from ical
  files.
  [thet]


1.0 (2013-11-06)
----------------

- Implement synchronisation strategies for icalendar import.
  [thet]

- Implement icalendar import/export synchronisation and add sync_uid index and
  sync_uid fields for ATEvent and IEventBasic. This follows RFC5545, chapter
  "3.8.4.7. Unique Identifier". The sync_uid index can also be used for any
  other synchronisation tasks, where an external universally unique identifier
  is used.
  [cillianderoiste, thet]

- Don't show the repeat forever button in the recurrence widget.
  [thet]

- Fix icalendar export for collections and Archetype topics. Fixes #104.
  [thet]

- Don't include occurrences in icalendar exports of event_listing, but include
  the original event with it's recurrence rule. Fixes #103.
  [thet]

- Don't include the recurrence definition when doing icalendar exports of
  individual occurrences. Fixes: #61.
  [thet]

- Restore Javascript based edit-form functionality to set end dates depending
  on start dates with the same delta of days as initialized, as developed by
  vincentfretin back at plone.app.event's birth.
  [thet]

- Deprecate the plone.app.event.dx.event type and plone.app.event.dx:default
  profile.  Please create your own type based on plone.app.event's Dexterity
  behaviors or use the "Event" type from plone.app.contenttypes. The
  plone.app.event:default profile is sufficient also for Dexterity-only based
  installations.
  [thet]

- Remove the behaviors plone.app.relationfield.behavior.IRelatedItems adn
  plone.app.versioningbehavior.behaviors.IVersionable from the Dexterity
  example type. We don't depend on these packages and won't introduce an
  explicit dependency on it.
  [thet]

- In portlet calendar and events, don't use the search_base directly to
  constuct calendar urls. The search base always starts from the Plone site
  root, which led to wrong urls in Lineage subsites.
  [thet]

- Don't validate end dates for open ended events, so open ended events in the
  future can be saved via the form. Fixes #97
  [gyst]

- Ical importer: Fix default value for imported attendees and categories.
  Return an empty tuple instead of None so that the edit form can be rendered.
  [cillianderoiste]

- Fix event_listing view on Collections to expand events. Fixes #91, Fixes #90.
  [thet]

- Don't show the event_listing_settings view in the object actions for
  event_listings on Collections or Topics, as it doesn't make sense there.
  [thet]

- Fix case, where the events, which started before a queried timerange and
  lasts into the timerange were not included in the list of event occurrences.
  [thet]

- Fix wrong result set with "limit" applied in get_events. Limiting for
  occurrence-expanded events can just happen after all occurrences are picked
  up in the result set, otherwise sorting can mess it up.
  [petschki]

- Indexer adapter for SearchableText: fixed encoding inconsistencies.  Always
  return utf-8 encoded string while using unicode internally.
  [seanupton]

- In test-setup, explicitly install DateRecurringIndex instead of extending
  it's test layer fixture. This should finally fix #81, where other tests
  couldn't be run when not extending the DRI or PAE test fixture layers.
  [thet]

- Support the @@images view for IOccurrence objects by using a factory, which
  returns a AT or DX specific view depending on the Occurrence's parent.
  [thet]

- Switch off linkintegrity checks during upgrade from atct to pae.at.
  [jensens]

- Remove event and calendar portlet assignments on plone.rightcolumn.
  Integrators should do assignments themselfes, as they are likely different
  from the standard assignment.
  [thet]

- Don't fail, if timezone isn't set.
  [gforcada]


1.0rc3 (2013-08-23)
-------------------

- Fix get_events with ret_mode=3, expand=True, without recurrence
  It was returning full object instead of IEventAccessor instances.
  This also fix event portlet with norecurrent events.
  [toutpt]


1.0rc2 (2013-07-21)
-------------------

- Introduce a BrowserLayer and register all views for it. Avoids view
  registration conflicts with other packages.
  [thet]

- For the recurrence behavior In z3c.form based Dexterity forms, use the
  RecurrenceField instead of a plain Text field. This ensures that the
  recurrence widget is used even for plain z3c.form forms without form schema
  hints. This change is forward-compatible and should not break any existing
  installations.
  [thet]

- In z3c.form based Dexterity forms, use plone.autoform form hints for widget
  parameters and remove the ParameterizedWidgetFactory. plone.autoform 1.4
  supports widget parameter form hints.
  [thet]

- Update french translations.
  [toutpt]

- Fix icalendar importer to support multiple-line EXDATE/RDATE definitions.
  [thet]

- Fix runtime error in icalendar importer.
  [gbastien]

- For the setup's tests extra, depend on plone.app.testing <= 4.2.2 until the
  Dexterity and Archetypes tests are split up and the tests don't have a hard
  dependency on Archetypes.
  [thet]

- Remove dependency on "persistent" to not use that one over the ZODB bundled
  package. "persistent" will become available as seperate package with ZODB 4.
  [thet]

- Declare mimimum dependency on plone.event 1.0rc1.
  [thet]

- Buildout infrastructure update.
  [thet]

- Remove deprecations.
  [thet]


1.0rc1 (2013-07-03)
-------------------

Please note, the next release will have all deprections removed.

- For events lasting longer than the day they start, include them in the
  construct_calendar data structure on each day they occur. Fixes #76.
  [thet]

- Fix ATEvent's StartEndDateValidator subscription adapter to correctly return
  error dicts.
  [thet]

- In the ATEvent migration step, call ObjectModifiedEvent for each migrated
  event to call off the data_postprocessing method, which assures correct time
  values in respect to timezones. Please note, the timezone must be set
  correctly before!
  [thet]

- Rename the formated_date and formated_start_date content providers to
  have the correct spelling of "formatted". Doing this change now while this
  package's adoption is not too wide spread.
  [thet]

- Use same i18n field and error message strings for ATEvent and DX behaviors.
  [thet]

- Let plone.app.event.base.get_events always do a query with a sort definition,
  even if we are in expand mode and do a sort afterwards again. We need this to
  get stable results when having a sort_limit applied. Fixes an issue where the
  events_portlet did show the next events with an offset of some days.
  [thet]

- For the event and calendar portlets, use UberSelectionWidget to select the
  search base path to make this field actually usable.
  [thet]

- Remove ICalendarLinkbase adapter, which provided URLs to a calendar view.
  Instead, for event and calendar portlet links, the searchbase setting path
  is used to link to it or as fallback to call event_listing on ISite root.
  [thet]

- As like in event_view, use the get_location function for supporting location
  references in event_listing and portlet_events. Implement get_location just
  as a simple wrapper - handling of references must be provided by external
  packages, like collective.venue.
  [thet]

- Fixed unicode issue in event_view with non-ascii location strings and
  of referenced locations via collective.venue.
  [thet]

- In event_listing views in "past" or "all" modes, do a reverse sort on the
  results, starting with newest events.
  [thet]

- Create an Python based import step to properly set up the portal catalog.
  This avoids clearing the index after importing a catalog.xml. This import
  steps obsoletes the ploneintegration catalog.xml import step also.
  [thet]

- Add a event listing settings form, which allows configuration of the event
  listing view via annotations on the context.
  [thet]

- For the event listing view, accept SearchableText and tags request parameters
  for filtering the result set.
  [thet]

- For default_start and default_end, return a datetime with minute, second and
  microsecond set to 0.
  [thet]

- Don't overload ATEvent's subject widget label and help texts but use AT and
  DX standard label_tags and help_tags messages.
  [thet]

- Fix compact event edit form layouts and don't float the recurrence widget.
  [thet]

- Change default listing mode in event_listing and replace "All" with seperate
  "Future" and "Past" buttons.
  [thet]


1.0b8 (2013-05-27)
------------------

- Fix OccurrenceTraverser to fallback to plone.app.imaging's ImageTraverser, if
  present and thus support image fields on plone.app.event based types.
  [thet]

- Change the AT validation code to an subsciption adapter. This allows reliable
  validation for types derived from ATEvent, which wasn't the case with the
  post_validate method.
  [thet]

- More compact layout for AT and DX edit forms.
  [thet]

- Add open_end option for Dexterity behaviors and Archetypes type.
  [thet]

- For whole_day events, let dates_for_display return the iso-date
  representation from date and not datetime instances.
  [thet]

- Remove support of microseconds and default to a resolution of one second for
  all datetime getter/setter and conversions. Microseconds exactness is not
  needed and dateutil does not support microseconds which results in unexpected
  results in comparisons.
  [thet]

- Changing the timezone in events is a corner case, so the timezone field is
  moved to the "dates" schemata for AT and DX.
  [thet]

- Remove font-weight bold for monthdays and font-weight normal for table header
  in portlet calendar. Set div.portletCalendar with to auto instead of
  unnecessary 100% + margin. Align with plonetheme.sunburst.
  [thet]

- Let the IRecurrenceSupport adapter return the event itself, when the event
  starts before and ends after a given range_start. Fixes a case, where
  get_events didn't return a long lasting event for a given timeframe with
  expand set to True.
  [thet]

- Let the @@event_listing view work on IATTopic and ICollection contexts.
  [thet]

- In event_view, handle the case that the location field is not of type
  basestring but a reference to another object, for example provided by
  collective.venue.
  [thet]

- Use plone.app.event's MessageFactory for ATEvent.
  [thet]

- Let EventAccessor for Archetypes based content type return it's values from
  property accessors instead properties directly. This let's return the correct
  value when an property get's overridden by archetypes.schemaextender.
  [thet]

- Deprecate upgrade_step_2 to plone.app.event beta 2, which is likely not
  necessary for any existing plone.app.event installation out there.
  [thet]

- For the Archetypes based ATEvent migration step, do a transaction.commit()
  before each migration to commit previous changes. This avoids running out of
  space for large migrations.
  [thet]

- Let IEventAccessor adapters set/get all basestring values in unicode.
  [thet]

- Add and install plone.app.collection in test environment, as we cannot assume
  that it's installed.
  [thet]

- Re-Add cmf_edit method for ATEvent to ensure better backwards compatibility.
  Move related cmf_edit tests from Products.CMFPlone to plone.app.event.
  [thet]

- Add Event profile definition for ATEvent completly in order to remove it from
  Products.CMFPlone. ATEvent is installed by ATContentTypes automatically as
  part of upcoming plone.app.contenttypes merge.
  [thet]

- Optimize css by using common classes for event_listing and event_view.
  [thet]

- Add schema.org and hCalendar microdata to event_view and event_listing views.
  Fixes #2, fixes #57.
  [thet]


1.0b7 (2013-04-24)
------------------

- Don't show plone.app.event:default and
  plone.app.event.ploneintegration:prepare profiles when creating a Plone site
  with @@plone-addsite.
  [thet]

- Remove render_cachekey from portlet_events, since it depends on an
  undocumented internal _data structure, which must contain catalog brains.
  [thet]

- In tests, use AbstractSampleDataEvents as base class for tests, which depend
  on AT or DX event content.
  [thet]

- Introduce create and edit functions in IEventAccessor objects.
  [thet]

- API Refactorings. In base.py:
    * get_portal_events and get_occurrences_from_brains combined to get_events.
    * get_occurrences_by_date refactored to construct_calendar.
    * Renamings:
        - default_start_dt -> default_start,
        - default_end_dt -> default_end,
        - cal_to_strftime_wkday -> wkday_to_mon1,
        - strftime_to_cal_wkday -> wkday_to_mon0.

    * Remove:
        - default_start_DT (use DT(default_start()) instead),
        - default_end_DT (use DT(default_end()) instead),
        - first_weekday_sun0 (use wkday_to_mon1(first_weekday()) instead),
        - default_tzinfo (use default_timezone(as_tzinfo=True) instead).

  In ical:
    * Renamed construct_calendar to construct_icalendar to avoid same name as
      in base.py.

  BBB code will be removed with 1.0.
  [thet]

- Update translations and translate event_view and event_listing.
  [thet]

- Configure event_listing to be an available view on Collections, Folders,
  Plone Sites and Topics.
  [thet]

- Depend on plone.app.dextterity in ZCML, so that all DublinCore metadata
  behaviors are set up correctly.
  [thet]

- Backport from seanupton: IObjectModifiedEvent subscriber returns early on
  newly created event (Commit c60c8b521c6b1ca219bfeaddb08e26605707e17 on
  https://github.com/seanupton/plone.app.event).
  [seanupton]

- Calendar portlet tooltips css optimizations: max-with and z-index.
  [thet]

- Add Brazilian Portuguese translation
  [ericof]

- Add ical import feature, register action to enable it and add a object tab to
  the @@ical_import_settings form. .ics files can be uploaded or fetched from
  the net from other calendar servers.
  [thet]

- Since more ical related code is upcoming (importer), add ical subpackage and
  move ical related code in here.
  [thet]

- When exporting whole_day/all day events to icalendar, let them end a day
  after at midnight instead on the defined day one second before midnight. This
  behavior is the preferred method of exporting all day events to icalendar.
  [thet]

- Additionally to the 'date' parameter, allow passing of year, month and day
  query string parameters to the event_listing view and automatically set the
  mode to 'day' if a date was passed.
  [thet]

- Backport from plone.app.portlets: Don't fail on invalid (ambigous) date
  information in request (Commit a322676 on plone.app.portlets).
  [tomgross]

- Backport from plone.app.portlets: Use str view names for getMultiAdapter
  calls (commit c296408 on plone.app.portlets).
  [wichert]


1.0b6 (2013-02-14)
------------------

- Styles for event_listing date navigation.
  [thet]

- Add datepicker for day selection in event_listing view.
  [thet]

- Fix event_listing to search only for events in the current context's path.
  Allow "all" request parameter for no path restriction in searches.
  [thet]

- Backport change from seanupton: get_portal_events() fix: navroot path index
  incorrectly passed as tuple, now fixed to path string.
  [seanupton, thet]

- Fix get_portal_events to respect path for query if given in keywords.
  [thet]


1.0b5 (2013-02-11)
------------------

- Restore Python 2.6 compatibility by avoiding total_seconds method from
  timedelta instances in icalendar export.
  [thet]


1.0b4 (2013-02-08)
------------------

- Remove occurrences.html view because it's replaced by event_listing view.
  [thet]

- Changed Dexterity event-type title from "Event (DX)" to "Event" for
  consistent naming between Archetypes and Dexterity content types.
  [thet]

- Updated and synced translations (.pot and German translations).
  [thet]

- Use content-core fill/define metal definitions in all templates which use
  main_template's master macro.
  [thet]

- Calendar Portlet: Better portlet and tooltip styling. Drop usage of
  todayevent and todaynoevent classes. Fix Linking to calendar_listing.
  [thet]

- Event listing: Optimized layout and styles, mode switch, calendar-navigation,
  timespan header.
  [thet]

- Implement week and month mode for start_end_from_mode function.
  [thet]

- Add icalendar timezone support and properly export whole day events.
  Fixes #22, Fixes #71.
  [thet]

- Don't set icon_expr for the Dexterity content type and use css instead.
  [thet]

- Restore compatibility to Plone 4.3 by including the ploneintegration module
  also for Plone 4.3 but not 4.4.
  [thet]

- Version fix for z3c.unconfigure==1.0.1. This fix can be removed, once Plone
  depends on zope.configuration>=3.8.
  [thet]

- Add icon_export_ical.png from Products.ATContentTypes to plone.app.event.
  [thet]

- Configure first_day parameter for DateTime and Recurrence Widget (AT and DX).
  [thet]

- Configure the default_view of plone.app.event's ATEvent to be @@event_view.
  This prevents of referencing the old event_view from the plone_content skin
  layer to be used in some cases.
  [thet]

- Style the calendar portlet tooltips only for the calendar portlet.
  [thet]


1.0b3 (2012-12-18)
------------------

- Set the CalendarLinkbase urlpath to respect the search_base in calendar and
  event portlets.
  [thet]

- Depend on plone.app.portlets >= 2.4.0, since portlet_calendar needs the
  render_portlet view for it's ajaxification. This may break Plone 4.2
  integrations, until you make a buildout version fix.
  [thet]

- Remove dependency on Grok for the Dexterity behaviors.
  [thet]

- Just use classes instead of id's for the calendar portlet's page switcher.
  [thet]

- Reimplement the calendar page switcher from the calendar portlet with jQuery
  and remove the implicit dependency on KSS.
  [thet]

- Use event_listing instead of the search view in CalendarLinkbase for calendar
  and event portlets.
  [thet]

- Add new API functions:
  [thet]

  - date_speller to format a date in a readable manner,

  - start_end_from_mode to return start and end date accordin to a mode string
    (today, past, future, etc.),

  - dt_start_of_day and dt_end_of_day to set a date to the start of the day
    (00:00:00) and to the end of the day (23:59:59) for use in searches.

- Add new event_listing view to show previous, upcoming, todays and other
  events in a listing.
  [thet]

- Fix EventAccessor for ATEvent to correctly return the description.
  [thet]

- In portlet_calendar, grey-out previous and next month dates by making them
  transparent.
  [thet]


1.0b2 (2012-10-29)
------------------

- Fix ical export of RDATE and EXDATE recurrence definitions. Fixes #63.
  [thet]

- Align ATEvent more to Archetypes standards and avoid AnnotationStorage and
  ATFieldProperty. We needed to remove the ATFieldProperty for the timezone
  field for a custom setter. By doing so, the other two ATFieldProperties were
  changed too. This way, the ATEvent API gets more consistent. For a convenient
  access to ATEvent as well as dextterity based event types, use the
  IEventAccessor from plone.event.interfaces. Upgrade step from pre 1.0b2 based
  ATEvent types is provided.
  [thet]

- Treat start/end datetime input always as localized values. Changing the
  timezone now doesn't convert the start/end values to the new zone (AT, DX).
  [thet]

- Fix moving start/end dates when saving an unchanged DX event (issue #62).
  [thet]

- Portlet assignment fix. Now both - calendar and event portlet - are
  installed.
  [thet]


1.0b1 (2012-10-12)
------------------

- Add the calendar portlet by default when installing plone.app.event.
  [thet]

- Backport changes from "merge plip-10888-kss branch" in plone.app.portlets.
  KSS attributes still left in place for backwards compatibility.
  [thet]

- Buildout infrastructure update.
  [thet]

- Icalendar export of attendees almost according to the RFC5545 standard. At
  the moment, we do not distinguish between CN and CAL-ADDRESS in Plone, so we
  just put the attendee value to the CN and CAL-ADDRESS parameter. Fixes #24.
  [thet]

- Support microseconds for DateTime conversions. For recurrence rules,
  timezones are not supported due to a python-datetime limitation.
  [thet]

- Don't allow ambiguous timezones like 'CET', which also have implementation
  errors in DateTime. Force them to another zone. Timezones should be set
  explicitly anyways.
  [thet]

- Let EventOccurrenceAccessor return its own URL instead of its parent.
  Once again fixes #58.
  [thet]

- Fix calendar portlet header, which day names were shifted by one day since a
  incompatibility between the calendar module (0 is Monday) and the strftime
  function (0 is Sunday).
  [thet]

- Create an formated_date content provider, which takes an occurrence or event
  object when called and formats the start/end date and times for display. This
  content provider can be overridden for other contexts. E.g. the events
  portlet uses just shows the start date and not the end date.
  [thet]

- Let IRecurrenceSupport adapter's occurrences method return as first
  occurrence the event object itself instead of an Occurrence object.
  Fixes #58.
  [thet]

- Include plone.event's new configure.zcml.
  [thet]

- For the ATEvent type, use a more specific IATEvent interface with IEvent and
  P.ATCT's IATEvent as bases. So we can provide adapters, overriding more
  general IEvent adapting adapters.
  [thet]

- Don't show start occurrence in "More occurrences" section in event_view.
  [thet]

- Create adapter ICalendarLinkbase which returns links to calendar views and
  can be overridden through a more specific implementation by addon products.
  For example, the portlet_calendar and portlet_events links to the @@search
  view can be changed to URLs to a real calendar view, if one is installed.
  [thet]

- For portlet_calendar and portlet_events configuration, make the workflow
  state selection optional. If nothing is selected, all states are searched.
  [thet]

- Add search_base (select path to search for events) and state (select review
  state for events to search) to portlet_calendar settings and search_base to
  portlet_events.
  [thet]

- Limit the amount of occurrences in the event view if the event yields
  more than 7 occurrences. Show only 6 occurrences and the last
  occurrence.
  [romanofski]

- More minor fixes.
  [thet]

  * Don't force DateTime conversion in query parameters of get_portal_events.
    The catalog index uses Python's datetime anyways.

  * Only set end date in _prepare_range to next day, if it's a date and not
    datetime.

  * Register the Archetypes postprocessing event subscribers also for
    IObjectCreatedEvent.

- Fix #51, logical error with range_end parameter in get_portal_events.
  [thet]

- Fix test startup by not depending on getSite().translate, which is a
  filesystem script.
  [thet]

- Backport changes from davilima: Add safety check for False all_events_links.
  [davilima6]

- Make get_occurrences_by_date work for events which do not have
  IRecurrenceSupport (e.g. Dexterity events without the recurrence behavior).
  [thet]

- Don't run event handlers for ATEvent, if it doesn't provide IEvent.
  [thet]

- Fix utf-8 encoding problem with icalendar export.
  [rnix]

- Unregister ics_view for ATFolder and ATBTreeFolder as well in
  ploneintegration.
  [rnix]

- Workaround for buggy strftime with timezone handling in DateTime.
  See: https://github.com/plone/plone.app.event/pull/47
  [seanupton]

- Rebind portlet_calendar tooltips after ajax calendar reloads.
  [thet]

- Allow the refreshCalendar kss view also on Occurrence objects.
  [thet]

- Let portlet_events link to @@search for future and previous events for sites
  without the standard events folder.
  [thet]

- Moved docs/HISTORY.rst to CHANGES.txt.
  [seanupton]

- Calendar portlet search links now use @@search (from plone.app.search)
  instead of (since Plone 4.2) deprecated ./search (search.pt).  Requires
  recent plone.app.search changes.
  [seanupton]

- Integrate the plone.app.event-ploneintegration functionality for Plone
  versions without plone.app.event core integration (all current version)
  into this package for simplification.
  [thet]

- IEventSummary behavior added for body text on Dexterity event type,
  as well as a SearchableText indexer adapter for the Dexterity event
  type.
  [seanupton]

- Filter calendar portlet search URLs for each day to a whitelist of
  event portal_type values.  Prevents non-event add-on types with
  start/end fields from showing up in calendar, as defense against
  unintended consequences (add-ons could explicitly override this
  template if they define additional Event types).
  [seanupton]

- API refactoring:
  * Move all generic interfaces to plone.event,
  * Extend IEventAccessor adapters to also be able to set attributes.
  [thet]

- Copy plonetheme.sunburst styles for the calendar portlet to event.css. This
  way, the calendar portlet is nicely styled, even without sunburst theme
  applied.
  [thet]

- For Dexterity behaviors, use IEventRecurrence adapter to store attributes
  directly on the context.  This fixes that recurrence occurrences start and
  end dates were not indexed, because the DateRecurringIndex had not access to
  the recurrence attribute.
  [thet]

- IRecurrence adapter returns now acquisition-wrapped occurrence
  objects.
  [romanofski]

- Event portlet is now showing occurrences, sorted by start date.
  [romanofski]

- Moved whole_day field in directly after the end date to get a more logical
  group.
  [thet]

- Added dedicated timezone validator with fallback zone.

- Added traverser for occurrences. The event view is used to show
  individual occurrences.
  [romanofski]

- Broken paging in the calendar portlet has been fixed (#11).
  [romanofski]

- Make the start DateTime timezone aware and fix an issue where the start date
  was after the end date. Fixes: #8.
  [romanofski]


1.0a2 (2012-03-28)
------------------

- Add portlet GenericSetup registration for calendar and event portlet.
  [thet]

- API CHANGE: Use zope.annotation for behaviors, remove unnecessary factories,
  create IRecurrence adapter for access to occurrences.
  [thet]


1.0a1 (2012-03-12)
------------------

- Initial alpha release.
  [thet]
