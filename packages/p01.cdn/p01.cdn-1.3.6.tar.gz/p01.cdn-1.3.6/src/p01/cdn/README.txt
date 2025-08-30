========================
Content Delivery Network
========================

The content delivery network (p01.cdn) package provides several concepts:

- delivers resources within a custom uri concept. This allows to offloads
  resources to a web server

- supports a version string for each uri. This prevents caching updated
  resources without to explicit change the resource name or uri.

- allows to serve resources from application server during development

The main goal of this package is to provide custom urls for each resource which
do not point back to the zope application server. This allows to off load
resources from the application server and serve them as static files from
a web server. An important point in such a concept is, that we can change such
(client cached) resource uris if we update scripts or images. Our version makes
sure that a resource uri get changed if we change the resource manger version.


Concepts
--------

This package provides two concepts.

The first concept uses a global cdn manager version. This means each resource
contains this resource manager version for identify the resource. This is
simple to use and it's vers simple to understand what's going on. You simply
define a cdn manager with version string and this string is a part of the
resource url. This concept has a conceptual side effect. If you change one
file, you need to change the cdn manager version number. This means all your
resources will get a new uri and thsi will force each browser to load all
resources again even if they didn't get changed. If this limitation is critical
for you then use the second concept which will version each file with it's own
version. But be warned, it's really hard to understand and do that right and
it brings a couple of extra steps into your development or release stack.
But the nice part is, you could everything automate without any user
interaction using a buildot server.

The second concept is on the first view also simple. We use the svn respository
version from when the resource get commited to the repository and the resource
url provides this repository version. As a fallback if a resource is not
versioned in the repository, it must came from a python package (egg). Then we
simply use the egg version as a part of the resource url. This sounds simple
right? But it's not so simply if you take a close look at the other concepts
related to resources e.g. minify and zrt (zope resource templates).
The good part is it works with zrt resources and minfied files. But it's a bit
complicated to understand what's going on on. Let's that explain a bit more.
If you have an image resource in your project (svn repos), you can add them, commit them to the repository and it will get a repository version number.
Thsi version numer does not get changed till you change the resource and commit
the changes to the repository. That was simple. Let's take a look at CSS files.
CSS files will reference images. This means an image must get versioned in the
repository before you can correct reference them. And correct reference them
makes only sense if you use the zrt (zope resource template) concept otherwise
you will need to change the image src in the CSS file everytime you change the
image itself. ZRT does this implicit.

But now some words on the resource version generation. We will generate the
correct resource version (from svn or egg package) with a recipe script called
p01.recipe.cdn:setup. The setup method will first lookup and write all versions
for each file into a cdn.json file. After that, each resource will use that
file for lookup it's version. This means if you change a file you need to
setup the versions again. After that, you can extract cdn resources with
p01.recipe.extract. That was abit complex but it's more or less straight
forward. Let's take a look what happens if you minifiy such extracted resources.
The minify recipe located in p01.recipe.cd:minify will generate a new minified
CSS file and this file neeeds to get commited to the repository. Then, again
you need to setup the versions and extract the files again. Only after this
secound rountrip will you get the right minified resource (version).


Summary
-------

This package provides the following concepts:

- The application server generates resource uris which will point to another
  domain then the application server uses. This will force to off load the
  resource and serve it from another web server

- During development a devmode uri can get defined. This allows to server
  the resource from the application server

- A resource manager supports to generate a unique url for resources. This is
  usefull because we use a built in default cache timeout of 10 years

- The application server can force to off load resources to a content delivery
  network like Nakami if you define the content delivery network server as uri
  and upload the resources to such a CDN server.

Note, there are two different kind of content delivery network concepts which
this package can provide. You can define an uri where the resources get served
from. If so, the resources get served from this content server. Or you can
define the application server uri as the resource uri. Then you can setup
a content delivery network proxy server which caches the resources based on
the default 10 year cache settings. In this case, the version number offered
from p01.cdn makes sure that the same resource doesn't get cached forever
from the external content delivery network.


The Resource Manager
--------------------

The Resource Manager is a central component that provides a version. It is up
to the rescource manager to decide whether the version is for example based on
a tag, a revision number, the package version number or a manually entered
version etc. Such a version get used as a part of the resource url.
This allows us to use a long cache time without to loose to option to replace
the resources (uri). We simply can bump up our version number which will force
to use another url for each resource without to rename the resource itself.

