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
"""Resource registration



$Id:$
"""
from __future__ import absolute_import
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.component
import zope.schema
import zope.configuration.fields
import zope.security.zcml
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import CheckerPublic
from zope.security.checker import NamesChecker
from zope.security.zcml import Permission
from zope.component.zcml import adapter
from zope.component.zcml import handler

import p01.cdn.layer
from p01.cdn import interfaces
from p01.cdn.resource import File
from p01.cdn.resource import ResourceFactory
from p01.cdn.resource import I18nResourceFactory
from p01.cdn.resource import ZRTResourceFactory
from p01.cdn.resource import DirectoryResourceFactory


allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                 'request', '__call__', 'uri')


###############################################################################
#
# directive interfaces

class IResourceManagerDirective(zope.interface.Interface):

    """ResourceManager (adapter) directive"""

    factory = zope.configuration.fields.Tokens(
        title=u"Adapter factory/factories",
        description=u"Adapter factory/factories",
        required=True,
        value_type=zope.configuration.fields.GlobalObject()
    )

    provides = zope.configuration.fields.GlobalInterface(
        title=u"Interface the resource manager provides",
        description=u"This attribute specifies the interface the adapter"
        u" instance must provide.",
        required=False,
    )

    layer = zope.configuration.fields.GlobalInterface(
        title=u"The layer the resource should be found in",
        description=u"The layer the resource should be found in",
        required=False
    )

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"Adapters can have names.\n\n"
                    u"This attribute allows you to specify the name for"
                    u" this adapter.",
        required=False,
    )

    permission = Permission(
        title=u"Permission",
        description=u"Permission",
        required=False,
    )

    # versions = zope.configuration.fields.Path(
    #     title=u"Resource name map used for (svn) versioning per resource",
    #     description=u"Resource name map used for (svn) versioning per resource",
    #     required=True
    # )


class IBasicResourceInformation(zope.interface.Interface):

    """Basic resource data."""

    manager = zope.schema.TextLine(
        title=u"Responsible resource manager name",
        description=u"""Responsible resource manager name
        This name is used for register as named adapter lookup. Note, normaly
        you only need to use a named resource manager and the resource manager
        name if you use more then one resource manager and you need to lookup
        resources from a resource manager from an inherited layer.""",
        required=False,
        default=u""
    )

    name = zope.schema.TextLine(
        title=u"The name of the resource",
        description=u"The resource adapter name.",
        required=True
    )

    layer = zope.configuration.fields.GlobalInterface(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False
    )

    permission = zope.security.zcml.Permission(
        title=u"The permission needed to access the resource.",
        description=u"""
        If a permission isn't specified, the resource will always be
        accessible.""",
        required=False
    )

    # you can use an optmized resource which is able to skip the resource
    # manager adapter lookup if you need even more speedup. Note, if a
    # z3c.baseregistry is involved, you need to make sure your resource
    # manager will get served from the right site component registry
    factory = zope.configuration.fields.Tokens(
        title=u"Resource factory",
        description=u"Resource factory",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
    )


class ICDNResourceDirective(IBasicResourceInformation):

    """Defines a browser resource with a explicit url.

    This allows to configure resources with custom urls. This is used if you
    like to cdn static resources form the zope and it's fornt end proxy
    server.
    """

    file = zope.configuration.fields.Path(
        title=u"File",
        description=u"The file containing the resource data.",
        required=False
    )


class IZRTCDNResourceDirective(ICDNResourceDirective):

    """Defines a ZRT browser resource with a explicit url."""


