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

import transaction

from pyams_file.interfaces import IBlobReferenceManager
from pyams_site.interfaces import ISiteRoot
from pyams_utils.registry import get_local_registry, get_utility, set_local_registry
from pyams_utils.traversing import get_parent

__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (file)')


def evolve(site):
    """Evolve 2: create reference for all files blobs"""
    registry = get_local_registry()
    try:
        nb_files = 0
        set_local_registry(site.getSiteManager())
        LOGGER.warning("Scanning files references for orphaned blobs...")
        references = get_utility(IBlobReferenceManager)
        for oid, refs in list(references.refs.items()):
            for ref in refs.copy():
                root = get_parent(ref, ISiteRoot)
                if root is None:
                    nb_files += 1
                    ref.remove_blob_reference()
                LOGGER.debug(f">>> removed blob reference for file {ref!r}")
            transaction.savepoint()
        LOGGER.warning(f"{nb_files} files updated")
        LOGGER.warning("Blobs references cleanup is finished. Launch *zeopack* (for ZEO storage) "
                       "or *zodbpack* (for Relstorage) command to remove all unused blobs.")
    finally:
        set_local_registry(registry)
