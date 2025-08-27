#
# Copyright (c) 2008-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_file.generations sub-package

"""

import sys
from importlib import import_module

from pyams_file.interfaces import IBlobReferenceManager
from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_utils.registry import utility_config

__docformat__ = 'restructuredtext'


REQUIRED_UTILITIES = (
    (IBlobReferenceManager, '', None, 'Blobs references manager'),
)


@utility_config(name='PyAMS file', provides=ISiteGenerations)
class FilesGenerationsChecker:
    """PyAMS file package generations checker"""

    order = 40
    generation = 4

    def evolve(self, site, current=None):
        """Check for required utilities, tables and tools"""
        check_required_utilities(site, REQUIRED_UTILITIES)
        if not current:
            current = 1
        for generation in range(current, self.generation):
            module_name = 'pyams_file.generations.evolve{}'.format(generation)
            module = sys.modules.get(module_name)
            if module is None:
                module = import_module(module_name)
            module.evolve(site)
