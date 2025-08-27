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

"""PyAMS_file.archive module

Base archive extractor class
"""


from io import BytesIO


class ArchiveExtractorBase:
    """Base archive extractor utility class"""

    def _initialize(self, data, mode='r'):  # pylint: disable=no-self-use,unused-argument
        """Initialize extractor data"""
        if isinstance(data, tuple):
            data = data[0]
        if isinstance(data, str):
            data = data.encode()
        if isinstance(data, bytes):
            data = BytesIO(data)
        return data
