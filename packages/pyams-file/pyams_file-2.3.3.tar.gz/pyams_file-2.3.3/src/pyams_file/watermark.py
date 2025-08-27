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

"""PyAMS_file.watermark module

This module is used to add watermarks to images.
"""

import os.path
from io import BytesIO, StringIO

from PIL import Image, ImageEnhance

from pyams_file.interfaces import IImageFile
from pyams_file.interfaces.thumbnail import IWatermarker
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


@utility_config(provides=IWatermarker)
class ImageWatermarker:
    """Image watermarker utility"""

    @staticmethod
    def _reduce_opacity(image, opacity):
        """Returns an image with reduced opacity."""
        assert 0 <= opacity <= 1
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        else:
            image = image.copy()
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)
        return image

    def add_watermark(self, image, watermark, position='scale', opacity=1, format=None):
        # pylint: disable=redefined-builtin,too-many-arguments,too-many-branches
        """Adds a watermark to an image and return a new image"""
        # init image
        if IImageFile.providedBy(image):
            image = image.data
        if isinstance(image, bytes):
            image = BytesIO(image)
        elif isinstance(image, str) and not os.path.exists(image):
            image = StringIO(image)
        image = Image.open(image)
        # check format
        if not format:
            format = image.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        # check RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        # init watermark
        if isinstance(watermark, str) and os.path.exists(watermark):
            watermark = Image.open(watermark)
        else:
            if IImageFile.providedBy(watermark):
                watermark = Image.open(StringIO(watermark.data))
            else:
                watermark = Image.open(watermark)
        if opacity < 1:
            watermark = self._reduce_opacity(watermark, opacity)
        # create a transparent layer the size of the image and draw the
        # watermark in that layer.
        layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        if position == 'tile':
            for y in range(0, image.size[1], watermark.size[1]):  # pylint: disable=invalid-name
                for x in range(0, image.size[0], watermark.size[0]):  # pylint: disable=invalid-name
                    layer.paste(watermark, (x, y))
        elif position == 'scale':
            # scale, but preserve the aspect ratio
            ratio = min(float(image.size[0]) / watermark.size[0],
                        float(image.size[1]) / watermark.size[1])
            w = int(watermark.size[0] * ratio)  # pylint: disable=invalid-name
            h = int(watermark.size[1] * ratio)  # pylint: disable=invalid-name
            watermark = watermark.resize((w, h))
            layer.paste(watermark, (int((image.size[0] - w) / 2), int((image.size[1] - h) / 2)))
        else:
            layer.paste(watermark, position)
        # composite the watermark with the layer
        new = BytesIO()
        composite = Image.composite(layer, image, layer)
        if format == 'JPEG':
            composite = composite.convert('RGB')
        composite.save(new, format)
        return new.getvalue(), format.lower()
