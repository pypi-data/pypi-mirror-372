#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""
Generic test cases for pyams_file doctests
"""

import os
import sys
from fnmatch import fnmatch

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface, implementer

from pyams_file.property import FileProperty, I18nFileProperty
from pyams_file.schema import FileField, I18nAudioField, I18nFileField, I18nImageField, \
    I18nMediaField, \
    I18nThumbnailImageField, I18nThumbnailMediaField, I18nThumbnailVideoField, I18nVideoField, \
    ImageField


__docformat__ = 'restructuredtext'


def get_package_dir(value):
    """Get package directory"""
    package_dir = os.path.split(value)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)
    return package_dir


def find_files(pattern, path):
    """Find files in given path matching name pattern"""
    for root, dirs, files in os.walk(path):  # pylint: disable=unused-variable
        for name in files:
            if fnmatch(name, pattern):
                yield (root, name)


#
# Tests classes
#

class IMyInterface(Interface):
    """Custom test interface"""
    data = FileField(title='File content', required=False)
    img_data = ImageField(title='Image content', required=False)
    required_data = FileField(title='Required field', required=True)



@implementer(IMyInterface)
class MyContent(Persistent, Contained):
    """Custom content class"""
    data = FileProperty(IMyInterface['data'])
    img_data = FileProperty(IMyInterface['img_data'])
    required_data = FileProperty(IMyInterface['required_data'])


class IMyI18nInterface(Interface):
    """Custom test interface with I18n field"""
    data = I18nFileField(title='File content', required=False)
    required_data = I18nFileField(title='Alternate content', required=True)
    media = I18nMediaField(title='Media field', required=False)
    thmedia = I18nThumbnailMediaField(title='Thumbnail media', required=False)
    image = I18nImageField(title='Image', required=False)
    thimage = I18nThumbnailImageField(title='Thumbnail image', required=False)
    video = I18nVideoField(title='Video', required=False)
    thvideo = I18nThumbnailVideoField(title='Thumbnail video', required=False)
    audio = I18nAudioField(title='Audio', required=False)


@implementer(IMyI18nInterface)
class MyI18nContent(Persistent, Contained):
    """Custom content class with I18n property"""
    data = I18nFileProperty(IMyI18nInterface['data'])
    required_data = I18nFileProperty(IMyI18nInterface['required_data'])
