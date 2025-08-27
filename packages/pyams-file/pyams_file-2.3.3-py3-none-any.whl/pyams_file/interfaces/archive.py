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

"""PyAMS_file.interfaces.archive module

This module provides a single helper interface to handle archives.
"""

from zope.interface import Interface


__docformat__ = 'restructuredtext'


class IArchiveExtractor(Interface):
    """Archive contents extractor"""

    def get_contents(self, data, mode='r'):
        """Get iterator over archive contents

        Each iteration is a tuple containing data and file name.
        """
