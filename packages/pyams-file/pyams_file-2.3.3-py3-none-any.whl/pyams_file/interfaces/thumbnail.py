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

"""PyAMS_file.interfaces.thumbnail module

This module provides all thumbnails related interfaces.
"""

from zope.interface import Attribute, Interface
from zope.schema import Int


__docformat__ = 'restructuredtext'


class IThumbnailFile(Interface):
    """Marker interface for thumbnails"""


class IThumbnailGeometry(Interface):
    """Image thumbnail geometry interface"""

    # pylint: disable=invalid-name
    x1 = Int(title="Thumbnail position X1",
             required=True,
             min=0)

    # pylint: disable=invalid-name
    y1 = Int(title="Thumbnail position Y1",
             required=True,
             min=0)

    # pylint: disable=invalid-name
    x2 = Int(title="Thumbnail position X2",
             required=True,
             min=0)

    # pylint: disable=invalid-name
    y2 = Int(title="Thumbnail position Y2",
             required=True,
             min=0)

    def is_empty(self):
        """Check if geometry is not empty"""


THUMBNAILERS_VOCABULARY_NAME = 'pyams_file.image.thumbnailers'


class IThumbnailer(Interface):
    """Interface of adapter used to generate image thumbnails"""

    label = Attribute("Thumbnail label")
    section = Attribute("Thumbnail section")
    weight = Attribute("Thumbnail weight")

    def get_default_geometry(self):
        """Get default thumbnail geometry"""

    # pylint:disable=redefined-builtin
    def create_thumbnail(self, target, format=None):
        """Create thumbnail of the given source object

        Source can be any file which can provide thumbnails (image, video,
        PDF file...).
        Target, which defines thumbnail size, can be defined as a selection name
        ('pano', 'square', 'xs'...), as a geometry or as a (width, height) tuple.

        If the requested image is of a resolution higher than that of the original file,
        the resulting image resolution will be that of the original file.

        If format (JPEG, PNG...) is given, this will be the format of the generated
        thumbnail; otherwise the format will be those of the source image.
        """


class IThumbnails(Interface):
    """Image thumbnail interface

    Displays are images thumbnails generated 'on the fly' and stored into image
    annotations for future use
    """

    def get_image_size(self):
        """Get original image size"""

    def get_thumbnail_size(self, thumbnail_name, forced=False):
        """Get real size of the generated thumbnail

        If forced is True, the generated thumbnail can be larger than the original
        source
        """

    def get_geometry(self, selection_name):
        """Get geometry of a given thumbnail"""

    def set_geometry(self, selection_name, geometry):
        """Set geometry for given thumbnail"""

    def clear_geometries(self):
        """Remove all stored geometries from object annotations"""

    def get_thumbnail_name(self, thumbnail_name, with_size=None):
        """Get matching name for the given thumbnail name or size"""

    # pylint:disable=redefined-builtin
    def get_selection(self, selection_name, format=None):
        """Get image for given user selection"""

    # pylint:disable=redefined-builtin,too-many-arguments
    def get_thumbnail(self, thumbnail_name, format=None, watermark=None,
                      watermark_position='scale', watermark_opacity=1):
        """Get requested thumbnail

        Display can be specified as:
        - a name matching a custom thumbnailer utility
        - a width, as wXXX where XXX is the requested image width
        - a height, as hYYY, where YYY is the requested image height
        - a size, as XXXxYYY
        """

    def delete_thumbnail(self, thumbnail_name):
        """Remove selected thumbnail from object annotations"""

    def clear_thumbnails(self):
        """Remove all thumbnails from object annotations"""


class IWatermarker(Interface):
    """Interface of utility used to add image watermark"""

    # pylint:disable=redefined-builtin,too-many-arguments
    def add_watermark(self, image, watermark, position='scale', opacity=1, format=None):
        """Add watermark to given image"""
