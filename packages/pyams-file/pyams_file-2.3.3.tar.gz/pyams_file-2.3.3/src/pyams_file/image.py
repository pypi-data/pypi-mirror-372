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

"""PyAMS_file.image module

This module provides several adapter to handle images thumbnails generation.

"""

import re
from io import BytesIO

from PIL import Image, ImageFilter
from pyramid.settings import asbool
from zope.component import getAdapters
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_file.file import ImageFile
from pyams_file.interfaces import IImageFile, IResponsiveImage
from pyams_file.interfaces.thumbnail import IThumbnailGeometry, IThumbnailer, IThumbnails, \
    THUMBNAILERS_VOCABULARY_NAME
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.registry import get_pyramid_registry
from pyams_utils.request import check_request
from pyams_utils.url import absolute_url
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'

from pyams_file import _  # pylint: disable=ungrouped-imports


WEB_FORMATS = ('WEBP', 'AVIF', 'JPEG', 'PNG', 'GIF')
THUMB_SIZE = re.compile(r'^(?:\w+:)?([0-9]+)x([0-9]+)$')


@implementer(IThumbnailGeometry)
class ThumbnailGeometry:
    """Image thumbnail geometry"""

    x1 = FieldProperty(IThumbnailGeometry['x1'])  # pylint: disable=invalid-name
    y1 = FieldProperty(IThumbnailGeometry['y1'])  # pylint: disable=invalid-name
    x2 = FieldProperty(IThumbnailGeometry['x2'])  # pylint: disable=invalid-name
    y2 = FieldProperty(IThumbnailGeometry['y2'])  # pylint: disable=invalid-name

    def __repr__(self):
        return '<ThumbnailGeometry: x1,y1={0.x1},{0.y1} - x2,y2={0.x2},{0.y2}>'.format(self)

    def __eq__(self, other):
        if IThumbnailGeometry.providedBy(other):
            return (self.x1 == other.x1) and \
                   (self.x2 == other.x2) and \
                   (self.y1 == other.y1) and \
                   (self.y2 == other.y2)
        return False

    def is_empty(self):
        """Check if geometry is empty"""
        return (self.x2 <= self.x1) or (self.y2 <= self.y1)


@adapter_config(required=IImageFile, provides=IThumbnailer)
class ImageThumbnailer(ContextAdapter):
    """Image thumbnailer adapter"""

    label = _("Default thumbnail")
    section = _("Default thumbnail")
    weight = 1

    ratio = (None, None)

    def get_default_geometry(self, options=None):    # pylint: disable=unused-argument
        """Default thumbnail geometry"""
        geometry = ThumbnailGeometry()
        width, height = self.context.get_image_size()
        geometry.x1 = 0  # pylint: disable=invalid-name
        geometry.y1 = 0  # pylint: disable=invalid-name
        geometry.x2 = width  # pylint: disable=invalid-name
        geometry.y2 = height  # pylint: disable=invalid-name
        return geometry
    
    def get_base_image(self, blob, format=None):
        """Get base image"""
        if blob is None:
            return None
        image = Image.open(blob)
        registry = get_pyramid_registry()
        if not format:
            format = registry.settings.get('pyams_file.thumbnails.format.forced')
        if not format:
            format = image.format
        format = format.upper()
        if format not in WEB_FORMATS:
            format = registry.settings.get('pyams_file.thumbnails.format.preferred', 'WEBP')
        # check image mode
        if image.mode in ('P', 'RGBA'):
            if format == 'JPEG':
                image = image.convert('RGB')
            elif image.mode != 'RGBA':
                image = image.convert('RGBA')
        # generate thumbnail
        return image, format.lower()

    def create_thumbnail(self, target, format=None):
        # pylint: disable=redefined-builtin,too-many-branches
        """Create thumbnail of given size and format

        :param target: size or geometry of the thumbnail
        :param format: image format
        """
        # check thumbnail name
        if isinstance(target, str):
            width, height = tuple(map(int, target.split('x')))
        elif IThumbnailGeometry.providedBy(target):
            width = target.x2 - target.x1
            height = target.y2 - target.y1
        elif isinstance(target, tuple):
            width, height = target
        else:
            return None
        with self.context as blob:
            try:
                new_image = BytesIO()
                image, format = self.get_base_image(blob, format)
                image.resize((width, height), Image.Resampling.HAMMING) \
                    .filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=0)) \
                    .save(new_image, format)
                return new_image, format.lower()
            finally:
                if blob is not None:
                    blob.close()


