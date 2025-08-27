#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_file.file module

This module is the core of PyAMS_file package. It defines a base :py:class:`File` class which is
used to store all external files as blobs.

The way in which files are physically stored can depend on ZODB storage settings, in particular
about the "shared blobs cache" parameter.
"""

try:
    import magic
except ImportError:
    magic = None

import os
from io import BytesIO

from BTrees.OOBTree import OOBTree  # pylint: disable=import-error,no-name-in-module
from PIL import Image
from ZODB.blob import Blob
from ZODB.utils import oid_repr
from persistent import Persistent
from pyramid.events import subscriber
from zope.container.contained import Contained
from zope.copy.interfaces import ICopyHook, ResumeCopy
from zope.interface import implementer
from zope.lifecycleevent import IObjectAddedEvent, IObjectRemovedEvent
from zope.location.interfaces import IContained
from zope.schema.fieldproperty import FieldProperty

from pyams_file.interfaces import FileModifiedEvent, IAudioFile, IBlobReferenceManager, IFile, \
    IFileInfo, IImageFile, ISVGImageFile, IVideoFile
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_utility
from pyams_utils.request import check_request

__docformat__ = 'restructuredtext'


BLOCK_SIZE = 1 << 16

EXTENSIONS_THUMBNAILS = {
    '.7z': 'application-x-7z-compressed.png',
    '.ac3': 'audio-ac3.png',
    '.afm': 'application-x-font-afm.png',
    '.avi': 'video-x-generic.png',
    '.bmp': 'application-x-egon.png',
    '.bz2': 'application-x-bzip.png',
    '.css': 'text-css.png',
    '.csv': 'text-csv.png',
    '.doc': 'application-msword.png',
    '.docx': 'application-msword.png',
    '.dot': 'application-msword-template.png',
    '.deb': 'application-x-deb.png',
    '.eps': 'image-x-eps.png',
    '.exe': 'application-x-ms-dos-executable.png',
    '.flv': 'application-x-shockwave-flash.png',
    '.gif': 'application-x-egon.png',
    '.gz': 'application-x-bzip.png',
    '.heic': 'application-x-egon.png',
    '.heif': 'application-x-egon.png',
    '.htm': 'application-x-mswinurl.png',
    '.html': 'application-x-mswinurl.png',
    '.jar': 'application-x-java-archive.png',
    '.java': 'text-x-java.png',
    '.jpeg': 'application-x-egon.png',
    '.jpg': 'application-x-egon.png',
    '.js': 'application-javascript.png',
    '.mp2': 'audio-ac3.png',
    '.mp3': 'audio-ac3.png',
    '.mp4': 'application-x-shockwave-flash.png',
    '.mpeg': 'audio-ac3.png',
    '.mpg': 'audio-ac3.png',
    '.mov': 'application-x-shockwave-flash.png',
    '.odf': 'odf.png',
    '.odp': 'application-vnd.oasis.opendocument.presentation.png',
    '.ods': 'application-vnd.oasis.opendocument.spreadsheet.png',
    '.odt': 'application-msword.png',
    '.ogg': 'audio-x-flac+ogg.png',
    '.otf': 'application-x-font-otf.png',
    '.otp': 'application-vnd.oasis.opendocument.presentation-template.png',
    '.ots': 'application-vnd.oasis.opendocument.spreadsheet-template.png',
    '.ott': 'application-msword-template.png',
    '.pdf': 'application-pdf.png',
    '.php': 'application-x-php.png',
    '.pl': 'application-x-perl.png',
    '.png': 'application-x-egon.png',
    '.ppt': 'application-vnd.ms-powerpoint.png',
    '.ps': 'application-postscript.png',
    '.psd': 'application-x-krita.png',
    '.py': 'text-x-python.png',
    '.rpm': 'application-x-rpm.png',
    '.rdf': 'text-rdf+xml.png',
    '.rtf': 'application-rtf.png',
    '.sql': 'text-x-sql.png',
    '.svg': 'application-x-kontour.png',
    '.tif': 'application-x-egon.png',
    '.tiff': 'application-x-egon.png',
    '.ttf': 'application-x-font-ttf.png',
    '.txt': 'text-plain.png',
    '.vhd': 'application-x-smb-workgroup.png',
    '.xls': 'application-vnd.ms-excel.png',
    '.xlsx': 'application-vnd.ms-excel.png',
    '.xml': 'application-xml.png',
    '.wav': 'audio-x-adpcm.png',
    '.webm': 'application-x-shockwave-flash.png',
    '.webp': 'application-x-egon.png',
    '.wmf': 'application-x-wmf.png',
    '.wmv': 'video-x-generic.png',
    '.xcf': 'application-x-krita.png',
    '.zip': 'application-x-7z-compressed.png'
}


#
# Blobs references manager utility
#

@factory_config(IBlobReferenceManager)
class BlobReferencesManager(Persistent, Contained):
    """Global blobs references manager utility

    The utility is used to keep all references of persistent files objects to
    their blobs; typically, when duplicating contents, we just increase blobs references instead
    of duplicating all their internal files contents, until they are modified.

    References management is done automatically when using file-related properties, like
    :py:class:`FileProperty <pyams_file.property.FileProperty>` or :py:class:`I18nFileProperty
    <pyams_file.property.I18nFileProperty>`.
    """

    def __init__(self):
        self.refs = OOBTree()

    def add_reference(self, blob, reference):
        """Add reference to given blob"""
        oid = getattr(blob, '_p_oid')
        if not oid:
            getattr(reference, '_p_jar').add(blob)
            oid = getattr(blob, '_p_oid')
        oid = oid_repr(oid)
        refs = self.refs.get(oid) or set()
        refs.add(reference)
        self.refs[oid] = refs

    def drop_reference(self, blob, reference):
        """Remove reference from given blob"""
        oid = oid_repr(getattr(blob, '_p_oid'))
        refs = self.refs.get(oid)
        if refs is not None:
            if reference in refs:
                refs.remove(reference)
            if refs:
                self.refs[oid] = refs
            else:
                del self.refs[oid]
                del blob
        else:
            del blob


#
# Persistent file class
#

@implementer(IFile, IFileInfo, IContained)
class File(Persistent, Contained):
    """Generic file persistent object"""

    title = FieldProperty(IFileInfo['title'])
    description = FieldProperty(IFileInfo['description'])
    filename = FieldProperty(IFileInfo['filename'])
    language = FieldProperty(IFileInfo['language'])

    _size = 0

    def __init__(self, data='', content_type=None, source=None):
        self.content_type = content_type
        self._blob = None
        if data:
            self.data = data
        elif source:
            if os.path.exists(source):
                try:
                    f = open(source, 'rb')  # pylint: disable=invalid-name
                    self.data = f
                finally:
                    f.close()

    def init_blob(self):
        """Initialize internal blob and add reference to it"""
        self.remove_blob_reference()
        self._blob = Blob()

    def add_blob_reference(self, reference=None):
        """Add reference to internal blob"""
        if self._blob is not None:
            references = get_utility(IBlobReferenceManager)
            references.add_reference(self._blob, reference if reference is not None else self)

    def remove_blob_reference(self):
        """Remove reference to internal blob

        Blob is deleted if there is no more reference to it.
        """
        if self._blob is not None:
            references = get_utility(IBlobReferenceManager)
            references.drop_reference(self._blob, self)
            self._blob = None

    def get_blob(self, mode='r'):
        """Open current blob in given mode"""
        if self._blob is None:
            return None
        return self._blob.open(mode=mode)

    def get_detached_blob(self):
        """Get a detached blob, which can be used after transaction end"""
        if self._blob is None:
            return None
        return open(self._blob.committed(), 'rb')

    def _get_data(self):
        """Read the whole blob content"""
        f = self.get_blob()  # pylint: disable=invalid-name
        if f is None:
            return None
        try:
            data = f.read()
            return data
        finally:
            f.close()

    def _set_data(self, data):
        """Set blob content"""
        self.init_blob()
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif hasattr(data, 'seek'):
            data.seek(0)
        f = self.get_blob('w')  # pylint: disable=invalid-name
        try:
            if hasattr(data, 'read'):
                self._size = 0
                _data = data.read(BLOCK_SIZE)
                size = len(_data)
                while size > 0:
                    f.write(_data)
                    self._size += size
                    _data = data.read(BLOCK_SIZE)
                    size = len(_data)
            else:
                f.write(data)
                self._size = len(data)
        finally:
            f.close()

    def _del_data(self):
        """Delete blob content"""
        self.remove_blob_reference()
        
    data = property(_get_data, _set_data, _del_data)

    def get_size(self):
        """Return current blob size"""
        return self._size

    def __enter__(self):
        """Context manager entry point"""
        return self.get_blob(mode='r')

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point

        We don't close the blob here.
        It's up to the context manager call to close it!
        """

    def __iter__(self):
        """Iterator over blob content to read by chunks"""
        if self._blob is None:
            return
        with self as f:  # pylint: disable=invalid-name
            while True:
                chunk = f.read(BLOCK_SIZE)
                if not chunk:
                    f.close()
                    return
                yield chunk

    def __bool__(self):
        """Non-zero test against blob size"""
        return self._size > 0


