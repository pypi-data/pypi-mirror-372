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
"""
$Id:$
"""
from __future__ import absolute_import
from zope.interface import implementer
from builtins import object
__docformat__ = "reStructuredText"

import json
import os.path
import posixpath

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from p01.cdn import interfaces


ZRT_START = u"""/*---[ START: zrt-replace.less ]----------------------------------------------*/
"""

ZRT_END = u"""/*---[ END: zrt-replace.less ]------------------------------------------------*/
"""


@implementer(interfaces.IResourceManager)
class ResourceManager(object):
    """Resource Manager"""


    _version = FieldProperty(interfaces.IResourceManager['version'])
    _namespace = FieldProperty(interfaces.IResourceManager['namespace'])
    _skin = FieldProperty(interfaces.IResourceManager['skin'])
    _site = FieldProperty(interfaces.IResourceManager['site'])
    rawURI = FieldProperty(interfaces.IResourceManager['rawURI'])
    _uri = FieldProperty(interfaces.IResourceManager['uri'])
    _output = FieldProperty(interfaces.IResourceManager['output'])
    useSVNVersions = FieldProperty(
        interfaces.IResourceManager['useSVNVersions'])
    svnVersionSourcePath = FieldProperty(
        interfaces.IResourceManager['svnVersionSourcePath'])
    zrtDirReplaces = FieldProperty(interfaces.IResourceManager['zrtDirReplaces'])
    zrtReplaces = FieldProperty(interfaces.IResourceManager['zrtReplaces'])
    svnZRTReplacePath = FieldProperty(
        interfaces.IResourceManager['svnZRTReplacePath'])
    versions = FieldProperty(interfaces.IResourceManager['versions'])

    def __init__(self, version, uri, output=None, namespace=None, skin=None,
        site=None, useSVNVersions=False, svnVersionSourcePath=None,
        svnZRTReplacePath=None):
        # set uri arguments
        self.version = version
        self.namespace = namespace
        self.skin = skin
        self.site = site
        # setup converted uri
        self.uri = uri
        # setup output
        self.output = output
        # subversion and package version based resource versioning
        self.useSVNVersions = useSVNVersions
        self.svnVersionSourcePath = svnVersionSourcePath
        self.svnZRTReplacePath = svnZRTReplacePath
        self.setUpVersions()

    def setUpVersions(self):
        """Load extracted resource versions"""
        self.versions = {}
        self.zrtDirReplaces = u''
        self.zrtReplaces = u''
        if self.svnVersionSourcePath is not None:
            if not os.path.exists(self.svnVersionSourcePath):
                f = open(self.svnVersionSourcePath, 'wb')
                f.close()
            # use version (don't enable during extraction)
            if self.useSVNVersions:
                f = open(self.svnVersionSourcePath, 'rb')
                fData = f.read()
                f.close()
                if fData:
                    self.versions = json.loads(fData)

    def addVersion(self, name, resource, options):
        """Add resource version

        The name is the traversable resource lookup name. The rName is the
        resource name and the fName is the external file name.

        NOTE: this method is only used during resource version setup. This
        optional step is only used if you use file based resource versions.
        The p01.recipe.cdn setup script is using this method for apply the
        version for each file based on svn repository or egg package version
        if the resource is located in an egg package.

        Note: you can simply implement your own version lookup concept if you
        use GIT or another concept. This method is all you need for define and
        setup the right version for the given resource. The p01.recipe.cdn
        extract method will later lookup the version for each file from the
        prepopulated self.versions dict.
        """
        # find svn or package version
        version = options.svn.getRevision(resource)
        # add zrt-repalce directive (p01.recipe.cdn extract will save them)
        zrtReplace = resource.getZRTReplace(name, version, options)
        if zrtReplace is not None:
            if resource.__parent__ is not None:
                self.zrtDirReplaces += zrtReplace
            else:
                self.zrtReplaces += zrtReplace
        # add version (p01.recipe.cdn extract will save them)
        # now, use resource.rName whcih could be different then the given name
        # attribute. Ok, most the time it's the same name but it could be
        # different if you implement some magic directory with a naming pattern
        # like we do with our i18n resources where we generate the rName
        f1, f2 = os.path.splitext(resource.rName)
        fName = '%s.v%s%s' % (f1, version, f2)
        self.versions[resource.rName] = fName
        return fName

    def checkVersions(self):
        """Check changed versions (used before write new files)

        Note: write a new file forces the less compiler to comile less to css.
        We will prevent this in p01.recipe.cdn if we didn't have new versions
        """
        if self.svnVersionSourcePath is not None:
            if os.path.isfile(self.svnVersionSourcePath):
                try:
                    f = open(self.svnVersionSourcePath, 'rb')
                    org = json.loads(f.read())
                    f.close()
                except ValueError:
                    # ValueError: No JSON object could be decoded
                    # empty file or bad format, mark as changed
                    return False
            else:
                org = {}
            if self.versions == org:
                # version not changed
                return True
            else:
                # version changed
                return False
        else:
            # version config not found on file system
            return False

    def saveVersions(self):
        """Store version mapping and zrt-replace.less in file system

        NOTE: this method is only used during resource extraction
        """
        # write cdn.json file
        if self.svnVersionSourcePath is not None:
            data = json.dumps(self.versions, indent=4, sort_keys=True)
            f = open(self.svnVersionSourcePath, 'wb')
            f.write(data)
            f.close()

    def saveZRTReplace(self):
        """Store version mapping and zrt-replace.less in file system

        NOTE: this method is only used during resource extraction
        """
        # write zrt-include.less file
        if self.svnZRTReplacePath is not None:
            data = ZRT_START
            data += self.zrtDirReplaces
            data += self.zrtReplaces
            data += ZRT_END
            f = open(self.svnZRTReplacePath, 'wb')
            f.write(data)
            f.close()

    def _convert(self):
        """Converts previous set uri with dynamic values

        This ensures that we convert the uri during change on everytime we
        access them.
        """
        version = self.version or 'missing-version'
        namespace = self.namespace or 'missing-namespace'
        skin = self.skin or 'missing-skin'
        site = self.site or 'missing-site'
        self._uri = self.rawURI % {'version': version,
            'namespace': namespace, 'skin': skin, 'site': site}

    def version():
        def fget(self):
            return self._version
        def fset(self, value):
            self._version = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    version = version()
    def namespace():
        def fget(self):
            return self._namespace
        def fset(self, value):
            self._namespace = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    namespace = namespace()
    def skin():
        def fget(self):
            return self._skin
        def fset(self, value):
            self._skin = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    skin = skin()
    def site():
        def fget(self):
            return self._site
        def fset(self, value):
            self._site = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    site = site()
    def uri():
        def fget(self):
            return self._uri
        def fset(self, uri):
            # keep a reference to the uri including formatting strings
            self.rawURI = uri
            self._convert()
        return property(fget, fset)

    uri = uri()
    def output():
        """Return dynamicly converted output path"""
        def fget(self):
            if self._output is not None:
                return self._output % {
                    'version': self.version,
                    'namespace': self.namespace,
                    }
            else:
                return self._output
        def fset(self, output):
            self._output = output
        return property(fget, fset)

    output = output()
    def getExtractFileName(self, name, resource):
        """Returns the relative resource path on extraction"""
        # get name from cdn.json resource version map or use given name
        rName = resource.getRelativePath(name)
        # check version map for correct resource name by relative resource path
        rName = self.versions.get(rName, rName)
        # just return the filename including a version if any
        return rName.split('/')[-1]

    def getURI(self, name=None):
        """Get the correct url based on the uri, namespace and version and
        resource name.

        We also, allow to use * as a version manager marker.

        An initial devmode uri could look like:

        http://localhost:8080/++skin++Admin/%(version)s/@@

        If your applicatiton uses site and subsite and each sub site is using
        another resource manager, the relative subsite path could get used
        as namespace. Then your uri could look like:

        http://localhost:8080/++skin++Admin/%(namespace)s/%(version)s/@@

        And the sub site could be set to something like: "root/subsite"

        A production setup does not require any special uri setup in general.
        It fully depends on your web servers rewrite rule and your extracted
        resource location. You will probably use a sub domain like:

        http://%(namespace)s.foobar.com/%(version)s/@@

        or with an additional namespace:

        http://cdn.foobar.com/%(namespace)s/%(version)s/@@

        or just as minimal as possible

        http://cdn.foobar.com/%(version)s/@@

        Note: you can also use the site and skin as a part of the uri
        formatting.

        """
        if name is None:
            # return base uri
            return self.uri
        else:
            # get name from cdn.json resource version map or use given name
            name = self.versions.get(name, name)
            # return resource uri
            return posixpath.join(self.uri, name)

    def __call__(self, request):
        """Let the instance act as an adapter if needed"""
        return self

    def __repr__(self):
        return '<%s %r at %r>' %(self.__class__.__name__, self.version,
            self.uri)