class ImageSelectionThumbnailer(ImageThumbnailer):
    """Image thumbnailer based on user selection"""

    section = _("Custom selections")

    def create_thumbnail(self, target, format=None):
        # pylint: disable=redefined-builtin,too-many-branches
        # get thumbnail size
        if isinstance(target, str):
            # pylint: disable=assignment-from-no-return
            geometry = IThumbnails(self.context).get_geometry(target)
            match = THUMB_SIZE.match(target)
            if match:
                width, height = tuple(map(int, match.groups()))
            else:
                width = abs(geometry.x2 - geometry.x1)
                height = abs(geometry.y2 - geometry.y1)
        elif IThumbnailGeometry.providedBy(target):
            geometry = target
            width = abs(geometry.x2 - geometry.x1)
            height = abs(geometry.y2 - geometry.y1)
        elif isinstance(target, tuple):
            width, height = target
            geometry = self.get_default_geometry()
        else:
            return None
        with self.context as blob:
            try:
                new_image = BytesIO()
                thumb_size = self.get_thumb_size(width, height, geometry)
                image, format = self.get_base_image(blob, format)
                image.crop((geometry.x1, geometry.y1, geometry.x2, geometry.y2)) \
                    .resize(thumb_size, Image.Resampling.HAMMING) \
                    .filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=0)) \
                    .save(new_image, format)
                return new_image, format.lower()
            finally:
                if blob is not None:
                    blob.close()

    def get_thumb_size(self, width, height, geometry):
        # pylint: disable=no-self-use,unused-argument
        """Get thumbnail size based on given dimensions"""
        return width, height


class ImageRatioThumbnailer(ImageSelectionThumbnailer):
    """Image thumbnailer with specific ratio"""

    ratio = (None, None)  # (width, height) ratio tuple

    def get_default_geometry(self, options=None):
        """Get default geometry for selection"""
        geometry = ThumbnailGeometry()
        width, height = self.context.get_image_size()
        thumb_max_height = width * self.ratio[1] / self.ratio[0]
        if thumb_max_height >= height:
            # image wider
            thumb_width = height * self.ratio[0] / self.ratio[1]
            geometry.x1 = round((width / 2) - (thumb_width / 2))
            geometry.y1 = 0
            geometry.x2 = round((width / 2) + (thumb_width / 2))
            geometry.y2 = height
        else:
            thumb_height = thumb_max_height
            geometry.x1 = 0
            geometry.y1 = round((height / 2) - (thumb_height / 2))
            geometry.x2 = width
            geometry.y2 = round((height / 2) + (thumb_height / 2))
        return geometry


@adapter_config(name='portrait', required=IImageFile, provides=IThumbnailer)
class ImagePortraitThumbnailer(ImageRatioThumbnailer):
    """Image portrait thumbnail adapter"""

    label = _("Portrait thumbnail")
    weight = 5

    ratio = (3, 4)


@adapter_config(name='square', required=IImageFile, provides=IThumbnailer)
class ImageSquareThumbnailer(ImageRatioThumbnailer):
    """Image square thumbnail adapter"""

    label = _("Square thumbnail")
    weight = 6

    ratio = (1, 1)


