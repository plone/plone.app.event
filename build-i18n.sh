#!/bin/sh
I18NDUDE=../../bin/i18ndude
$I18NDUDE rebuild-pot --pot plone/app/event/locales/plone.app.event.pot --create plone.app.event .
$I18NDUDE sync --pot plone/app/event/locales/plone.app.event.pot plone/app/event/locales/de/LC_MESSAGES/plone.app.event.po 
$I18NDUDE sync --pot plone/app/event/locales/plone.app.event.pot plone/app/event/locales/en/LC_MESSAGES/plone.app.event.po 
$I18NDUDE sync --pot plone/app/event/locales/plone.app.event.pot plone/app/event/locales/fr/LC_MESSAGES/plone.app.event.po 
$I18NDUDE sync --pot plone/app/event/locales/plone.app.event.pot plone/app/event/locales/it/LC_MESSAGES/plone.app.event.po 
$I18NDUDE sync --pot plone/app/event/locales/plone.app.event.pot plone/app/event/locales/pt_BR/LC_MESSAGES/plone.app.event.po 