The Resource Manager is also responsible for define the output directory. The
buildout extract recipe defined in p01.recipe.cdn is able to extract resources
to a location defined from the relevant Resource Manager or given as output
recipe option.

The Resource Manager is also responsible for define the uri for each resource.
During the resource zcml configuration (startup) the Rescource Manager adapter
get called and prepopulates the resources including nested directories.
Later during resource processing the resource manager get asked for the
resource uri.

The Rescource Manager is implemented as an adapter adapting a request. This
allows to use different Resource Manager providing different uri and output
locations. We alsoo support the z3c.baseregistry pattern. this means you can
override the resource maanger for a different site providing another component
registre given from z3c.baseregistry.

NOTE: since the IResourceManager is an adapter adapting a request, we support
the layer and skin pattern like for any other view/pages. This means we
can inherit resources from a base or a specific resource manager depending
on it's layer configuration. This is probably not so simple to understand but
allows to inherit base resources without to re-register them everywhere. And
much more important this inheritation allows to partial update resources if you
register them carfully with different resource managers. An important part
in such a multi resource manager setup is the resource manager namespace
property. This property is responsible for generate a namespace where you can
use for rewrite rules in your web server configuration. But as I told above,
take care such a configuration is not easy to setup. You also need to think
about how you extract your resources to different locations for a working
rewrite concept. In general there is no simple rule for setup more then
one resource manager in one application server setup. You will probably
need the resource manager namespace property and different output locations
for a working setup.

Now let's setup a sample resource manager:


  >>> import os
  >>> import os.path
  >>> import zope.interface
  >>> import zope.component
  >>> import p01.cdn
  >>> from p01.cdn import interfaces
  >>> from p01.cdn import layer
  >>> from p01.cdn import manager
  >>> samplesDir = os.path.join(os.path.dirname(p01.cdn.__file__), 'samples')

This package provides a simple resource manager implementation. We will setup
them with a version number and an external uri:

  >>> VERSION = '1.0.0'
  >>> URI = 'http://www.foobar.tld'
  >>> manager = manager.ResourceManager(VERSION, URI)
  >>> manager
  <ResourceManager '1.0.0' at 'http://www.foobar.tld'>

Let's now register the version manager, so that it is available for later use:

  >>> @zope.component.adapter(layer.ICDNRequest)
  ... @zope.interface.implementer(interfaces.IResourceManager)
  ... def getCDNResourceManager(request):
  ...     return manager

  >>> zope.component.provideAdapter(getCDNResourceManager)


Resource Traversal
------------------

Zope uses a special, empty-named view to traverse resources from a site like
this:

  <site>/@@/<resource-path>

With the p01.cdn concept, we will support URLs like this:

  <site>/@@/<version>/<resource-path>

That means that we need a custom implementation of the resources view that can
handle the resource version number.

  >>> from zope.publisher.browser import TestRequest
  >>> from p01.cdn.resources import VersionResources
  >>> from p01.cdn.resources import Resources

  >>> request = TestRequest()
  >>> zope.interface.alsoProvides(request, layer.ICDNRequest)
  >>> context = object()

  >>> resources = VersionResources(context, request)

The resources object is a browser view:

  >>> resources.__parent__ is context
  True
  >>> resources.__name__

The view is also a browser publisher. But it does not support a default:

  >>> resources.browserDefault(request)
  (<function empty at ...>, ())

When traversing to a sub-item, the version can be specified:

  >>> resources.publishTraverse(request, '1.0.0')
  <Resources '1.0.0'>

The result of the traversal is the real resources object. When asking for
an unknown resource or version, a ``ResourceNotFound`` is raised which is a
NotFound error and allows us to register a page. This page doesn't provide the
default NotFound template and layout:

  >>> try:
  ...   resources.publishTraverse(request, 'missing')
  ... except p01.cdn.exceptions.ResourceNotFound as ex:
  ...   print(ex)
  (<VersionResources...>, 'missing')


A regular resource does not honor the version element. That's because
it's ``__call__()`` method defines how the URL is constructed, which is
ignorant of the version.

So let's use this package's implementation of a resource factory which will
act as a single named adapter providing a __call__ method for adaption. First
get a resource file:

  >>> from p01.cdn.resource import File
  >>> from p01.cdn.resource import ResourceFactory
  >>> rName = 'test.gif'
  >>> samples = os.path.join(os.path.dirname(p01.cdn.__file__), 'samples')
  >>> file = File(os.path.join(samples, rName), rName)

