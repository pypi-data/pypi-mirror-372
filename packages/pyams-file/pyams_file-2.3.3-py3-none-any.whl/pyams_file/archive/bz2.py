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

"""PyAMS_file.archive.bz2 module

Bzip2 extraction module.
"""

import bz2

from pyams_file.archive import ArchiveExtractorBase
from pyams_file.archive.tar import TarArchiveExtractor
from pyams_file.file import get_magic_content_type
from pyams_file.interfaces.archive import IArchiveExtractor
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


CHUNK_SIZE = 4096


@utility_config(name='application/x-bzip2', provides=IArchiveExtractor)
class BZip2ArchiveExtractor(ArchiveExtractorBase):
    """BZip2 file format archive extractor"""

    def _initialize(self, data, mode='r'):
        """Initialize extractor"""
        data = super()._initialize(data, mode)
        return data, bz2.BZ2Decompressor()

    def get_contents(self, data, mode='r'):
        """Extract archive contents"""
        data, extractor = self._initialize(data, mode)
        decompressed = extractor.decompress(data.read(CHUNK_SIZE))
        while not decompressed:
            decompressed = extractor.decompress(data.read(CHUNK_SIZE))
        mime_type = get_magic_content_type(decompressed[:CHUNK_SIZE])
        if mime_type == 'application/x-tar':
            tar = TarArchiveExtractor()
            data.seek(0)
            yield from tar.get_contents(data, 'r:bz2')
        else:
            while extractor.needs_input:
                decompressed += extractor.decompress(data.read(CHUNK_SIZE))
            yield decompressed, ''
