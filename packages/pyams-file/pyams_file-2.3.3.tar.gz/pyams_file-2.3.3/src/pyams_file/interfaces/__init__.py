#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_file.interfaces module

This module provides all module interfaces and constants.
"""

from zope.annotation import IAttributeAnnotatable
from zope.interface import Interface, implementer
from zope.lifecycleevent import IObjectModifiedEvent, ObjectModifiedEvent
from zope.schema import Bytes, BytesLine, Choice, Text, TextLine

from pyams_i18n.interfaces import BASE_LANGUAGES_VOCABULARY_NAME


__docformat__ = 'restructuredtext'

from pyams_file import _


#
# Blobs references manager
#

class IBlobReferenceManager(Interface):
    """Blobs references manager

    This utility interface is used to manage references to blobs: each file contains a
    link to a ZODB "Blob" object which is used to store it's data; when a content is duplicated,
    all it's blobs references are updated but the blob itself is not duplicated to reduce space
    usage. As long as a blob data is not modified, the same content can be shared between several
    versions of a same content. So it's only when all references to a given blob have been removed
    that the blob file is deleted and can be garbaged collected.
    """

    def add_reference(self, blob, reference):
        """Add a reference to given blob"""

    def drop_reference(self, blob, reference):
        """Remove reference from given blob

        Blob is deleted if no more referenced.
        """


#
# Main file objects interfaces
#

class IFileModifiedEvent(IObjectModifiedEvent):
    """Modified file event interface"""


@implementer(IFileModifiedEvent)
class FileModifiedEvent(ObjectModifiedEvent):
    """Modified file event"""


class IFile(IAttributeAnnotatable):
    """File object interface"""

    content_type = BytesLine(title="Content type",
                             description="The content type identifies the type of content data",
                             required=False,
                             default=b'',
                             missing_value=b'')

    data = Bytes(title="Content data",
                 description="Actual file content",
                 required=False,
                 default=b'',
                 missing_value=b'')

    def get_size(self):
        """Returns the byte-size of object's data"""

    def get_blob(self, mode='r'):
        """Get Blob file associated with this object"""

    def add_blob_reference(self, reference):
        """Add a reference to file internal blob"""

    def free_blob(self):
        """Free blob associated with this object"""


class IMediaFile(IFile):
    """Multimedia file"""


class IBaseImageFile(IMediaFile):
    """Base image interface"""


class IImageFile(IBaseImageFile):
    """Image object interface"""

    def get_image_size(self):
        """Returns an (x, y) tuple describing image dimensions"""

    def resize(self, width, height, keep_ratio=True):
        """Resize image to given dimensions"""

    def crop(self, x1, y1, x2, y2):  # pylint: disable=invalid-name
        """Crop image to given coordinates"""

    def rotate(self, angle=-90):
        """Rotate image, default to right"""


class ISVGImageFile(IBaseImageFile):
    """SVG file interface"""


class IResponsiveImage(Interface):
    """Responsive image marker interface"""


class IVideoFile(IMediaFile):
    """Video file interface"""


class IAudioFile(IMediaFile):
    """Audio file interface"""


class IFileInfo(Interface):
    """File extended information"""

    title = TextLine(title=_("Title"),
                     required=False)

    description = Text(title=_("Description"),
                       required=False)

    filename = TextLine(title=_("Save file as..."),
                        description=_("Name under which the file will be saved"),
                        required=False)

    language = Choice(title=_("Language"),
                      description=_("File's content language"),
                      vocabulary=BASE_LANGUAGES_VOCABULARY_NAME,
                      required=False)


class IFileFieldContainer(IAttributeAnnotatable):
    """Marker interface for contents holding file properties"""


FILE_CONTAINER_ATTRIBUTES = 'pyams_file.file.attributes'
