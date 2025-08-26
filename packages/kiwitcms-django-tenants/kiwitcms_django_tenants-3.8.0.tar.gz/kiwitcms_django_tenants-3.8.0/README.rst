kiwitcms-django-tenants
=======================

This is a fork of https://github.com/django-tenants/django-tenants at version 3.8.0,
https://github.com/django-tenants/django-tenants/releases/tag/v3.7.8, commit 7d82923.

It reverts the changes made in
https://github.com/django-tenants/django-tenants/pull/997 b/c they cause existing
Kiwi TCMS tests to fail and appear to be much more disruptive than what appears initially!
Kiwi TCMS needs the rest of the changes in order to become compatible with Django 5.2,
but we don't want to risk breaking production instances hence the fork!

For the full list of changes between the last known working version and the original 3.8.0 see:
https://github.com/django-tenants/django-tenants/compare/v3.7.0...v3.7.8
