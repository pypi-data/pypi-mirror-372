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

"""PyAMS_file.skin main module

This module provides functions used to render images.
"""

from datetime import datetime, timezone

from pyquery import PyQuery
from pyramid.renderers import render
from zope.dublincore.interfaces import IZopeDublinCore

from pyams_file.interfaces import ISVGImageFile
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_utils.request import check_request
from pyams_utils.url import absolute_url


__docformat__ = 'restructuredtext'


def render_svg(image, width=None, height=None, request=None, css_class='', img_class='', alt=''):
    """Render SVG file"""
    # pylint: disable=too-many-arguments
    options = {}
    if width or height:
        options['style'] = 'width: {0}{1}; height: {2}{3};'.format(
            width, 'px' if isinstance(width, int) else '',
            height, 'px' if isinstance(height, int) else '')
    else:
        options['style'] = ''
    options['css_class'] = css_class
    if alt or img_class:
        svg = PyQuery(image.data)
        if alt:
            group = PyQuery('<g></g>')
            group.append(PyQuery('<title />').text(alt))
            for child in svg.children():
                group.append(child)
            svg.empty().append(group)
        if img_class:
            svg.attr('class', img_class)
        options['svg'] = svg.outer_html()
    else:
        options['svg'] = image.data
    return render('templates/svg-render.pt', options, request)


def render_img(image, width=None, height=None, request=None, css_class='', img_class='',
               timestamp=False, alt=''):
    # pylint: disable=too-many-arguments,assignment-from-no-return
    """Render image thumbnail"""
    thumbnail = None
    thumbnails = IThumbnails(image, None)
    if thumbnails is not None:
        if width and height:
            thumbnail = thumbnails.get_thumbnail('{0}x{1}'.format(width, height))
        elif width and (width != 'auto'):
            thumbnail = thumbnails.get_thumbnail('w{0}'.format(width))
        elif height and (height != 'auto'):
            thumbnail = thumbnails.get_thumbnail('h{0}'.format(height))
    if thumbnail is None:
        thumbnail = image
    if request is None:
        request = check_request()
    url = absolute_url(thumbnail, request)
    if timestamp:
        zdc = IZopeDublinCore(thumbnail, None)
        if zdc is None:
            timestamp = datetime.now(timezone.utc).timestamp()
        else:
            timestamp = zdc.modified.timestamp()    # pylint: disable=no-member
        url += '?_={0}'.format(timestamp)
    result = '<img src="{0}" class="{1}" alt="{2}" />'.format(url, img_class, alt)
    if css_class:
        result = '<div class="{0}">{1}</div>'.format(css_class, result)
    return result


def render_image(image, width=None, height=None, request=None, css_class='', img_class='',
                 timestamp=False, alt=''):
    # pylint: disable=too-many-arguments
    """Render image"""
    if ISVGImageFile.providedBy(image):
        return render_svg(image, width, height, request, css_class, img_class, alt)
    return render_img(image, width, height, request, css_class, img_class, timestamp, alt)
