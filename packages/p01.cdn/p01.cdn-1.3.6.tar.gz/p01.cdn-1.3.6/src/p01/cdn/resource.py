##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Resource factories and resources

Note; our resource factories defined below, will process the uri based on the
given resource maanger during resource lookup. This is required since we
support the z3c.baseregistry. If you need more speedup, you can define your
own resource factories and use them in the resource zcml directives.

Especialy if you only use one resource manager, you can simply define a
resource manger and override the getResourceManager method in the resource
factories defined below.

$Id:$
"""

from __future__ import absolute_import

import os
import sys
import time
from builtins import object

import p01.cdn.exceptions
import p01.cdn.zrt
import pkg_resources
import zope.component
import zope.interface
import zope.location
import zope.publisher.http
from p01.cdn import interfaces
from p01.cdn.processor import ZRTProcessor
from p01.cdn.zrt import CDNReplace
from zope.component import hooks
from zope.contenttype import guess_content_type
from zope.i18n.interfaces import INegotiator
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserPublisher

try:
    from email.utils import formatdate
    from email.utils import parsedate_tz
    from email.utils import mktime_tz
except ImportError:
    # python 2.4
    from email.Utils import formatdate
    from email.Utils import parsedate_tz
    from email.Utils import mktime_tz

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode # p01.checker.silence
    binary_type = str
else:
    text_type = str
    binary_type = bytes

# package version cache
PKG_VERSION_CACHE = {}

# 10 years expiration date
DEFAULT_CACHE_TIMEOUT = 10 * 365 * 24 * 60 * 60

ZRT_REPLACE = u"""/* zrt-replace: "%(prefix)s%(rName)s" tal"string:${context/++resource++%(fName)s}" */
"""

ZRT_DIR_REPLACE = u"""/* zrt-replace: "%(prefix)s%(rName)s" tal"string:${context/++resource++%(dName)s/%(fName)s}" */
"""

def empty():
    """Callable empty string"""
    return ''


###############################################################################
#
# lazy (egg) package version extraction

def getPackageVersion(pkgName):
    """Returns the package version

    Note: resources define in egg packages are not under version control. We
    will use the egg package version. This has the benefit that such resource
    versions and the generated cdn resource url doesn't get changed for the
    same egg package version.

    All files located in your project and versioned in your svn repository
    will use the repository revision at the time they get commited. This has
    a little ugly side effect if you minify such resources. Then this means you
    need to commit a resource before minify them. After minify the minified
    resource will become another version and you need to setup/generate the
    resource version again. This could slown down the release process a bit.
    But the nice part is, you could automat that with p01.build and a buildbot
    server if you like.

    """
    # try to get the resource version. Note: this only works for resources
    # included from egg packages
    v = PKG_VERSION_CACHE.get(pkgName, None)
    if v is None:
        try:
            dist = pkg_resources.require(pkgName)[0]
            v = dist.version
            PKG_VERSION_CACHE[pkgName] = v
        except Exception:
            return None
    return v


###############################################################################
#
# cache control

def setCacheControl(response, seconds=DEFAULT_CACHE_TIMEOUT):
    # 10 years cache timeout by default
    response.setHeader('Cache-Control', 'public,max-age=%s' % seconds)
    t = time.time() + seconds
    response.setHeader('Expires', formatdate(t, usegmt=True))



###############################################################################
#
# file system file wrapper

class File(object):

    def __init__(self, path, name):
        self.path = path
        self.__name__ = name

        f = open(path, 'rb')
        data = f.read()
        f.close()

        self.content_type = guess_content_type(path, data)[0]
        self.lmt = float(os.path.getmtime(path)) or time.time()
        self.lmh = formatdate(self.lmt, usegmt=True)


###############################################################################
#
# cdn resource factories

class ResourceFactoryBase(object):
    """Resource factory base class

    name is the resource.__name__

    rName is the relative resource traversal path dir/sub/resource: This path
    is the relative traversal path from the cdn resource manger to the resource.
    The cdn resoure manager name is not a part of this name. The uri is built
    based on this name prefixed with the cdn manager base uri

    """

    def __init__(self, path, checker, manager, name, pkgName=None):
        self._file = File(path, name)
        self._checker = checker
        self._manager = manager
        # names used for relative path setup
        self._name = name
        # package version used for cdn extration for non svn files
        self._pkgName = pkgName

    def getResourceManager(self, request):
        """Returns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self._manager)

    def __call__(self, request):
        raise NotImplementedError("Subclass must implement __call__ method")


