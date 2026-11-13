"""Execute trusted local XSLT with SaxonC, including XML-to-JSON stylesheets."""

from saxonche import PySaxonApiError, PySaxonProcessor

from ..exceptions import TransformationError
from ..xml import parse_xml

XSLT_NAMESPACE = "http://www.w3.org/1999/XSL/Transform"


class XsltEngine:
    """One processor per call avoids sharing mutable Saxon state across requests."""

    input_formats = frozenset({"xml", "json"})

    def accepts(self, path):
        """Infer XSLT from the document root, independent of filename extension."""
        root = parse_xml(path.read_text(encoding="utf-8"))
        return root.tag in {
            f"{{{XSLT_NAMESPACE}}}stylesheet",
            f"{{{XSLT_NAMESPACE}}}transform",
        }

    def transform(self, metadata, operation):
        """Return serialized output and messages emitted by xsl:message."""
        try:
            with PySaxonProcessor(license=False) as processor:
                executable = processor.new_xslt30_processor().compile_stylesheet(
                    stylesheet_file=str(operation.path)
                )
                executable.set_save_xsl_message(True)
                if operation.input_format == "json":
                    # The stylesheet parses JSON and chooses its representation.
                    executable.set_parameter(
                        "json-text", processor.make_string_value(metadata)
                    )
                    result = executable.call_template_returning_string("main")
                else:
                    # Saxon receives safely parsed XML without a DTD.
                    from lxml import etree

                    safe_xml = etree.tostring(parse_xml(metadata), encoding="unicode")
                    document = processor.parse_xml(xml_text=safe_xml)
                    result = executable.transform_to_string(xdm_node=document)
                messages = executable.get_xsl_messages()
                return result, [str(messages)] if messages is not None else []
        except (PySaxonApiError, TransformationError) as exc:
            raise TransformationError(
                "execution_failed", str(exc), stage="transformation"
            ) from exc
