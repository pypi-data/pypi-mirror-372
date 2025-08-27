================================
PyAMS_file thumbnails management
================================

PyAMS_file package provides a set of adapters related to thumbnails management, which is the
ability to automatically generate smaller images, adapted to a web page, of an original image.

You can also use custom selections of predefined images ratios (like square, portrait, panoramic...)
by selecting adapted areas of the original images, and you can then generate smaller thumbnails
from these selections.


Initialization
--------------

You'll notice in this tests that the current transaction is committed regularly: it's because of
how blob files are functionning, a blob file can't be reopened without being committed.

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

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))
    >>> manager.push({'request': request, 'registry': config.registry})

    >>> from pyams_file.tests import MyContent
    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png')

    >>> content = MyContent()
    >>> app['content'] = content
    >>> with open(img_name, 'rb') as file:
    ...     content.img_data = file
    >>> transaction.commit()


Getting default thumbnails
--------------------------

Let's now try to get image thumbnails:

    >>> from pyams_file.interfaces.thumbnail import IThumbnails
    >>> img = content.img_data
    >>> thumbs = IThumbnails(img)

Thumbnails are defined by their size, and by their name for custom selections; sizes can be given
in width, height or both: in any case, it's the maximum size of the resulting thumbnail:

    >>> th1 = thumbs.get_thumbnail('128x128')
    >>> th1
    <pyams_file.file.ImageFile object at 0x...>
    >>> th1.get_image_size()
    (128, 39)
    >>> th2 = thumbs.get_thumbnail('w128')
    >>> th2.get_image_size()
    (128, 39)
    >>> th3 = thumbs.get_thumbnail('h128')
    >>> th3.get_image_size()
    (412, 128)

If you look for a thumbnail of a bigger size than the original one, it's the original image which
is returned:

    >>> th4 = thumbs.get_thumbnail('1024x1024')
    >>> th4.get_image_size()
    (535, 166)
    >>> th4 is img
    True

Each thumbnail has it's own URL, to be included into a web page:

    >>> from pyams_utils.url import absolute_url
    >>> absolute_url(th3, request)
    'http://example.com/content/++attr++img_data/++thumb++412x128.png'

Generated thumbnails are stored into original image annotations, so that they don't have to be
computed each time; they are cleared when the image is modified:

    >>> sorted(thumbs.thumbnails.keys())
    ['128x39', '412x128']

    >>> from pyams_file.interfaces import FileModifiedEvent
    >>> config.registry.notify(FileModifiedEvent(img))
    >>> sorted(thumbs.thumbnails.keys())
    []

Thumbnails are automatically generated into original file format, but you can request a specific
file format for a given thumbnail:

    >>> th5 = thumbs.get_thumbnail('128x128', 'JPEG')
    >>> th5.content_type
    'image/jpeg'


Using selections
----------------

Selections allow to select parts of your image of a selected ratio; they can also be used, in
different circumstances, to provide custom parts of an image which will be used in responsive
mode in a "<picture />" HTML tag; selections are given names based on the different Bootstrap
medias sizes ("xs", "sm", "md", "lg" and "xl"), and on custom predefined aspect ratios: "portrait",
"square", "pano", "card" and "banner" which are used inside PyAMS:

    >>> th6 = thumbs.get_thumbnail('sm')
    >>> th6 is None
    True

Why is this thumbnail empty? It's because, to support responsive thumbnails, an image has to be
marked with a custom interface:

    >>> from zope.interface import alsoProvides
    >>> from pyams_file.interfaces import IResponsiveImage
    >>> alsoProvides(img, IResponsiveImage)

    >>> th6 = thumbs.get_thumbnail('sm')
    >>> th6.get_image_size()
    (535, 166)
    >>> th6 is img
    False

You can combine a custom selection with a custom size by separating them with ":":

    >>> transaction.commit()
    >>> th7 = thumbs.get_thumbnail('sm:128x128')
    >>> th7.get_image_size()
    (128, 39)

By default, responsive selections cover the whole area of the original image; let's try to create
a define a custom area for this selection:

    >>> from pyams_file.image import ThumbnailGeometry
    >>> geometry = ThumbnailGeometry()
    >>> geometry.x1 = 20
    >>> geometry.y1 = 20
    >>> geometry.x2 = 515
    >>> geometry.y2 = 146
    >>> geometry
    <ThumbnailGeometry: x1,y1=20,20 - x2,y2=515,146>

    >>> thumbs.set_geometry('sm', geometry)
    >>> th8 = thumbs.get_thumbnail('sm')
    >>> th8.get_image_size()
    (495, 126)

    >>> transaction.commit()
    >>> th9 = thumbs.get_thumbnail('sm:128x128')
    >>> th9.get_image_size()
    (128, 32)


