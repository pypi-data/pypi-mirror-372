====================
PyAMS ZFiles package
====================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Doctests are available in the *doctests* source folder.


What is ZFiles?
===============

ZFiles is an extension package for PyAMS which allows to define a "files storage" environment.

This environment is very simple, and provides several APIs (for REST/JSON, XML-RPC
or JSON-RPC protocols) which allows applications to store and retrieve external files of any
type (maybe images, videos, PDF files...). Applications which are using the service just get a
unique ID (called OID) when they upload a new document, which can be stored by the applications
and used to retrieve them afterwards when needed.

ZFiles is just a storage manager for these documents; the lifecycle management is delegated to
the applications which use it as storage backend.
