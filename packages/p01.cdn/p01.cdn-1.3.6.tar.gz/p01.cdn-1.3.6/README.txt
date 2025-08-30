This package provides a meta directive which allows to register resources
like images, javascripts or other static content like falsh movies etc. for 
Zope3. The main usecase of this package is that we can define a sub domain.
This sub domain get used if we call the absolute url of such a resource.
This allows to offload the resouce calls from the zope server and it's 
front end proxy. In short words, this package offers a content delivery network
setup for Zope3.
