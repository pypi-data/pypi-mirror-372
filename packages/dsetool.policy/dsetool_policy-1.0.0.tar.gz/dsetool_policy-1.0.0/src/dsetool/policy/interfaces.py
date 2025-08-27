from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IProductLayer


class IDSEToolPolicyLayer(IProductLayer):
    """Marker interface that defines a browser layer."""


class IDSEToolPolicyClientLayer(IOSHAClientSkinLayer):
    """Marker interface for the DSETool Policy client skin layer.

    This layer is used to mark requests that are related to the DSETool Policy
    client.

    The layer is applied by the traversing adapter.
    """
