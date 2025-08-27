==================
PyAMS_file package
==================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> import os, sys, tempfile
    >>> temp_dir = tempfile.mkdtemp()

Blos storage requires a blobs storage directory, which can only be used with a FileStorage,
ZEOStorage of RelStorage:

    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'file://{dir}/Data.fs?blobstorage_dir={dir}/blobs'.format(
    ...     dir=temp_dir)

    >>> import transaction
    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)
    >>> from pyams_file import includeme as include_file
    >>> include_file(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...
    Upgrading PyAMS file to generation 4...

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.dublincore.interfaces import IZopeDublinCore
    >>> from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
    >>> config.registry.registerAdapter(ZDCAnnotatableAdapter, (IAttributeAnnotatable, ), IZopeDublinCore)

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))
    >>> manager.push({'request': request, 'registry': config.registry})


Creating a file object from scratch
-----------------------------------

A File object can be created from a path or from a file object:

    >>> from pyams_file.file import File

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png')

    >>> with open(img_name, 'rb') as file:
    ...     file1 = File(file)
    >>> file1
    <pyams_file.file.File object at 0x...>

    >>> file2 = File(source=img_name)
    >>> file2
    <pyams_file.file.File object at 0x...>


Blobs references manager
------------------------

The blobs references manager is a local utility which is in charge of keeping internal references
to file *blobs*; when a content containing a file is created, a reference is added to this file;
if the content is duplicated, the file is not duplicated but a new reference is added to it.

If the file associated with the copy is modified afterwards, one of the references is removed and
replaced by a reference to a new blob file; when the number of references to a given file is
reduced to zero, the blob file is physically deleted.

    >>> from pyams_utils.registry import get_utility
    >>> from pyams_file.interfaces import IBlobReferenceManager
    >>> from pyams_file.tests import find_files
    >>> refs = get_utility(IBlobReferenceManager)
    >>> len(refs.refs)
    0
    >>> list(find_files("*.blob", os.path.join(temp_dir, 'blobs')))
    []


Defining file schema fields and properties
------------------------------------------

Doctests defined classes can't be persisted, so we use testing classes defined into
PyAMS_file.tests:

    >>> from pyams_file.tests import IMyInterface, MyContent

File schema fields provide validation methods:

    >>> source = 'This is my file content'
    >>> IMyInterface['data'].validate(source)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ('This is my file content', <InterfaceClass pyams_file.interfaces.IFile>, 'data')

Yes... A file fields requires... a File object!

    >>> value = File(source)
    >>> IMyInterface['data'].validate(value)