@subscriber(IObjectAddedEvent, context_selector=IFile)
def handle_added_file(event):
    """Add blob reference when file is added"""
    event.object.add_blob_reference()


@subscriber(IObjectRemovedEvent, context_selector=IFile)
def handle_removed_file(event):
    """Remove blob associated with file when removed"""
    event.object.remove_blob_reference()


@adapter_config(required=IFile,
                provides=ICopyHook)
class BlobFileCopyHook(ContextAdapter):
    """Blob file copy hook

    Inspired by z3c.blobfile package. When a blob file is copied, we just add a reference to
    it instead of copying it's contents, until it is modified.
    """

    def __call__(self, toplevel, register):
        register(self._copy_blob)
        raise ResumeCopy

    def _copy_blob(self, translate):
        # Just add a reference to blob when copying file
        target = translate(self.context)
        setattr(target, '_blob', getattr(self.context, '_blob'))
        target.add_blob_reference(target)


#
# Persistent images
#

@implementer(IImageFile)
class ImageFile(File):
    """Image file persistent object"""

    image_size = (-1, -1)

    def _set_data(self, data):
        if isinstance(data, str):
            data = BytesIO(data.encode('utf-8'))
        elif isinstance(data, bytes):
            data = BytesIO(data)
        File._set_data(self, data)
        if hasattr(data, 'seek'):
            data.seek(0)
        img = Image.open(data)
        self.image_size = img.size

    data = property(File._get_data, _set_data, File._del_data)

    def get_image_size(self):
        """Get image dimensions"""
        return self.image_size

    def resize(self, width, height, keep_ratio=True):
        """Resize image to given dimensions"""
        with self as blob:
            try:
                image = Image.open(blob)
                image_size = image.size
                if width >= image_size[0] and height >= image_size[1]:
                    return
                new_image = BytesIO()
                w_ratio = 1. * width / image_size[0]
                h_ratio = 1. * height / image_size[1]
                if keep_ratio:
                    ratio = min(w_ratio, h_ratio)
                    image.resize((round(ratio * image_size[0]), round(ratio * image_size[1])),
                                 Image.Resampling.HAMMING) \
                         .save(new_image, image.format, quality=99)
                else:
                    image.resize((round(w_ratio * image_size[0]), round(h_ratio * image_size[1])),
                                 Image.Resampling.HAMMING) \
                         .save(new_image, image.format, quality=99)
                self.data = new_image
                request = check_request()
                request.registry.notify(FileModifiedEvent(self))
            finally:
                blob.close()

    def crop(self, x1, y1, x2, y2):  # pylint: disable=invalid-name
        """Crop image to given coordinates"""
        with self as blob:
            try:
                image = Image.open(blob)
                new_image = BytesIO()
                image.crop((x1, y1, x2, y2)) \
                     .save(new_image, image.format, quelity=99)
                self.data = new_image
                request = check_request()
                request.registry.notify(FileModifiedEvent(self))
            finally:
                blob.close()

    def rotate(self, angle=-90):
        """Rotate image of given angle, in clockwise degrees"""
        with self as blob:
            try:
                image = Image.open(blob)
                new_image = BytesIO()
                image.rotate(angle, expand=True) \
                     .save(new_image, image.format, quality=99)
                self.data = new_image
                request = check_request()
                request.registry.notify(FileModifiedEvent(self))
            finally:
                blob.close()