Now we have to setup the correct uri. This is normaly done based on a product
configuration or ennvironment variable. Let's just define a different base uri
for our resource maanger:

  >>> manager.uri = 'http://images.projekt01.com'
  >>> rm = getCDNResourceManager(request)
  >>> rm
  <ResourceManager '1.0.0' at 'http://images.projekt01.com'>

and setup a resource:

  >>> rPath = os.path.join(samples, rName)
  >>> resourceFactory = ResourceFactory(rPath, None, u'', rName)

As you can see, our resource factory knows our resource manager:

  >>> rm = resourceFactory.getResourceManager(request)
  >>> rm
  <ResourceManager '1.0.0' at 'http://images.projekt01.com'>

  >>> rm.getURI(rName)
  'http://images.projekt01.com/test.gif'

Now, register our resource whcih is normal done with the p01:cdnResource
directive:

  >>> import zope.interface
  >>> zope.component.provideAdapter(resourceFactory, (TestRequest,),
  ...     zope.interface.Interface, 'test.gif')

and test with the zope traversal concept:

  >>> img = resources.publishTraverse(request, 'test.gif')
  >>> img
  <CDNResource 'test.gif'>

Calling a resrouce will return the URL:

  >>> img()
  'http://images.projekt01.com/test.gif'

As you can see, the resource url above doesn't provide '@@' as a resources
lookup hook which is fine because we don't need to deliver the resource from
the application server. This also means you have to make sure that the above
url provides this resource.

You can also see, that the version doesn't get used. Read below how to enable
such a resource manager version in your uri.

Note: we provide a p01.recipe.cdn which is able to extract all resources and
stores them in a folder. This folder can get used for easy deploy the resources
to such a content delivery network server.


namespace and version
---------------------

Normaly you will need more the just a simple url for build a simple rewrite
rule pattern. The p01.cdn resource manager uri pattern provides 2 different
concepts called namespace and version. We can simply enable the version by
useing the following url string pattern:

  >>> manager.uri = 'http://images.projekt01.com/%(version)s'

since the resource manager provides the following version, which will get
injected using the ``%(version)s`` variable:

  >>> manager.version
  '1.0.0'

we will get the following resource uri:

  >>> img = resources.publishTraverse(request, 'test.gif')
  >>> img()
  'http://images.projekt01.com/1.0.0/test.gif'


we can also include a ``%(namespace)s`` in our resource manager uri pattern:

  >>> manager.uri = 'http://images.projekt01.com/%(namespace)s/%(version)s'

This will produce the following resource uri:

  >>> img = resources.publishTraverse(request, 'test.gif')
  >>> img()
  'http://images.projekt01.com/missing-namespace/1.0.0/test.gif'

As you see, our manager doesn't define a namespace and this will end with
using ``missing-resource-manager-namespace`` as a marker for the missing
namespace value. Let's define a namespace:

  >>> manager.namespace = 'mysite'

and you will get the following resource uri:

  >>> img = resources.publishTraverse(request, 'test.gif')
  >>> img()
  'http://images.projekt01.com/mysite/1.0.0/test.gif'


CDN Resource
------------

The CDN resource directive allows to register resources with a predefined base
url. Such a resource will provide the base url if we ask for an absolute url.
This allows us to off load image, CSS, JS resource files from a zope server by
using a different domain for such resources.


CDN Directory
-------------

The CDN directory is a resource directory which contains child resources.
Use this directive as <p01:cdnDirectory>.

The directive <p01:cdnDirectory> will map all subfolders as child resources too
and will map each subfolder explicit to the given base url.


CDN i18n Resource
-----------------

The CDN i18n resource is a resource container which registers it's item as i18n
resources. If you use this directive as <p01:cdnI18nResource>, the contained
items get registered as i18n resources. The items in such a i18n resource
containermust provide locales names like de.gif, en.gif etc. Such names get
mapped to urls like: foo-de.gif, foo-fr.gif if the resouce name is called foo.


Deployment
----------

You always have to think about the deploment if you use a cdn resource concept.
Independent if you use the p01.cdn concept or any other concept. You have to make
sure that you understand when you need to extract your resources and where to install. I recommend to plan your release stack before you use any content
delivery network (cdn) concept. You have at least to answer the following
questions:

- When do I need to extract the resoruces from the application for deployment

- Where do I extract the resources

- How do I keep the application release and deployment in sync with the
  resource release and deployment.

Just a hint, both p01.cdn concepts allow to deploy new resources without
to affect the current deployed application and later deploy the application.
