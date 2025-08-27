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

"""PyAMS_file.archive.zip module

ZIP files extraction module.
"""

import zipfile

from pyams_file.archive import ArchiveExtractorBase
from pyams_file.file import get_magic_content_type
from pyams_file.interfaces.archive import IArchiveExtractor
from pyams_utils.registry import query_utility, utility_config


__docformat__ = 'restructuredtext'


CHUNK_SIZE = 4096


@utility_config(name='application/zip', provides=IArchiveExtractor)
class ZipArchiveExtractor(ArchiveExtractorBase):
    """ZIP file format archive extractor"""

    zip_data = None

    def _initialize(self, data, mode='r'):
        """Initialize extractor"""
        data = super()._initialize(data, mode)
        return data, zipfile.ZipFile(data, mode=mode)

    def get_contents(self, data, mode='r'):
        """Extract archive contents"""
        data, extractor = self._initialize(data, mode)
        members = extractor.infolist()
        for member in members:
            filename = member.filename
            content = extractor.read(filename)
            if not content:  # skip empty files and directories
                continue
            mime_type = get_magic_content_type(content[:CHUNK_SIZE])
            archiver = query_utility(IArchiveExtractor, name=mime_type)
            if archiver is not None:
                yield from archiver.get_contents(content)
            else:
                yield content, filename
