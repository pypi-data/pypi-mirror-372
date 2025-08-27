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

"""PyAMS_file.archive.gz module

GZip files extraction module.
"""

import gzip

from pyams_file.archive import ArchiveExtractorBase
from pyams_file.archive.tar import TarArchiveExtractor
from pyams_file.file import get_magic_content_type
from pyams_file.interfaces.archive import IArchiveExtractor
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


CHUNK_SIZE = 4096


@utility_config(name='application/x-gzip', provides=IArchiveExtractor)
class GZipArchiveExtractor(ArchiveExtractorBase):
    """GZip file format archive extractor"""

    def _initialize(self, data, mode='r'):
        """Initialize extractor"""
        data = super()._initialize(data, mode)
        return data, gzip.GzipFile(fileobj=data, mode=mode)

    def get_contents(self, data, mode='r'):
        """Extract archive contents"""
        data, extractor = self._initialize(data, mode)
        gzip_data = extractor.read(CHUNK_SIZE)
        mime_type = get_magic_content_type(gzip_data)
        if mime_type == 'application/x-tar':
            tar = TarArchiveExtractor()
            data.seek(0)
            yield from tar.get_contents(data, 'r:gz')
        else:
            next_data = extractor.read(CHUNK_SIZE)
            while next_data:
                gzip_data += next_data
                next_data = extractor.read(CHUNK_SIZE)
            yield gzip_data, ''