class ICDNI18nResourceDirective(IBasicResourceInformation):

    """Defines a directory containing files.

    The <p01:i18nResource> offers all files in the folder as i18n aware
    resources. This means the resource file must provide usefull locale names.

    Note, only files with the same file ending get uased as resources. And you
    can define exclude names which get not used as resources.
    """

    excludeNames = zope.schema.List(
        title=u"The names which get excluded from registration as resources",
        description=u"""This names get excluded from register as resources""",
        value_type=zope.schema.TextLine(
            title=u"Exclude name",
            description=u"Name to exclude from registration",
            required=True),
        required=False
    )

    directory = zope.configuration.fields.Path(
        title=u"Directory",
        description=u"The directory containing the resource data.",
        required=True
    )

    defaultLanguage = zope.schema.TextLine(
        title=u"Default language",
        description=u"Defines the default language",
        default=u'en',
        required=False
    )

    i18nFactory = zope.configuration.fields.Tokens(
        title=u"I18nResource factory",
        description=u"I18nResource factory",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
    )


class ICDNResourceDirectoryDirective(IBasicResourceInformation):

    """Defines a directory containing offload resources."""

    directory = zope.configuration.fields.Path(
        title=u"Directory",
        description=u"The directory containing the resource data.",
        required=True
    )

    excludeNames = zope.schema.List(
        title=u"The names which get excluded from traversing as resources",
        description=u"""This names get excluded from traversing as resources""",
        value_type=zope.schema.TextLine(
            title=u"Exclude name",
            description=u"Name to exclude from traversing as resource",
            required=True),
        required=False
    )


###############################################################################
#
# directives

def cdnResourceManager(_context, factory, layer=p01.cdn.layer.ICDNRequest,
    provides=None, name='', permission='zope.Public'):
    """Resource Manager (adapter) directive"""
    if provides is None:
        if len(factory) == 1:
            p = list(zope.interface.implementedBy(factory[0]))
            if len(p) == 1:
                provides = p[0]

        if provides is None:
            provides = interfaces.IResourceManager

    # register the resource manager adapter
    adapter(_context, factory, provides=provides,
            for_=(layer,), permission=permission, name=name, trusted=False,
            locate=False)


# lazy apply resource manager during registration does not work since we
# support the z3c.baseregistry. We need to lookup the right resource manager
# during calling a resource. Otherwise we can't ensure that we get the right
# resource manager
#def registerCDNResource(methodName, *args, **kwargs):
#    """Lazy apply resource manager and register resource"""
#    factory = args[0]
#    layer = args[1][0]
#    name = args[3]
#    sm = zope.component.getSiteManager()
#    mFactory = sm.adapters.lookup1(layer, interfaces.IResourceManager)
#    manager = mFactory(None)
#    factory.setResourceManager(manager)
#    method = getattr(sm, methodName)
#    method(*args, **kwargs)
def registerCDNResource(methodName, *args, **kwargs):
    """Lazy apply resource manager and register resource"""
    sm = zope.component.getSiteManager()
    method = getattr(sm, methodName)
    method(*args, **kwargs)


def cdnResource(_context, name, manager=u'', layer=p01.cdn.layer.ICDNRequest,
    permission='zope.Public', file=None, factory=ResourceFactory):
    """This cdn resource directive allows to register a file as resource"""

    if permission == 'zope.Public':
        permission = CheckerPublic

    rName = name
    pkgName = _context.context.package.__name__

    checker = NamesChecker(allowed_names, permission)
    obj = factory(file, checker, manager, name, pkgName=pkgName)

    _context.action(
        discriminator=('resource', name, IBrowserRequest, layer),
        callable=registerCDNResource,
        args=('registerAdapter', obj, (layer,), interfaces.ICDNResource,
              name, _context.info),
    )


def cdnZRTResource(_context, name, manager=u'', layer=p01.cdn.layer.ICDNRequest,
    permission='zope.Public', file=None, factory=ZRTResourceFactory):
    """This ZRT cdn resource directive allows to register a file as resource"""

    if permission == 'zope.Public':
        permission = CheckerPublic

    pkgName = _context.context.package.__name__

    checker = NamesChecker(allowed_names, permission)
    obj = factory(file, checker, manager, name, pkgName=pkgName)

    _context.action(
        discriminator=('resource', name, IBrowserRequest, layer),
        callable=registerCDNResource,
        args=('registerAdapter', obj, (layer,), interfaces.ICDNResource,
              name, _context.info),
    )


