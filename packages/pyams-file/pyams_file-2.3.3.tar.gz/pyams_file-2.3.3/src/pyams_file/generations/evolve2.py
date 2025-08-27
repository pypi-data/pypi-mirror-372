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

"""PyAMS_file.generations.evolve2 module

This module is doing a database scan of all registered blobs to add a reference to them
into blobs manager.
"""

import logging

from zope.intid import IIntIds

from pyams_file.interfaces import IBlobReferenceManager, IFile
from pyams_utils.registry import get_local_registry, get_utility, set_local_registry

__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (file)')


def evolve(site):
    """Evolve 2: create reference for all files blobs"""
    registry = get_local_registry()
    try:
        nb_files = 0
        set_local_registry(site.getSiteManager())
        LOGGER.warning("Creating references to all blobs...")
        intids = get_utility(IIntIds)
        references = get_utility(IBlobReferenceManager)
        for ref in list(intids.refs.keys()):
            obj = intids.queryObject(ref)
            if IFile.providedBy(obj):
                blob = getattr(obj, '_blob', None)
                if blob is not None:
                    references.add_reference(blob, obj)
                    nb_files += 1
                LOGGER.debug(f">>> updated blob reference for file {obj!r}")
        LOGGER.warning(f"{nb_files} files updated")
    finally:
        set_local_registry(registry)
