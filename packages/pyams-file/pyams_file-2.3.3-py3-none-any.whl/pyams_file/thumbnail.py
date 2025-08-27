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

"""PyAMS_file.thumbnail module

This module is used to generate images thumbnails.
"""

import logging
import re

from BTrees import OOBTree  # pylint: disable=no-name-in-module
from persistent.mapping import PersistentMapping
from pyramid.events import subscriber
from pyramid.threadlocal import get_current_registry
from transaction.interfaces import ITransactionManager
from zope.interface import alsoProvides
from zope.lifecycleevent import IObjectRemovedEvent, ObjectAddedEvent, ObjectCreatedEvent, \
    ObjectRemovedEvent
from zope.location import locate
from zope.traversing.interfaces import ITraversable

from pyams_file.file import FileFactory
from pyams_file.interfaces import IFileModifiedEvent, IImageFile, IMediaFile
from pyams_file.interfaces.thumbnail import IThumbnailFile, IThumbnailer, IThumbnails, \
    IWatermarker
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.registry import query_utility
from pyams_utils.request import check_request


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (file)')


THUMBNAIL_ANNOTATIONS_KEY = 'pyams_file.image.thumbnails'
THUMBNAIL_GEOMETRY_KEY = 'pyams_file.image.geometry'

THUMB_WIDTH = re.compile(r'^(?:\w+:)?w([0-9]+)$')
THUMB_HEIGHT = re.compile(r'^(?:\w+:)?h([0-9]+)$')
THUMB_SIZE = re.compile(r'^(?:\w+:)?([0-9]+)x([0-9]+)$')


