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

"""PyAMS_file.skin.view module

This module provides a Pyramid view used to download any file.
"""

import mimetypes
import urllib
from http.client import NOT_MODIFIED, OK, PARTIAL_CONTENT

from pyramid.response import Response
from pyramid.view import view_config
from zope.dublincore.interfaces import IZopeDublinCore

from pyams_file.interfaces import IFile
from pyams_utils.rest import handle_cors_headers
from pyams_utils.unicode import translate_string


__docformat__ = 'restructuredtext'


MAX_RANGE_LENGTH = 1 << 21  # 2 Mb


@view_config(context=IFile, request_method=('GET', 'OPTIONS'))
def FileView(request):  # pylint: disable=invalid-name
    """Default file view"""
    context = request.context

    # check request method
    origin = request.headers.get('Origin')
    if (origin is not None) and (origin != request.host_url):
        handle_cors_headers(request, allowed_methods=('GET', 'OPTIONS'))

    # initialize response
    response = Response(headers=request.response.headers)

    # check OPTIONS method
    if request.method == 'OPTIONS':
        response.status = OK
        response.content_type = 'text/plain'
        return response

    # set content type
    content_type = context.content_type
    if isinstance(content_type, bytes):
        content_type = content_type.decode('utf-8')
    response.content_type = content_type

    # check for last modification date
    zdc = IZopeDublinCore(context, None)
    if zdc is not None:
        modified = zdc.modified
        if modified is not None:
            if_modified_since = request.if_modified_since
            # pylint: disable=no-member
            if if_modified_since and \
                    (int(modified.timestamp()) <= int(if_modified_since.timestamp())):
                response.status = NOT_MODIFIED
                return response
            response.last_modified = modified

    body_file = context.get_blob(mode='c')

    # set Content-Disposition header
    disposition = ''
    if request.params.get('dl') is not None:
        disposition = 'attachment'

    filename = context.filename or 'noname'
    extension = mimetypes.guess_extension(content_type)
    if extension and not filename.endswith(extension):
        filename = f'{filename}{extension}'
    filename = urllib.parse.quote(translate_string(filename, force_lower=False),
                                  encoding='utf-8')
    filename = f'filename="{filename}"'

    disposition_format = '{}; {}' if disposition and filename else '{}{}'
    response.content_disposition = disposition_format.format(disposition, filename)

    # check for range request
    if request.range is not None:
        try:
            body = body_file.read()
            body_length = len(body)
            range_start = request.range.start or 0
            if 'Firefox' in request.user_agent:  # avoid partial range for Firefox videos
                range_end = body_length
            else:
                range_end = request.range.end or min(body_length, range_start + MAX_RANGE_LENGTH)
            ranged_body = body[range_start:range_end]
            response.status = PARTIAL_CONTENT
            response.content_range = (range_start, range_start + len(ranged_body), body_length)
            response.body = ranged_body
        finally:
            body_file.close()
    else:
        response.body_file = body_file

    return response