Using selections with default ratio
-----------------------------------

Selections with default ratios are used regularly inside PyAMS; they are used like responsive
selections and unless specified otherwise, they are centered into the original image, with the
biggest possible size:

    >>> transaction.commit()
    >>> th10 = thumbs.get_thumbnail('square')
    >>> th10.get_image_size()
    (166, 166)

"portrait" is a selection with a 3/4 ratio:

    >>> th11 = thumbs.get_thumbnail('portrait')
    >>> th11.get_image_size()
    (125, 166)

"pano" is a selection with a 16/9 ratio:

    >>> th12 = thumbs.get_thumbnail('pano')
    >>> th12.get_image_size()
    (295, 166)

"card" is a selection with a 2/1 ratio, which can be used for Twitter cards:

    >>> th13 = thumbs.get_thumbnail("card")
    >>> th13.get_image_size()
    (332, 166)

And finally "banner" is a selection with a ratio of 5/1:

    >>> th14 = thumbs.get_thumbnail("banner")
    >>> th14.get_image_size()
    (535, 106)

Standard selections can also be resized in a single operation:

    >>> transaction.commit()
    >>> th15 = thumbs.get_thumbnail("banner:128x128")
    >>> th15.get_image_size()
    (128, 25)


Using custom thumbnails geometries
----------------------------------

You can specify a custom geometry to use to create a thumbnail:

    >>> from pyams_file.image import ThumbnailGeometry
    >>> geometry = ThumbnailGeometry()
    >>> geometry.x1 = 100
    >>> geometry.y1 = 100
    >>> geometry.x2 = 400
    >>> geometry.y2 = 500
    >>> geometry.is_empty()
    False

    >>> thumbs.clear_geometries()
    >>> thumbs.set_geometry('lg', geometry)
    >>> th16 = thumbs.get_thumbnail('lg')
    >>> th16.get_image_size()
    (300, 400)

    >>> thumbs.set_geometry('xl', geometry)
    >>> transaction.commit()
    >>> th17 = thumbs.get_thumbnail('xl:128x128')
    >>> th17.get_image_size()
    (96, 128)

An image selection helper is available:

    >>> from pyams_file.image import get_image_selection
    >>> get_image_selection(img, 'square', '128x128')
    'http://example.com/content/++attr++img_data/++thumb++square:166x166.png/++thumb++128x128.png'


Rendering images
----------------

PyAMS_file provides a few helpers to include an image tag into an HTML template:

    >>> transaction.commit()
    >>> from pyams_file.skin import render_image, render_svg
    >>> render_image(img, width=128, request=request)
    '<img src="http://example.com/content/++attr++img_data/++thumb++128x39.jpeg" class="" alt="" />'
    >>> render_image(th15, request=request)
    '<img src="http://example.com/content/++attr++img_data/++thumb++banner:535x106.png/++thumb++128x25.png" class="" alt="" />'

Other arguments are available when rendering images:

    >>> render_image(img, height=128, request=request)
    '<img src="http://example.com/content/++attr++img_data/++thumb++412x128.png" class="" alt="" />'
    >>> render_image(img, width=128, height=128, request=request)
    '<img src="http://example.com/content/++attr++img_data/++thumb++128x39.jpeg" class="" alt="" />'
    >>> render_image(img, width=128, css_class='my-image', timestamp=True, request=request)
    '<div class="my-image"><img src="http://example.com/content/++attr++img_data/++thumb++128x39.jpeg?_=..." class="" alt="" /></div>'


You can also render SVG images using this function:

    >>> from pyramid_chameleon import zpt
    >>> config.add_renderer('.pt', zpt.renderer_factory)

    >>> svg_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'icon.svg')

    >>> content = MyContent()
    >>> app['content-2'] = content
    >>> with open(svg_name, 'rb') as file:
    ...     content.data = file
    >>> transaction.commit()

    >>> img2 = content.data
    >>> render_svg(img2)
    '<div class=" d-inline-block align-middle svg-container"...>...<svg ...><path d="..." fill="#fff"/></svg>\n</div>\n'

You can also provide an alternate text and a custom CSS class:

    >>> render_svg(img2, css_class='my-wrapper', img_class='my-picture', alt='My icon')
    '<div class="my-wrapper d-inline-block align-middle svg-container"...>...<svg xmlns="..." viewBox="..." class="my-picture"><g><title>My icon</title><path d="..." fill="#fff"></path></g></svg>\n</div>\n'

