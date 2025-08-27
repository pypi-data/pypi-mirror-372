===============================
Using archives files with PyAMS
===============================

PyAMS_file package offers a few helpers to use archives files and extract their contents.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> import os, sys

    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_file import includeme as include_file
    >>> include_file(config)

    >>> from pyams_file.interfaces.archive import IArchiveExtractor


TAR archives
------------

    >>> extractor = config.registry.getUtility(IArchiveExtractor, name='application/x-tar')
    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.tar')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    'test_image.png'


BZip2 archives
--------------

    >>> extractor = config.registry.getUtility(IArchiveExtractor, name='application/x-bzip2')

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png.bz2')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    ''


BZip2 TAR archives
------------------

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.tar.bz2')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    'test_image.png'


GZip archives
-------------

    >>> extractor = config.registry.getUtility(IArchiveExtractor, name='application/x-gzip')

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png.gz')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    ''


GZip TAR archives
-----------------

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.tar.gz')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    'test_image.png'


ZIP archives
------------

    >>> extractor = config.registry.getUtility(IArchiveExtractor, name='application/zip')

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.zip')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    'test_image.png'


Combined archives
-----------------

You can extract all contents from an archive containing other archives!

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.tar.bz2.zip')
    >>> with open(img_name, 'rb') as file:
    ...     contents = list(extractor.get_contents(file))
    >>> len(contents)
    1
    >>> isinstance(contents[0], tuple)
    True
    >>> isinstance(contents[0][0], bytes)
    True
    >>> contents[0][0][:128]
    b'\x89PNG...'
    >>> contents[0][1]
    'test_image.png'