def cdnResourceDirectory(_context, name, manager=u'', directory=None,
                         excludeNames=[], layer=p01.cdn.layer.ICDNRequest,
                         permission='zope.Public',
                         factory=DirectoryResourceFactory):
    """This i18n cdn resource directive allows to register folders as
    resources.

    """
    if not os.path.isdir(directory):
        raise ConfigurationError("Directory %s does not exist" % directory)

    if permission == 'zope.Public':
        permission = CheckerPublic

    pkgName = _context.context.package.__name__

    checker = NamesChecker(allowed_names + ('__getitem__', 'get'), permission)

    obj = factory(directory, checker, manager, name, excludeNames=excludeNames,
        pkgName=pkgName)
    _context.action(
        discriminator=('resource', name, IBrowserRequest, layer),
        callable=registerCDNResource,
        args=('registerAdapter', obj, (layer,), interfaces.ICDNResource,
              name, _context.info),
    )


def cdnI18NResource(_context, name, manager=u'', directory=None,
                    defaultLanguage=u'en', excludeNames=[],
                    layer=p01.cdn.layer.ICDNRequest,
                    permission='zope.Public', i18nFactory=I18nResourceFactory,
                    factory=ResourceFactory):
    """This i18n cdn resource directive allows to register folders as
    resources.

    A resource must be a file name and the folder must contain files including
    this resource name and provide a locale with the file extension. e.g.
    logo-de.gif

    """
    if not os.path.isdir(directory):
        raise zope.configuration.exceptions.ConfigurationError(
            "Directory %s does not exist" % directory)

    # resource name, e.g. logo.gif
    if not '.' in name:
        raise zope.configuration.exceptions.ConfigurationError(
            "Resource %s must be a file name not a directory" % name)
    rName = os.path.splitext(name)[0]

    if permission == 'zope.Public':
        permission = CheckerPublic

    pkgName = _context.context.package.__name__

    checker = NamesChecker(allowed_names, permission)

    # collect relevant resource files
    data = {}
    for fName in os.listdir(directory):
        if fName in excludeNames:
            continue
        # never include (private) .svn folders
        elif fName.startswith('.'):
            continue
        # only include files starting with the same name as the resource name
        elif not fName.startswith(rName):
            raise zope.configuration.exceptions.ConfigurationError(
                "Resource %s must startwith resource name" % (fName, name))
        elif not '-' in fName:
            raise zope.configuration.exceptions.ConfigurationError(
                "Resource %s must contain a locale at the end separated with "
                "- e.g. logo-en.gif, logo-de.gif etc." % (fName, name))
        else:
            # setup resource name e.g. logo-de.gif
            # split file name into plain name and language locale, cut extension
            pName, pExt = os.path.splitext(fName)
            # extract language locale
            locale = pName.replace('%s-' % rName, '')
            # add the file as a tuple to the data dict
            path = os.path.join(directory, fName)
            data[locale] = File(path, fName)

            # register resource for each language used for traversal
            obj = factory(path, checker, manager, fName, pkgName=pkgName)
            _context.action(
                discriminator=('resource', fName, IBrowserRequest, layer),
                callable=registerCDNResource,
                args=('registerAdapter', obj, (layer,),
                      interfaces.ICDNResource, fName, _context.info),
            )

    # register i18n resource factory used for lookup via ++resource++foo
    obj = i18nFactory(data, checker, manager, name, defaultLanguage)
    _context.action(
        discriminator=('resource', name, IBrowserRequest, layer),
        callable=registerCDNResource,
        args=('registerAdapter', obj, (layer,), interfaces.ICDNResource,
              name, _context.info),
    )
