"""Safe XML parsing shared by validation and the XSLT engine."""

from lxml import etree

from .exceptions import TransformationError


def parse_xml(text: str):
    """Parse without fetching resources; DTDs and entities are not accepted."""
    try:
        parser = etree.XMLParser(
            resolve_entities=False, load_dtd=False, no_network=True
        )
        root = etree.fromstring(text.encode("utf-8"), parser)
        if root.getroottree().docinfo.doctype:
            raise ValueError("DTD declarations are not supported")
        return root
    except (etree.XMLSyntaxError, ValueError) as exc:
        raise TransformationError("invalid_xml", str(exc)) from exc
