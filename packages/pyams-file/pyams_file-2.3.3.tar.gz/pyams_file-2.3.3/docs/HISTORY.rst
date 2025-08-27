Changelog
=========

2.3.3
-----
 - updated file view range handler

2.3.2
-----
 - added check on file property setter

2.3.1
-----
 - small refactoring to remove duplicated code

2.3.0
-----
 - updated subscribers and helpers to correctly handle files deletion

2.2.0
-----
 - added support for WebP, AVIF and HEIF/HEIC images formats using custom Pillow plugins
 - set WebP as default thumbnails image format
 - allow setting of preferred or imposed thumbnails image format into configuration

2.1.0
-----
 - added support for Python 3.12
 - when setting a property-file value using a "(filename, data)" tuple, you can also set
   content-type (including an optional charset) by using a "filename; content-type" syntax in
   the first tuple value

2.0.3
-----
 - added filename conversion in file download view

2.0.2
-----
 - allow setting of file property field value from CGI FieldStorage

2.0.1
-----
 - upgraded Buildout configuration

2.0.0
-----
 - migrated to Pyramid 2.0
 - added support for Python 3.11
 - updated resampling settings for last Pillow version

1.6.4
-----
 - automatically remove diacritics from provided file name

1.6.3
-----
 - specify supported methods in CORS requests handler

1.6.2
-----
 - added CORS requests handler support to file view

1.6.1
-----
 - added support for Python 3.10
 - moved TALES extensions to *pyams_file_views* package

1.6.0
-----
 - added "selections" argument to *picture* TALES extension (see new PyAMS_skin
   *BootstrapThumbnailsSelectionDictField* schema field
 - updated *content-disposition* header handler in file view

1.5.5
-----
 - corrected doctests

1.5.4
-----
 - updated SVG image rendering

1.5.3
-----
 - package upgrade because of version mismatch

1.5.2
-----
 - added image helper to get selection thumbnail

1.5.1
-----
 - updated testing dependencies

1.5.0
-----
 - added images thumbnailers vocabulary
 - updated "pictures" TALES extension

1.4.0
-----
 - removed support for Python < 3.7
 - updated doctests

1.3.0
-----
 - added IBlobsReferencesManager factory configuration
 - removed Travis-CI configuration

1.2.5
-----
 - added commit into thumbnails traverser to avoid exceptions for uncommitted blobs
 - updated "adapter_config" arguments names
 - updated doctests

1.2.4
-----
 - updated doctests

1.2.3
-----
 - updated tests with ZCA hook

1.2.2
-----
 - updated tests for correct execution in Travis

1.2.1
-----
 - Pylint code cleanup and improved tests

1.2.0
-----
 - changed File blob's mode in context manager to readonly
 - removed intermediate commits in thumbnails traverser
 - updated file properties to be able to remove an attribute and unreference files objects
   accordingly
 - added subscriber to correctly remove all referenced files when a parent object is removed
 - refactored archives extraction utilities
 - improved tests and coverage

1.1.2
-----
 - updated Travis authentication token

1.1.1
-----
 - updated doctests for Travis-CI
 - updated Travis-CI configuration

1.1.0
-----
 - added watermark opacity argument to IThumbnails.get_thumbnail interface
 - added support for Bootstrap 'xl' responsive image size
 - updated SVG images renderer
 - updated doctests

1.0.1
-----
 - use current request registry instead of global registry to query adapters

1.0.0
-----
 - initial release