You can also specify width and/or height when rendering an SVG file; default units are given in
pixels, but you can specify your own unit:

    >>> render_svg(img2, width=128, height='3rem')
    '<div class=" d-inline-block align-middle svg-container"... style="width: 128px; height: 3rem;">...<svg xmlns="..." viewBox="..."><path d="..." fill="#fff"/></svg>\n</div>\n'

Note: *render_image* function can render bitmap images as well as SVG images; we only use the
*render_svg* function here for testing purpose:

Because of possible libmagic behaviour in Travis-CI, we wake sure that SVG interface is
provided by the SVG image:

    >>> from pyams_file.interfaces import ISVGImageFile
    >>> if not ISVGImageFile.providedBy(img2):
    ...     alsoProvides(img2, ISVGImageFile)

    >>> render_image(img2, width=128, height='3rem')
    '<div class=" d-inline-block align-middle svg-container"... style="width: 128px; height: 3rem;">...<svg xmlns="..." viewBox="..."><path d="..." fill="#fff"/></svg>\n</div>\n'


Watermarking
------------

The "get_thumbnail" method accepts a "watermark" parameter; this allows you to set a watermark
image which will be applied on top of the original image before creating a thumbnail. The given
argument can be a file-like object, a file path or another instance of an ImageFile object.

The "watermark_position" parameter allows to define watermark position; default "scale" value is
scaling the watermark image to fit the original image size; you can use the "tile" value to tile
the watermark over the original image several times, or you can provide a tuple to set watermark
position in (x, y) above the original image, without scaling in this case.

    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'background.jpg')
    >>> wtm_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'watermark.png')

    >>> content = MyContent()
    >>> app['content-3'] = content
    >>> with open(img_name, 'rb') as file:
    ...     content.img_data = file
    >>> transaction.commit()

    >>> img3 = content.img_data
    >>> img3
    <pyams_file.file.ImageFile object at 0x...>
    >>> alsoProvides(img3, IResponsiveImage)

    >>> thumbs = IThumbnails(img3)
    >>> th17 = thumbs.get_thumbnail('xl', watermark=wtm_name)
    >>> th17
    <pyams_file.file.ImageFile object at 0x...>
    >>> th17.get_image_size()
    (1320, 770)

You can also specify custom watermarks positions:

    >>> thumbs.delete_thumbnail('xl')
    >>> th18 = thumbs.get_thumbnail('xl', watermark=wtm_name, watermark_position='tile')
    >>> th18.get_image_size()
    (1320, 770)

    >>> thumbs.delete_thumbnail('xl')
    >>> th19 = thumbs.get_thumbnail('xl', watermark=wtm_name, watermark_position='scale')
    >>> th19.get_image_size()
    (1320, 770)

Watermark opacity can also be set:

    >>> thumbs.delete_thumbnail('xl')
    >>> th20 = thumbs.get_thumbnail('xl', watermark=wtm_name, watermark_opacity=0.5)
    >>> th20.get_image_size()
    (1320, 770)


Using thumbnails traverser
--------------------------

As you can see in previous chapter, generated thumbnails URLs include a "++thumb++" traverser,
which allows to access a given thumbnail from an URL:

    >>> from zope.traversing.interfaces import ITraversable
    >>> from pyams_file.interfaces import IImageFile
    >>> from pyams_file.thumbnail import ThumbnailTraverser
    >>> config.registry.registerAdapter(ThumbnailTraverser, (IImageFile,), ITraversable,
    ...                                 name='thumb')

    >>> transaction.commit()
    >>> traverser = config.registry.getAdapter(img, ITraversable, name='thumb')
    >>> th21 = traverser.traverse('md:w600')
    >>> th21
    <pyams_file.file.ImageFile object at 0x...>
    >>> th21.get_image_size()
    (535, 166)

You can see here that the returned image can be of lower resolution than what was requested; this
is the case when the source image has a lower resolution than was is requested!


Thumbnailers vocabulary
-----------------------

    >>> from pyams_file.image import ImageThumbnailersVocabulary
    >>> vocabulary = ImageThumbnailersVocabulary()
    >>> len(vocabulary._terms)
    5
    >>> vocabulary.getTermByToken('pano')
    <zope.schema.vocabulary.SimpleTerm object at 0x...>


Tests cleanup:

    >>> IThumbnails(img).clear_thumbnails()
    >>> IThumbnails(img3).clear_thumbnails()

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(None)
    >>> manager.clear()
    >>> transaction.commit()
    >>> tearDown()

