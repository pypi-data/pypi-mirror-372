from dsetool.policy.interfaces import IDSEToolPolicyClientLayer
from dsetool.policy.interfaces import IDSEToolPolicyLayer
from euphorie.client.client import IClient
from zope.component import adapter
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse


@adapter(IClient, IDSEToolPolicyLayer)
@implementer(IPublishTraverse)
class ClientPublishTraverser(DefaultPublishTraverse):
    """Publish traverser to setup the skin layer.

    This traverser marks the request with IOSHAClientSkinLayer when the
    client is traversed and the osha.oira product is installed.
    """

    def publishTraverse(self, request, name):
        from euphorie.client.utils import setRequest

        setRequest(request)
        request.client = self.context

        ifaces = [
            iface
            for iface in directlyProvidedBy(request)
            if not IBrowserSkinType.providedBy(iface)
        ]
        directlyProvides(request, IDSEToolPolicyClientLayer, ifaces)
        return super().publishTraverse(request, name)
