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

"""PyAMS_file.generations.evolve1 module

This generation module is looking for existing thumbnails and remove them from the database
to avois a bug in previous release which was leading to blob files never being correctly deleted
on database packing.
"""

import logging

from zope.intid import IIntIds

from pyams_file.interfaces import IMediaFile
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_utils.registry import get_local_registry, get_utility, set_local_registry

__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (file)')


def evolve(site):
    """Evolve 1: remove all images thumbnails to free blobs"""
    registry = get_local_registry()
    try:
        medias = set()
        set_local_registry(site.getSiteManager())
        LOGGER.warning("Removing all thumbnails from database to free unused blobs...")
        intids = get_utility(IIntIds)
        for ref in list(intids.refs.keys()):
            obj = intids.queryObject(ref)
            if IMediaFile.providedBy(obj):
                LOGGER.debug(">>> removing thumbnails for image {!r}".format(obj))
                thumbnails = IThumbnails(obj, None)
                if thumbnails is not None:
                    medias.add(obj)
                    thumbnails.clear_thumbnails()
        LOGGER.warning("Thumbnails cleanup is finished. Launch *zeopack* (for ZEO storage) "
                       "or *zodbpack* (for Relstorage) command to remove all unused blobs.")
        LOGGER.warning("{} images updated".format(len(medias)))
    finally:
        set_local_registry(registry)