class ImageHorizontalThumbnailer(ImageRatioThumbnailer):
    """Image horizontal thumbnailer"""

    def get_thumb_size(self, width, height, geometry):
        thumb_size = abs(geometry.x2 - geometry.x1), abs(geometry.y2 - geometry.y1)
        w_ratio = 1. * width / thumb_size[0]
        h_ratio = 1. * height / thumb_size[1]
        ratio = min(w_ratio, h_ratio)
        return round(ratio * thumb_size[0]), round(ratio * thumb_size[1])


@adapter_config(name='pano', required=IImageFile, provides=IThumbnailer)
class ImagePanoThumbnailer(ImageHorizontalThumbnailer):
    """Image panoramic thumbnail adapter"""

    label = _("Panoramic thumbnail")
    weight = 7

    ratio = (16, 9)


@adapter_config(name='card', required=IImageFile, provides=IThumbnailer)
class ImageCardThumbnailer(ImageHorizontalThumbnailer):
    """Image card thumbnail adapter"""

    label = _("Card thumbnail")
    weight = 8

    ratio = (2, 1)


@adapter_config(name='banner', required=IImageFile, provides=IThumbnailer)
class ImageBannerThumbnailer(ImageRatioThumbnailer):
    """Image banner thumbnail adapter"""

    label = _("Banner thumbnail")
    weight = 9

    ratio = (5, 1)


class ResponsiveImageThumbnailer(ImageSelectionThumbnailer):
    """Responsive image thumbnailer"""

    section = _("Responsive selections")


@adapter_config(name='xs', required=IResponsiveImage, provides=IThumbnailer)
class XsImageThumbnailer(ResponsiveImageThumbnailer):
    """eXtra-Small responsive image thumbnailer"""

    label = _("Smartphone thumbnail")
    weight = 10


@adapter_config(name='sm', required=IResponsiveImage, provides=IThumbnailer)
class SmImageThumbnailer(ResponsiveImageThumbnailer):
    """SMall responsive image thumbnailer"""

    label = _("Tablet thumbnail")
    weight = 11


@adapter_config(name='md', required=IResponsiveImage, provides=IThumbnailer)
class MdImageThumbnailer(ResponsiveImageThumbnailer):
    """MeDium responsive image thumbnailer"""

    label = _("Medium screen thumbnail")
    weight = 12


@adapter_config(name='lg', required=IResponsiveImage, provides=IThumbnailer)
class LgImageThumbnailer(ResponsiveImageThumbnailer):
    """LarGe responsive image thumbnailer"""

    label = _("Large screen thumbnail")
    weight = 13


@adapter_config(name='xl', required=IResponsiveImage, provides=IThumbnailer)
class XlImageThumbnailer(ResponsiveImageThumbnailer):
    """EXtra-Large responsive image thumbnailer"""

    label = _("Extra-large screen thumbnail")
    weight = 14


@vocabulary_config(name=THUMBNAILERS_VOCABULARY_NAME)
class ImageThumbnailersVocabulary(SimpleVocabulary):
    """Image thumbnailers vocabulary"""

    def __init__(self, context=None):
        if not IImageFile.providedBy(context):
            context = ImageFile()
        request = check_request()
        translate = request.localizer.translate
        terms = []
        for name, adapter in sorted(getAdapters((context,), IThumbnailer),
                                    key=lambda x: x[1].weight):
            if not name:
                continue
            terms.append(SimpleTerm(name, title=translate(adapter.label)))
        super().__init__(terms)


def get_image_selection(image, selection, size, request=None):
    """Image selection helper

    :param image: source image
    :param selection: image selection name
    :param size: thumbnail image size of given selection
    :param request: current request
    :return str: URL of resulting image selection thumbnail
    """
    thumbnails = IThumbnails(image, None)
    if thumbnails is None:
        return None
    thumbnail = IThumbnails(thumbnails.get_selection(selection)).get_thumbnail(size)
    if request is None:
        request = check_request()
    return absolute_url(thumbnail, request)