@adapter_config(required=IImageFile, provides=IThumbnails)
class ImageThumbnailAdapter:
    """Image thumbnails adapter"""

    def __init__(self, image):
        self.image = image
        self.thumbnails = get_annotation_adapter(image, THUMBNAIL_ANNOTATIONS_KEY, OOBTree.OOBTree,
                                                 notify=False, locate=False)

    def get_image_size(self):
        """Get image size, in pixels"""
        return self.image.get_image_size()

    def get_thumbnail_size(self, thumbnail_name, forced=False):
        """Get size in pixels of requested thumbnail"""
        w_ratio, h_ratio = 1., 1.
        width, height = self.get_image_size()
        match = THUMB_WIDTH.match(thumbnail_name)
        if match:
            w = int(match.groups()[0])  # pylint: disable=invalid-name
            w_ratio = 1. * width / w
            h_ratio = 0.
        else:
            match = THUMB_HEIGHT.match(thumbnail_name)
            if match:
                h = int(match.groups()[0])  # pylint: disable=invalid-name
                w_ratio = 0.
                h_ratio = 1. * height / h
            else:
                match = THUMB_SIZE.match(thumbnail_name)
                if match:
                    groups = match.groups()
                    w = int(groups[0])  # pylint: disable=invalid-name
                    h = int(groups[1])  # pylint: disable=invalid-name
                    w_ratio = 1. * width / w
                    h_ratio = 1. * height / h
        if match:
            ratio = max(w_ratio, h_ratio)
            if not forced:
                ratio = max(ratio, 1.)
            return int(width / ratio), int(height / ratio)
        return None

    def get_geometry(self, selection_name):
        """Get geometry matching given selection name"""
        geometries = get_annotation_adapter(self.image, THUMBNAIL_GEOMETRY_KEY, default={})
        # get default geometry for custom thumbnails
        if ':' in selection_name:
            selection_name, options = selection_name.split(':', 1)
        else:
            options = None
        if selection_name in geometries:
            return geometries[selection_name]
        registry = check_request().registry
        thumbnailer = registry.queryAdapter(self.image, IThumbnailer, name=selection_name)
        if thumbnailer is not None:
            return thumbnailer.get_default_geometry(options)
        return None

    def set_geometry(self, selection_name, geometry):
        """Set geometry for given selection name"""
        geometries = get_annotation_adapter(self.image, THUMBNAIL_GEOMETRY_KEY, PersistentMapping,
                                            notify=False, locate=False)
        geometries[selection_name] = geometry
        for current_thumbnail_name in list(self.thumbnails.keys()):
            if (current_thumbnail_name == selection_name) or \
                    current_thumbnail_name.startswith('{0}:'.format(selection_name)):
                self.delete_thumbnail(current_thumbnail_name)

    def clear_geometries(self):
        """Clear all stored geometries"""
        geometries = get_annotation_adapter(self.image, THUMBNAIL_GEOMETRY_KEY)
        if geometries is not None:
            for geometry_name in list(geometries.keys()):
                del geometries[geometry_name]

    def get_thumbnail_name(self, thumbnail_name, with_size=False):
        """Get name for given thumbnail name"""
        size = self.get_thumbnail_size(thumbnail_name)
        if size is not None:
            if with_size:
                return '{0}x{1}'.format(*size), size
            return '{0}x{1}'.format(*size)
        return None, None

    def get_selection(self, selection_name, format=None):
        # pylint: disable=redefined-builtin
        """Get thumbnail for given selection name"""
        LOGGER.debug(">>> Requested thumbnail selection: {}".format(selection_name))
        if selection_name in self.thumbnails:
            return self.thumbnails[selection_name]
        geometry = self.get_geometry(selection_name)
        if geometry == IThumbnailer(self.image).get_default_geometry():
            return self.image
        registry = get_current_registry()
        thumbnailer = registry.queryAdapter(self.image, IThumbnailer, name=selection_name)
        if thumbnailer is not None:
            selection = thumbnailer.create_thumbnail(geometry, format)
            if selection is not None:
                if isinstance(selection, tuple):
                    selection, format = selection
                else:
                    format = 'webp'
                selection = FileFactory(selection)
                alsoProvides(selection, IThumbnailFile)
                registry.notify(ObjectCreatedEvent(selection))
                self.thumbnails[selection_name] = selection
                selection_size = selection.get_image_size()
                locate(selection, self.image,
                       '++thumb++{0}:{1}x{2}.{3}'.format(selection_name,
                                                         selection_size[0],
                                                         selection_size[1],
                                                         format))
                LOGGER.debug("  > Generated thumbnail selection: {}".format(selection.__name__))
                registry.notify(ObjectAddedEvent(selection))
                return selection
        return None

    def get_thumbnail(self, thumbnail_name, format=None, watermark=None,
                      watermark_position='scale', watermark_opacity=1):
        # pylint: disable=redefined-builtin,too-many-arguments,too-many-locals,too-many-branches
        """Get thumbnail for given thumbnail name, which can provide selection and size"""
        LOGGER.debug(">>> Requested thumbnail: {}".format(thumbnail_name))
        # check for existing thumbnail
        if thumbnail_name in self.thumbnails:
            return self.thumbnails[thumbnail_name]
        # check for selection thumbnail, in "selection:size" format
        if ':' in thumbnail_name:
            selection_name, size = thumbnail_name.split(':', 1)
            selection = self.get_selection(selection_name)
            if selection is not None:
                thumbnails = IThumbnails(selection)
                return thumbnails.get_thumbnail(size)
        # check for matching one
        name, size = self.get_thumbnail_name(thumbnail_name, with_size=True)
        if name:
            if name in self.thumbnails:
                return self.thumbnails[name]
            # check for original image
            if size == self.get_image_size():
                return self.image
            # we will look for default image thumbnailer
            thumbnailer_name = ''
            options = name
        else:
            if ':' in thumbnail_name:
                thumbnailer_name, options = thumbnail_name.split(':', 1)
            else:
                thumbnailer_name = thumbnail_name
                options = name = thumbnail_name
        # generate and store thumbnail
        registry = get_current_registry()
        thumbnailer = registry.queryAdapter(self.image, IThumbnailer, name=thumbnailer_name)
        if thumbnailer is not None:
            thumbnail_image = thumbnailer.create_thumbnail(options, format)
            if thumbnail_image is not None:
                if isinstance(thumbnail_image, tuple):
                    thumbnail_image, format = thumbnail_image
                else:
                    format = 'webp'
                # check watermark
                if watermark is not None:
                    watermarker = query_utility(IWatermarker)
                    if watermarker is not None:
                        thumbnail_image.seek(0)
                        thumbnail_image, format = watermarker.add_watermark(thumbnail_image,
                                                                            watermark,
                                                                            watermark_position,
                                                                            watermark_opacity)
                # create final image
                thumbnail_image = FileFactory(thumbnail_image)
                alsoProvides(thumbnail_image, IThumbnailFile)
                registry.notify(ObjectCreatedEvent(thumbnail_image))
                self.thumbnails[name] = thumbnail_image
                thumbnail_size = thumbnail_image.get_image_size()
                locate(thumbnail_image, self.image,
                       '++thumb++{0}{1}{2}x{3}.{4}'.format(thumbnailer_name,
                                                           ':' if thumbnailer_name else '',
                                                           thumbnail_size[0],
                                                           thumbnail_size[1],
                                                           format))
                LOGGER.debug("  < Generated thumbnail: {}".format(thumbnail_image.__name__))
                registry.notify(ObjectAddedEvent(thumbnail_image))
                return thumbnail_image
        return None

    def delete_thumbnail(self, thumbnail_name):
        """Delete given thumbnail"""
        if thumbnail_name in self.thumbnails:
            thumbnail_image = self.thumbnails[thumbnail_name]
            registry = get_current_registry()
            registry.notify(ObjectRemovedEvent(thumbnail_image))
            del self.thumbnails[thumbnail_name]
            LOGGER.debug(">>> Removed thumbnail: {}".format(thumbnail_name))

    def clear_thumbnails(self):
        """Clear all current image thumbnails"""
        # pylint: disable=expression-not-assigned
        [self.delete_thumbnail(thumbnail_name) for thumbnail_name in list(self.thumbnails.keys())]


@subscriber(IFileModifiedEvent, context_selector=IMediaFile)
@subscriber(IObjectRemovedEvent, context_selector=IMediaFile)
def handle_modified_image(event):
    """Clear thumbnails and selections when an image is updated or removed"""
    thumbnails = IThumbnails(event.object, None)
    if thumbnails is not None:
        thumbnails.clear_geometries()
        thumbnails.clear_thumbnails()


@adapter_config(name='thumb', required=IImageFile, provides=ITraversable)
class ThumbnailTraverser(ContextAdapter):
    """++thumb++ namespace traverser"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Traverse to given thumbnail name"""
        if '.' in name:
            thumbnail_name, format = name.rsplit('.', 1)  # pylint: disable=redefined-builtin
        else:
            thumbnail_name = name
            format = None  # pylint: disable=redefined-builtin
        # pylint: disable=assignment-from-no-return
        thumbnails = IThumbnails(self.context)
        if ':' in thumbnail_name:
            selection_name, thumbnail_name = thumbnail_name.split(':', 1)
            selection = thumbnails.get_selection(selection_name, format)
            if selection is not None:
                thumbnails = IThumbnails(selection)
        # pylint: disable=assignment-from-no-return
        result = thumbnails.get_thumbnail(thumbnail_name, format)
        ITransactionManager(result).commit()  # pylint: disable=too-many-function-args
        return result