class ResourceFactory(ResourceFactoryBase):
    """Resource factory"""

    def __call__(self, request):
        manager = self.getResourceManager(request)
        uri = manager.getURI(self._name)
        resource = CDNResource(manager, self._file, request, uri,
            rName=self._name, pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


class ZRTResourceFactory(ResourceFactoryBase):
    """ZRT Resource factory."""

    def __call__(self, request):
        manager = self.getResourceManager(request)
        uri = manager.getURI(self._name)
        resource = ZRTCDNResource(manager, self._file, request, uri,
            rName=self._name, pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


class I18nResourceFactory(object):
    """I18n resource factory."""

    def __init__(self, data, checker, manager, name, defaultLanguage,
        pkgName=None,):
        self.__data = data
        self.__uris = []
        self._manager = manager
        self._name = name
        self.__defaultLanguage = defaultLanguage
        self._checker = checker
        # package version used for cdn extration for non svn files
        self._pkgName = pkgName

    def getResourceManager(self, request):
        """Returns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self._manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource = I18nCDNResource(manager, self.__data, request,
            self.__defaultLanguage, rName=self._name, pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


class SubResourceFactory(ResourceFactoryBase):
    """Resource factory"""

    def __init__(self, path, checker, manager, name, rName=None, pkgName=None):
        super(SubResourceFactory, self).__init__(path, checker, manager, name,
            pkgName=pkgName)
        self._rName = rName

    def __call__(self, request):
        manager = self.getResourceManager(request)
        uri = manager.getURI(self._rName)
        resource = CDNResource(manager, self._file, request, uri,
            rName=self._rName, pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


class SubDirectoryResourceFactory(object):
    """Sub directory resource factory"""

    def __init__(self, data, path, checker, manager, name, rName=None,
        excludeNames=None, pkgName=None):
        self.data = data
        self._path = path
        self._checker = checker
        self._manager = manager
        self._name = name
        self._rName = rName
        if excludeNames is None:
            excludeNames = []
        self._excludeNames = excludeNames
        # package version used for cdn extration for non svn files
        self._pkgName = pkgName

    def getResourceManager(self, request):
        """Returns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
                                         name=self._manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource = CDNResourceDirectory(manager, self.data, request,
            self._path, self._name, rName=self._rName,
            excludeNames=self._excludeNames, pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


class DirectoryResourceFactory(object):
    """Directory resource factory"""
    data = {}

    def __init__(self, path, checker, manager, name, excludeNames=None,
        pkgName=None):
        self._path = path
        self._checker = checker
        self._manager = manager
        self._name = name
        if excludeNames is None:
            excludeNames = []
        self._excludeNames = excludeNames
        # package version used for cdn extration for non svn files
        self._pkgName = pkgName
        self.setupData()

    def getStructure(self, path, data, rNameBase):
        """Populate the directory structure with the right factories during
        zcml configuration loading.

        This allows us to read and setup the directory and file factories
        without to define the uri during zcml configuration. The uri will still
        get built based on the resource manager during resource access.

        """
        for name in os.listdir(path):
            if name.startswith('.'):
                continue
            if name in self._excludeNames:
                continue
            data[name] = {}
            # setup relative resource name
            rName = '%s/%s' % (rNameBase, name)
            objPath = os.path.join(path, name)
            if os.path.isdir(objPath):
                rNameNewBase = '%s/%s' % (rNameBase, name)
                subData = self.getStructure(objPath, {}, rNameNewBase)
                data[name]['factory'] = SubDirectoryResourceFactory(
                    subData, path, self._checker, self._manager,
                    name, rName=rName, excludeNames=self._excludeNames,
                    pkgName=self._pkgName)
            else:
                data[name]['factory'] = SubResourceFactory(
                    objPath, self._checker, self._manager, name, rName=rName,
                    pkgName=self._pkgName)
        return data

    def setupData(self):
        """Setup directory structure"""
        # condition
        if not os.path.isdir(self._path):
            raise TypeError(
                "p01.cdnDirectory must be a directory", self._path)
        # get base path for given directory and start producing nested
        # directory and file structure
        rNameBase = self._name
        self.data = self.getStructure(self._path, {}, rNameBase)

    def getResourceManager(self, request):
        """Returns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self._manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource = CDNResourceDirectory(
            manager, self.data, request, self._path, self._name,
            rName=self._name, excludeNames=self._excludeNames,
            pkgName=self._pkgName)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


###############################################################################
#
# extraction and  publisher

class CDNExtractMixin(object):
    """CDN resource extraction mixin class"""

    rName = None

    def getRelativePath(self, name):
        """Return the relative resource path"""
        # NOTE: by default the name is the resource.rName only the i18n
        # resource is using the lang as name
        return self.rName


@implementer(IBrowserPublisher)
class ResourcePublisher(CDNExtractMixin):
    """Knows how to serv a resource."""


    # 10 years expiration date
    cacheTimeout = DEFAULT_CACHE_TIMEOUT

    def publishTraverse(self, request, name):
        """Raise NotFound if someone tries to traverse it"""
        raise p01.cdn.exceptions.ResourceNotFound(self, name)

    def browserDefault(self, request):
        """Return a callable for processing browser requests."""
        return getattr(self, request.method), ()

    def doGET(self, context):
        """Return the file data for downloading with GET requests."""
        request = self.request
        response = request.response

        setCacheControl(response, self.cacheTimeout)

        # HTTP If-Modified-Since header handling..
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:
                mod_since = int(mktime_tz(parsedate_tz(header)))
            except:
                mod_since = None
            if mod_since is not None:
                if getattr(context, 'lmt', None):
                    last_mod = int(context.lmt)
                else:
                    last_mod = 0
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        response.setHeader('Content-Type', context.content_type)
        response.setHeader('Last-Modified', context.lmh)

        f = open(context.path, 'rb')
        data = f.read()
        f.close()
        return data

    def GET(self):
        """Return the file data for downloading with GET requests."""
        return self.doGET(self.context)

    def HEAD(self):
        """Return proper headers and no content for HEAD requests."""
        response = self.request.response
        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Last-Modified', self.context.lmh)
        setCacheControl(response, self.cacheTimeout)
        return ''

###############################################################################
#
# cdn resources

@implementer(interfaces.ICDNResource)
class CDNResource(ResourcePublisher, zope.location.Location):
    """CDN resource implementation."""


    def __init__(self, manager, context, request, uri, rName=None, pkgName=None):
        self.manager = manager
        self.context = context
        self.path = context.path
        self.request = request
        self.uri = uri
        # cdn extract attrbutes
        self.rName = rName
        # package version used for cdn extration for non svn files
        self.pkgName = pkgName

    @property
    def pkgVersion(self):
        """Lazy package version based on package name"""
        return getPackageVersion(self.pkgName)

    @property
    def rNameDirectory(self):
        if self.rName is not None and '/' in self.rName:
            return self.rName.split('/')[0]
        else:
            # self.__parent__ and rName setup seems to be broken
            return u"BAD/CDNResource/dName/%s" % self.rName

    @property
    def rNameWithoutDirectory(self):
        if self.rName is not None and '/' in self.rName:
            return '/'.join(self.rName.split('/')[1:])
        else:
            # self.__parent__ and rName setup seems to be broken
            return u"BAD/CDNResource/rNameWithoutDirectory/%s" % self.rName

    def getZRTReplace(self, name, version, options):
        """Returns the related zrt-replace directive"""
        prefix = options.zrtPrefixes.get(self.rName)
        if self.rName is not None and '/' in self.rName:
            if prefix is None:
                prefix = options.zrtDirPrefix
            return ZRT_DIR_REPLACE % {
                'prefix': prefix and prefix or '',
                'rName': self.rName,
                'dName': self.rNameDirectory,
                'fName': self.rNameWithoutDirectory,
                }
        else:
            if prefix is None:
                prefix = options.zrtPrefix
            return ZRT_REPLACE % {
                'prefix': prefix and prefix or '',
                'rName': self.rName,
                'fName': self.__name__,
                }

    def __call__(self):
        return self.uri

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


@implementer(interfaces.IZRTCDNResource)
class ZRTCDNResource(CDNResource):
    """ZRT CDN resource implementation."""

    def _encodeResult(self, data):
        response = self.request.response
        encoding = zope.publisher.http.getCharsetUsingRequest(self.request) or 'utf-8'
        content_type = response.getHeader('Content-Type') or ''

        if isinstance(data, text_type):
            major, minor, params = zope.contenttype.parse.parse(content_type)

            if 'charset' in params:
                encoding = params['charset']

            try:
                data = data.encode(encoding)
            except UnicodeEncodeError:
                encoding = 'utf-8'
                data = data.encode(encoding)

            params['charset'] = encoding
            content_type = "%s/%s" % (major, minor)
            content_type += ";" + ";".join("%s=%s" % (k, v) for k, v in list(params.items()))
            response.setHeader('Content-Type', content_type)

        elif not isinstance(data, binary_type):
            raise TypeError("Expected text or bytes, got: %s" % type(data))

        response.setHeader('Content-Length', str(len(data)))
        return data

    def GET(self):
        data = super(ZRTCDNResource, self).GET()
        zp = ZRTProcessor(data, commands={'replace': CDNReplace})
        # Note: we run into a ValueError because of using unicode
        # with application/javascript content_type.
        # Use a DirectResult which will bypass the _implicitResult
        # method from zope.publisher.http line 799
        # return zp.process(hooks.getSite(), self.request)

        # bugfix, encode and use DirectResult
        data = zp.process(hooks.getSite(), self.request)
        body = self._encodeResult(data)
        return zope.publisher.http.DirectResult((body,))


@implementer(interfaces.II18nCDNResource)
class I18nCDNResource(ResourcePublisher, zope.location.Location):
    """I18n CDN resource implementation."""


    _locale = None
    __rNameBase = None

    def __init__(self, manager, data, request, defaultLanguage, rName=None,
        pkgName=None):
        self.manager = manager
        self._data = data
        self.request = request
        self.defaultLanguage = defaultLanguage
        self._locale = self.defaultLanguage
        self.rName = rName
        # keep original rName as reference
        self.__rNameBase = rName
        # package version used for cdn extration for non svn files
        self.pkgName = pkgName

    @property
    def pkgVersion(self):
        """Lazy package version based on package name"""
        return getPackageVersion(self.pkgName)

    def getNameForLocale(self, locale=None):
        """Get resource name for locale"""
        if locale is None:
            locale = self.locale
        if not locale or locale not in self._data:
            locale = self.defaultLanguage
        name, ext = os.path.splitext(self.__rNameBase)
        return '%s-%s%s' % (name, self.locale, ext)

    def getAvailableLocales(self):
        """Returns available locales"""
        for locale in list(self._data.keys()):
            yield locale

    def locale():
        """Switch locale and resource name (rName) for extraction"""
        def fget(self):
            return self._locale
        def fset(self, locale):
            if self._locale != locale:
                if locale in self._data:
                    self._locale = locale
                else:
                    self._locale = self.defaultLanguage
                # switch rName for given locale
                self.rName = self.getNameForLocale(self._locale)
        return property(fget, fset)

    locale = locale()
    @property
    def path(self):
        """Return file path for extraction"""
        f = self._data[self.locale]
        return f.path

    def getExtractableResources(self):
        for locale in self.getAvailableLocales():
            # switch locale
            self.locale = locale
            yield self
        # reset to default locale
        self._locale = self.defaultLanguage
        self.rName = self.__rNameBase

    # cdn extract api
    def getRelativePath(self, name):
        """Return the relative resource path"""
        return self.rName

    def getZRTReplace(self, name, version, options):
        """Returns the related zrt-replace directive"""
        prefix = options.zrtPrefixes.get(self.rName)
        if prefix is None:
            prefix = options.zrtPrefix
        return ZRT_REPLACE % {
            'prefix': prefix and prefix or '',
            'rName': self.rName,
            'fName': self.__name__,
            }

    def getURI(self, locale):
        rName = self.getNameForLocale(locale)
        return self.manager.getURI(rName)

    def getPath(self, locale):
        f = self._data[locale]
        return f.path

    def getPaths(self):
        """Used for extract paths, see p01.recipe.cdn/extract.py"""
        for f in list(self._data.values()):
            yield f.path

    def getURIs(self):
        """Used for extract uris, see p01.recipe.cdn/extract.py"""
        for locale in list(self._data.keys()):
            yield self.getURI(locale)

    # serving resource data
    def setUpRequestLocale(self):
        """Setup negotiated locale"""
        langs = list(self._data.keys())
        negotiator = zope.component.getUtility(INegotiator)
        self.locale = negotiator.getLanguage(langs, self.request)

    def GET(self):
        """Return the file data for downloading with GET requests."""
        # first ensure a context
        self.setUpRequestLocale()
        try:
            context = self._data[self.locale]
        except KeyError:
            context = self._data[self.defaultLanguage]
        return self.doGET(context)

    def __call__(self):
        """Returns the uri for serve as cdn resource"""
        self.setUpRequestLocale()
        try:
            return self.getURI(self.locale)
        except KeyError:
            return self.getURI(self.defaultLanguage)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


# Directory resource
@implementer(interfaces.ICDNResourceDirectory)
class CDNResourceDirectory(ResourcePublisher, zope.location.Location):


    def __init__(self, manager, data, request, path, name, rName=None,
                 excludeNames=None, pkgName=None):
        self.manager = manager
        self.data = data
        self.request = request
        self.path = path
        self.__name__ = name
        self.rName = rName
        if excludeNames is None:
            excludeNames = []
        self.excludeNames = excludeNames
        # package version used for cdn extration for non svn files
        self.pkgName = pkgName

    @property
    def pkgVersion(self):
        """Lazy package version based on package name"""
        return getPackageVersion(self.pkgName)

    def publishTraverse(self, request, name):
        """See interface IBrowserPublisher"""
        return self.get(name)

    def browserDefault(self, request):
        """See interface IBrowserPublisher"""
        return empty, ()

    @property
    def uri(self):
        return self()

    def __call__(self):
        return self.manager.getURI(self.rName)

    def __getitem__(self, name):
        """Retruns a resource from the folder

        Raises KeyError if not found.
        """
        res = self.get(name, None)
        if res is None:
            raise KeyError(name)
        return res

    def get(self, name, default=None):
        """Retruns a resource from the folder

        Raises p01.cdn.exceptions.ResourceNotFound if not found.
        """
        if name not in self.excludeNames:
            data = self.data.get(name)
            if data is not None:
                factory = data['factory']
                resource = factory(self.request)
                resource.__parent__ = self
                return resource
        # we don't return default, we raise not available
        raise p01.cdn.exceptions.ResourceNotFound(self, name)