File fields value can also be provided as a tuple containing filename and a file-like object:

    >>> value = ('test.txt', File(source))
    >>> IMyInterface['data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (<pyams_file.file.File object at 0x...>, '<file-like object>', 'data')

    >>> from io import StringIO
    >>> value = ('test.txt', StringIO(source))
    >>> IMyInterface['data'].validate(value)

    >>> IMyInterface['data'].validate((123, StringIO(source)))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (123, <class 'str'>, 'data.filename')


Finally, let's try to validate special values:

    >>> from pyams_utils.interfaces.form import NOT_CHANGED, TO_BE_DELETED

    >>> IMyInterface['data'].validate(NOT_CHANGED)
    >>> IMyInterface['data'].validate(TO_BE_DELETED)

    >>> IMyInterface['required_data'].validate(NOT_CHANGED)
    >>> IMyInterface['required_data'].validate(TO_BE_DELETED)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.RequiredMissing


Let's now use properties fields; a File content can be set from a simple string:

    >>> content = MyContent()
    >>> content.data = 'This is my file content'
    Traceback (most recent call last):
    ...
    AttributeError: 'NoneType' object has no attribute 'add'

Why this error? It's because blob files have to be "parented" to their context to get a
database reference before being able to set their content:

    >>> from zope.location import locate
    >>> locate(content, app)

    >>> content.data = 'This is my file content'
    >>> content.data
    <pyams_file.file.File object at 0x... oid 0x... in <ZODB.Connection.Connection object at 0x...>>
    >>> content.data.__parent__ is content
    True
    >>> content.data.__name__
    '++attr++data'

The boolean value of a File object is based on the size of it's content:

    >>> bool(content.data)
    True

A simple "locate" call to define the parent is enough; another option can be to set the "__parent__"
attribute, or to set a value, for example, in a parent folder, like in:

    >>> app['content'] = content

When retrieving file content, you will notice that this content has been converting to bytes
(using UTF-8 encoding):

    >>> content.data.data
    b'This is my file content'
    >>> content.data.get_size()
    23
    >>> len(refs.refs)
    1
    >>> len(refs.refs[list(refs.refs)[0]])
    1
    >>> refs.refs[list(refs.refs)[0]]
    {<pyams_file.file.File object at 0x...>}
    >>> list(find_files("*.blob", os.path.join(temp_dir, 'blobs')))
    []

Why don't we have any file in the blobs directory? That's because our transaction hasn't been
committed yet!

    >>> transaction.commit()
    >>> len(list(find_files("*.blob", os.path.join(temp_dir, 'blobs'))))
    1

You can also provide a file-like object to set a file property content:

    >>> with open(os.path.join(temp_dir, 'data.txt'), 'w') as file:
    ...     _ = file.write('This is my file content')
    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = file

And finally, we can set a file property using a tuple containing a filename and a file object:

    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = ('data.txt', file)
    >>> content.data.content_type
    'text/plain'

File name can include an optional content-type, separated by a comma:

    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = ('data.txt; text/plain; charset=utf-8', file)
    >>> content.data.content_type
    'text/plain; charset=utf-8'

If provided file name contains punctuation or diacritics, they are automatically removed:

    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = ("da,tà-2'ç.txt", file)

    >>> content.data.filename
    'data-2c.txt'

Special values can be used to specify that a file should be left unchanged or deleted:

    >>> other_content = MyContent()
    >>> locate(other_content, app)
    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     other_content.data = file

    >>> other_content_data = other_content.data
    >>> other_content_data
    <pyams_file.file.File object at 0x...>

    >>> other_content.data = NOT_CHANGED
    >>> other_content.data.data
    b'This is my file content'
    >>> other_content.data is other_content_data
    True

    >>> other_content.data = TO_BE_DELETED
    >>> other_content.data is None
    True


Using a file as context manager
-------------------------------

Any File object can be used as a context manager, as a builtin *file* object; but to prevent
transactions problems (the transaction must be committed if you request a thumbnail just after
creating an image), this access is restricted to read-only mode:

    >>> with content.data as file:
    ...     print(file.read())
    ...     file.close()
    b'This is my file content'

    >>> with content.data as file:
    ...     try:
    ...         file.write(b'This is a new content')
    ...     finally:
    ...         file.close()
    Traceback (most recent call last):
    ...
    io.UnsupportedOperation: File not open for writing

Please note also that it's up to you to close the file object, as the context manager doesn't
keep a pointer to the opened file, to prevent ResourceWarning messages about unclosed files...


Iterating over file content
---------------------------

Instead of reading the whole file content in a single operation, you can iterate over file contents
by blocks of 64kb each:

    >>> for block in content.data:
    ...     print(block)
    b'This is my file content'


Copying a file
--------------

Copying a file should only generate a new reference into blobs manager, without creating a new
blob file:

    >>> from zope.copy import copy
    >>> copied_content = copy(content)
    >>> app['copy'] = copied_content
    >>> len(refs.refs)
    1
    >>> len(refs.refs[list(refs.refs)[0]])
    2
    >>> refs.refs[list(refs.refs)[0]]
    {<pyams_file.file.File object at 0x...>, <pyams_file.file.File object at 0x...>}

We can now change data of the copied content, to see that this added a reference to a new file,
and that the first reference was removed:

    >>> copied_content.data = 'This is a new content'
    >>> len(refs.refs)
    2
    >>> blob_refs = list(refs.refs.keys())
    >>> len(refs.refs[blob_refs[0]])
    1
    >>> len(refs.refs[blob_refs[1]])
    1

And we can remove copy data to remove a reference:

    >>> copied_content.data = None
    >>> len(refs.refs)
    1
    >>> blob_refs = list(refs.refs.keys())
    >>> len(refs.refs[list(refs.refs)[0]])
    1


I18n files properties
---------------------

I18n file properties are working exactly like normal I18n properties:

    >>> from pyams_file.tests import IMyI18nInterface, MyI18nContent

    >>> source = 'This is my test'
    >>> value = {'en': source}
    >>> IMyI18nInterface['data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ('This is my test', <InterfaceClass pyams_file.interfaces.IFile>, 'data')

    >>> IMyI18nInterface['required_data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ('This is my test', <InterfaceClass pyams_file.interfaces.IFile>, 'required_data')

    >>> value = {'en': File(source)}
    >>> IMyI18nInterface['data'].validate(value)
    >>> IMyI18nInterface['required_data'].validate(value)

    >>> value2 = {'en': (123, value)}
    >>> IMyI18nInterface['data'].validate(value2)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (123, <class 'str'>, 'data.filename')

    >>> value = {'en': ('test.txt', value)}
    >>> IMyI18nInterface['data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ({'en': <pyams_file.file.File object at 0x...>}, '<file-like object>', 'data')

    >>> IMyI18nInterface['required_data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ({'en': <pyams_file.file.File object at 0x...>}, '<file-like object>', 'required_data')

    >>> value = {'en': ('test.txt', StringIO(source))}
    >>> IMyI18nInterface['data'].validate(value)
    >>> IMyI18nInterface['required_data'].validate(value)

    >>> value = {'en': NOT_CHANGED}
    >>> IMyI18nInterface['data'].validate(value)
    >>> IMyI18nInterface['required_data'].validate(value)
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.RequiredMissing

This last error is raised because field is not bound to any context; we have to create a context
and bind it's field to it:

    >>> i18n_content = MyI18nContent()
    >>> locate(i18n_content, app)
    >>> i18n_content.required_data = {'en': File(source)}
    >>> field = IMyI18nInterface['required_data'].bind(i18n_content)
    >>> field.validate(value)


Let's now use our I18n fields properties:

    >>> i18n_content = MyI18nContent()
    >>> locate(i18n_content, app)
    >>> i18n_content.data = {'en': 'This is my I18n content'}
    >>> i18n_content.data
    {'en': <pyams_file.file.File object at 0x...>}
    >>> i18n_content.data['en'].data
    b'This is my I18n content'

We can also set a value using a tuple made of filename and file object:

    >>> i18n_content.data = {'en': ('test.txt', 'This is my I18n content')}

Eventually, the filename can include an optional content-type, separator with a comma:

    >>> i18n_content.data = {'en': ('test.txt; text/plain; charset=utf-8', 'This is my I18n content')}
    >>> i18n_content.data['en'].content_type
    'text/plain; charset=utf-8'


Managing images
---------------

Let's now try to use an image instead of a simple text content:

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png')
    >>> with open(img_name, 'rb') as file:
    ...     content.data = file
    >>> content.data
    <pyams_file.file.ImageFile object at 0x...>
    >>> content.data.get_size()
    20212

As we can see, the image has automatically been recognized as such:

    >>> content.data.content_type
    'image/png'
    >>> content.data.get_image_size()
    (535, 166)

We now have a few helpers to manipulate images; let's commit first:

    >>> content.data.resize(500, 500, keep_ratio=True)
    >>> content.data.get_size()
    22463
    >>> content.data.get_image_size()
    (500, 155)

Resizing an image to higher resolution than original image just leaves the original image
unchanged:

    >>> content.data.resize(1000, 1000, keep_ratio=True)
    >>> content.data.get_size()
    22463
    >>> content.data.get_image_size()
    (500, 155)

We can also rotate image, or crop on a given selection:

    >>> transaction.commit()
    >>> content.data.rotate(-90)
    >>> content.data.get_size()
    22867
    >>> content.data.get_image_size()
    (155, 500)

    >>> transaction.commit()
    >>> content.data.crop(50, 50, 300, 300)
    >>> content.data.get_size()
    9257
    >>> content.data.get_image_size()
    (250, 250)

Please note also that if you can store any type of content in a generic file field, you can only
store images in an image field:

    >>> content.img_data = 'This is a bad text content'
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (<pyams_file.file.File object at 0x...>, <InterfaceClass pyams_file.interfaces.IBaseImageFile>, 'img_data')

    >>> content.img_data = content.data
    >>> content.img_data.content_type
    'image/png'
    >>> content.img_data.get_size()
    9257
    >>> content.img_data.get_image_size()
    (250, 250)


Downloading a file
------------------

Each file has it's own URL, which is defined via "absolute_url()" on any File object instance.
The FileView is used to download a file:

    >>> transaction.commit()

We can suppress warnings here to avoid a RessourceWarning about unclosed files; in a normal
Pyramid context, the response body is closed automatically:

    >>> import warnings
    >>> warnings.filterwarnings('ignore')

    >>> from pyams_file.skin.view import FileView
    >>> request = DummyRequest(context=content.data, range=None, if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '200 OK'
    >>> response.content_type
    'image/png'
    >>> response.has_body
    True
    >>> result = response({'REQUEST_METHOD': 'GET'}, lambda x, y: None)
    >>> len(list(result)[0])
    9257

You can also specify a request parameter to get a download of a file, instead of a link to a file
that will be automatically displayed into a web browser:

    >>> request = DummyRequest(context=content.data, params={'dl': 1},
    ...                        range=None, if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '200 OK'
    >>> response.content_disposition
    'attachment; filename="noname.png"'

To get a file name, we have to set it into file properties:

    >>> content.data.filename = 'pyams-test.png'
    >>> request = DummyRequest(context=content.data, params={'dl': 1},
    ...                        range=None, if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '200 OK'
    >>> response.content_disposition
    'attachment; filename="pyams-test.png"'

We should be able to include any non latin-1 character into a file name:

    >>> content.data.filename = 'pyams-testé-€.png'
    >>> request = DummyRequest(context=content.data, params={'dl': 1},
    ...                        range=None, if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '200 OK'
    >>> response.content_disposition
    'attachment; filename="pyams-teste-%E2%82%AC.png"'

File view also allows custom headers, like ranged requests or requests based on last modification
date:

    >>> from webob.byterange import Range
    >>> request = DummyRequest(context=content.data, user_agent='Dummy',
    ...                        range=Range(0, 100), if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '206 Partial Content'
    >>> response.content_length
    100

    >>> request = DummyRequest(context=content.data, user_agent='Dummy',
    ...                        range=Range(9000, 10000), if_modified_since=None)
    >>> response = FileView(request)
    >>> response.status
    '206 Partial Content'
    >>> response.content_length
    257

    >>> from datetime import datetime, timedelta
    >>> from pyams_utils.timezone import gmtime

    >>> now = gmtime(datetime.now())
    >>> request = DummyRequest(context=content.data,
    ...                        range=None, if_modified_since=now)
    >>> response = FileView(request)
    >>> response.status
    '200 OK'
    >>> response.last_modified is None
    True

    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> config.registry.notify(ObjectModifiedEvent(content.data))
    >>> IZopeDublinCore(content.data).modified = now - timedelta(days=1)

    >>> response = FileView(request)
    >>> response.status
    '304 Not Modified'


Deleting a file
---------------

Three options are available to delete a file (if it's not required!): the first one is just to
assign a null value to the given property; the second one is by using the "del" instruction; and third
to be able to delete a file from a form is to assign a special value called **TO_BE_DELETED**, defined by
PyAMS_utils:

    >>> len(refs.refs)
    3

    >>> content.data
    <pyams_file.file.ImageFile object at 0x...>
    >>> content.data = None
    >>> content.data is None
    True
    >>> len(refs.refs)
    2

    >>> with open(img_name, 'rb') as file:
    ...     content.data = file
    >>> del content.data
    >>> content.data is None
    True
    >>> len(refs.refs)
    2

    >>> with open(img_name, 'rb') as file:
    ...     content.data = file
    >>> len(refs.refs)
    3
    >>> from pyams_utils.interfaces.form import TO_BE_DELETED
    >>> content.data = TO_BE_DELETED
    >>> content.data is None
    True
    >>> i18n_content.data = {'en': TO_BE_DELETED}
    >>> len(refs.refs)
    1

Let's try now with another I18n required property:

    >>> i18n_content.required_data = {}
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.RequiredMissing

    >>> i18n_content.required_data = {'en': None}
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (None, ...)

    >>> i18n_content.required_data = {'en': 'This is my I18n content'}
    >>> i18n_content.required_data = {'en': NOT_CHANGED, 'fr': 'Contenu en Français'}
    >>> i18n_content.required_data = {'en': TO_BE_DELETED}
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.RequiredMissing

When using required property on I18n fields, the condition is accepted as soon as at least
one language is filled:

    >>> i18n_content.required_data = {'en': 'This is my I18n content', 'fr': TO_BE_DELETED}
    >>> sorted(i18n_content.required_data.keys())
    ['en']


Deleting files container
------------------------

When files are added to an object with properties, an *IFileFieldContainer* marker interface
is added to this object, and an annotation is added to store the name of attributes containing
files; an event subscriber is associated to removal of objects containing files so that the
references to their blobs are correctly removed.

Let's remove some files:

    >>> from pyams_utils.adapter import get_annotation_adapter
    >>> from pyams_file.property import FILE_CONTAINER_ATTRIBUTES
    >>> from pyams_file.interfaces import IFileFieldContainer

    >>> len(refs.refs)
    2

    >>> content = MyContent()
    >>> locate(content, app)
    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = file
    ...     content.required_data = file

    >>> len(refs.refs)
    4

    >>> IFileFieldContainer.providedBy(content)
    True
    >>> attributes = get_annotation_adapter(content, FILE_CONTAINER_ATTRIBUTES, set,
    ...                                     notify=False, locate=False)
    >>> sorted(attributes)
    ['data', 'required_data']
    >>> del content.data
    >>> sorted(attributes)
    ['required_data']

Deleting the same property several times is not a problem:

    >>> content.data is None
    True
    >>> del content.data
    >>> content.data is None
    True

    >>> del content.required_data
    >>> sorted(attributes)
    []
    >>> content.required_data is None
    True
    >>> del content.required_data
    >>> content.required_data is None
    True

    >>> len(refs.refs)
    2

    >>> IFileFieldContainer.providedBy(i18n_content)
    True
    >>> attributes = get_annotation_adapter(i18n_content, FILE_CONTAINER_ATTRIBUTES, set,
    ...                                     notify=False, locate=False)
    >>> sorted(attributes)
    ['required_data::en']
    >>> del i18n_content.data
    >>> i18n_content.data is None
    True
    >>> del i18n_content.data
    Traceback (most recent call last):
    ...
    KeyError: 'data'

    >>> del i18n_content.required_data
    >>> sorted(attributes)
    []
    >>> i18n_content.required_data is None
    True

    >>> len(refs.refs)
    1

Deleting the whole property is also the only way to remove a whole value on a required attribute!

Notifying object destruction will also trigger removal of blobs references:

    >>> content = MyContent()
    >>> locate(content, app)
    >>> with open(os.path.join(temp_dir, 'data.txt'), 'r+b') as file:
    ...     content.data = file

    >>> len(refs.refs)
    2

    >>> transaction.commit()

    >>> from zope.lifecycleevent import ObjectRemovedEvent

    >>> IFileFieldContainer.providedBy(content)
    True
    >>> content.__parent__ = None
    >>> config.registry.notify(ObjectRemovedEvent(content))

    >>> len(refs.refs)
    1


Removing unused blobs
---------------------

After these tests, we can see that despite the fact that we don't have any File object anymore
into our database, several blobs are still present on the filesystem:

    >>> transaction.commit()
    >>> len(list(find_files("*.blob", os.path.join(temp_dir, 'blobs'))))
    23

Why so many files? Because each time a File object is committed, even when using an history-free
storage, a new blob file is stored on the filesystem; these files will be removed when using the
"zeopack" (when using ZEO) or "zodbpack" (when using Relstorage) command line scripts.


Tests cleanup:

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(None)
    >>> manager.clear()
    >>> transaction.commit()
    >>> tearDown()
