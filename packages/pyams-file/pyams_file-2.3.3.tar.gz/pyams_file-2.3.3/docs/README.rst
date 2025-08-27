==================
PyAMS_file package
==================

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
<https://github.com/py-ams>`_.


What is PyAMS_file?
===================

PyAMS_file is a PyAMS extension package used to handle files storage into ZODB. Provided features
allow to create file fields attributes which, when associated with matching properties, will allow
storage of any file easilly.

Extensions also allow easy management of medias files, like images, videos or audios files, for
example to generate thumbnails of images files.

This package also provides an extension to PyAMS_i18n, which will allow to store and retrieve
translated versions of a given file in several languages.

Some helpers related to archives management are also provided.
