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

"""PyAMS_file.schema module

This module provides all custom file-related schema fields.
"""

from zope.interface import Attribute, Interface, implementer
from zope.schema import Bytes
from zope.schema.interfaces import IBytes, RequiredMissing, WrongType

from pyams_file.interfaces import IAudioFile, IBaseImageFile, IFile, IMediaFile, IVideoFile
from pyams_i18n.schema import I18nField, II18nField
from pyams_utils.interfaces.form import IDataManager, NOT_CHANGED, TO_BE_DELETED
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


#
# Schema fields interfaces
#

class IThumbnailField(Interface):
    """Generic field interface with thumbnail"""


class IFileField(IBytes):
    """File object field interface"""

    schema = Attribute("Required value schema")


class IMediaField(IFileField):
    """Media file object field interface"""


class IThumbnailMediaField(IMediaField, IThumbnailField):
    """Media object field with thumbnail interface"""


class IImageField(IMediaField):
    """Image file object field interface"""


class IThumbnailImageField(IImageField, IThumbnailField):
    """Image object field with thumbnail interface"""


class IVideoField(IMediaField):
    """Video file field interface"""


class IThumbnailVideoField(IVideoField, IThumbnailField):
    """Video object field with thumbnail interface"""


class IAudioField(IMediaField):
    """Audio file field interface"""


#
# Custom schema fields
#

@implementer(IFileField)
class FileField(Bytes):
    """Custom field used to handle file-like properties"""

    schema = IFile

    def _validate(self, value):
        if value is TO_BE_DELETED:
            if self.required and not self.default:
                raise RequiredMissing
        elif value is NOT_CHANGED:
            return
        elif isinstance(value, tuple):
            try:
                filename, stream = value
                if not isinstance(filename, str):
                    raise WrongType(filename, str, '{0}.filename'.format(self.__name__))
                if not hasattr(stream, 'read'):
                    raise WrongType(stream, '<file-like object>', self.__name__)
            except ValueError as exc:
                raise WrongType(value, tuple, self.__name__) from exc
        elif not self.schema.providedBy(value):
            raise WrongType(value, self.schema, self.__name__)


@implementer(IMediaField)
class MediaField(FileField):
    """Custom field used to store media-like properties"""

    schema = IMediaFile


@implementer(IThumbnailMediaField)
class ThumbnailMediaField(MediaField):
    """Custom field used to store media properties with thumbnail selection"""


@implementer(IImageField)
class ImageField(MediaField):
    """Custom field used to handle image properties"""

    schema = IBaseImageFile


@implementer(IThumbnailImageField)
class ThumbnailImageField(ImageField):
    """Custom field used to handle images properties with square selection"""


@implementer(IVideoField)
class VideoField(MediaField):
    """Custom field used to store video file"""

    schema = IVideoFile


@implementer(IThumbnailVideoField)
class ThumbnailVideoField(VideoField):
    """Custom field used to store video properties with thumbnail selection"""


@implementer(IAudioField)
class AudioField(MediaField):
    """Custom field used to store audio file"""

    schema = IAudioFile


#
# I18n file fields
#

class II18nFileField(II18nField):
    """I18n file field marker interface"""


@implementer(II18nFileField)
class I18nFileField(I18nField):
    """I18n file field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        super().__init__(value_type=FileField(min_length=value_min_length,
                                              max_length=value_max_length,
                                              required=False),
                         **kwargs)

    def _validate(self, value):  # pylint: disable=too-many-branches
        if self.required:
            if self.default:
                return
            if not value:
                raise RequiredMissing
            has_value = False
            registry = get_current_registry()
            for lang, lang_value in value.items():
                # check for NOT_CHANGED value
                if lang_value is NOT_CHANGED:  # check for empty file value
                    adapter = registry.queryMultiAdapter((self.context, self), IDataManager)
                    if adapter is not None:
                        try:
                            old_value = adapter.query() or {}
                        except TypeError:  # can't adapt field context => new content?
                            old_value = None
                        else:
                            old_value = old_value.get(lang)
                    else:  # default data manager
                        old_value = getattr(self.context, self.__name__, {}).get(lang)
                    has_value = has_value or bool(old_value)
                    if has_value:
                        break
                elif lang_value is not TO_BE_DELETED:
                    has_value = True
                    break
            if not has_value:
                raise RequiredMissing
        for lang_value in value.values():
            if lang_value in (NOT_CHANGED, TO_BE_DELETED):
                return
            if isinstance(lang_value, tuple):
                try:
                    filename, stream = lang_value
                    if not isinstance(filename, str):
                        raise WrongType(filename, str, '{0}.filename'.format(self.__name__))
                    if not hasattr(stream, 'read'):
                        raise WrongType(stream, '<file-like object>', self.__name__)
                except ValueError as exc:
                    raise WrongType(lang_value, tuple, self.__name__) from exc
            elif not self.value_type.schema.providedBy(lang_value):
                raise WrongType(lang_value, self.value_type.schema, self.__name__)


class II18nMediaField(II18nFileField):
    """I18n media field marker interface"""


@implementer(II18nMediaField)
class I18nMediaField(I18nFileField):
    """I18n media field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=MediaField(min_length=value_min_length,
                                  max_length=value_max_length,
                                  required=False),
            **kwargs)


class II18nThumbnailMediaField(II18nMediaField):
    """I18n field for media with thumbnail"""


@implementer(II18nThumbnailMediaField)
class I18nThumbnailMediaField(I18nMediaField):
    """I18n media field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=ThumbnailMediaField(min_length=value_min_length,
                                           max_length=value_max_length,
                                           required=False),
            **kwargs)


class II18nImageField(II18nFileField):
    """I18n image field marker interface"""


@implementer(II18nImageField)
class I18nImageField(I18nMediaField):
    """I18n image field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=ImageField(min_length=value_min_length,
                                  max_length=value_max_length,
                                  required=False),
            **kwargs)


class II18nThumbnailImageField(II18nImageField):
    """I18n field for image with thumbnail marker interface"""


@implementer(II18nThumbnailImageField)
class I18nThumbnailImageField(I18nImageField):
    """I18n field for image with thumbnail"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=ThumbnailImageField(min_length=value_min_length,
                                           max_length=value_max_length,
                                           required=False),
            **kwargs)


class II18nVideoField(II18nMediaField):
    """I18n video field marker interface"""


@implementer(II18nVideoField)
class I18nVideoField(I18nMediaField):
    """I18n video field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=VideoField(min_length=value_min_length,
                                  max_length=value_max_length,
                                  required=False),
            **kwargs)


class II18nThumbnailVideoField(II18nVideoField):
    """I18n field for video with thumbnail marker interface"""


@implementer(II18nThumbnailVideoField)
class I18nThumbnailVideoField(I18nFileField):
    """I18n field for video with thumbnail"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=ThumbnailVideoField(min_length=value_min_length,
                                           max_length=value_max_length,
                                           required=False),
            **kwargs)


class II18nAudioField(II18nMediaField):
    """I18n audio field marker interface"""


@implementer(II18nAudioField)
class I18nAudioField(I18nMediaField):
    """I18n audio field"""

    def __init__(self, key_type=None, value_type=None,
                 value_min_length=None, value_max_length=None, **kwargs):
        # pylint: disable=bad-super-call
        super(I18nFileField, self).__init__(
            value_type=AudioField(min_length=value_min_length,
                                  max_length=value_max_length,
                                  required=False),
            **kwargs)