@implementer(ISVGImageFile)
class SVGImageFile(File):
    """SVG image file persistent object"""


@implementer(IVideoFile)
class VideoFile(File):
    """Video file persistent object"""


@implementer(IAudioFile)
class AudioFile(File):
    """Audio file persistent object"""


#
# Generic files utilities
#

def get_magic_content_type(input):  # pylint: disable=redefined-builtin
    """Get content-type based on magic library as *bytes*

    As libmagic bindings are provided via several 'magic' packages, we try them in order
    """
    if magic is not None:
        if hasattr(input, 'seek'):
            input.seek(0)
        if hasattr(input, 'read'):
            input = input.read()
        if hasattr(magic, 'detect_from_content'):
            result = magic.detect_from_content(input)  # pylint: disable=no-member
            if result:
                return result.mime_type
        elif hasattr(magic, 'from_buffer'):
            return magic.from_buffer(input, mime=True)
    return None


def FileFactory(data):  # pylint: disable=invalid-name
    """File object factory

    Automatically create the right file type based on magic
    content-type recognition.
    """
    content_type = get_magic_content_type(data)
    if content_type.startswith('image/svg'):
        factory = SVGImageFile
    elif content_type.startswith('image/'):
        factory = ImageFile
    elif content_type.startswith('video/'):
        factory = VideoFile
    elif content_type.startswith('audio/'):
        factory = AudioFile
    else:
        factory = File
    return factory(data, content_type)
