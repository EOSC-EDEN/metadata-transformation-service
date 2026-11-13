# Schema provenance

Downloaded on 2026-10-26:

* DataCite 4.1: https://schema.datacite.org/meta/kernel-4.1/metadata.xsd
  and its referenced `include/` XSDs. Original comments and notices are retained.
* XML namespace schema: https://www.w3.org/2009/01/xml.xsd
* OAI-DC wrapper: https://www.openarchives.org/OAI/2.0/oai_dc.xsd

Import/include locations have been rewritten to local filenames for offline use.
`simpledc.xsd` is a project-authored Simple Dublin Core schema implementing the
15 literal elements with optional xml:lang; it is not a downloaded DCMI schema.
The OAI wrapper imports that local schema. The upstream DCMI schema endpoint was
unavailable during creation. This local schema does not support arbitrary
xsi:type extensions or qualified Dublin Core profiles.

`datacite-minimal.json` is a project-authored JSON Schema for the documented
minimal example, based on the structure (not copied content) of:
https://github.com/inveniosoftware/datacite/blob/master/tests/data/datacite-v4.1-full-example.json

The generated example records are new synthetic records. They are not copies of
the full upstream example. The JSON profile is intentionally narrower than the
upstream representation. Extend its schema and stylesheet together.

`dublincore.json` is a project-authored flat Simple Dublin Core JSON schema.
All fifteen terms accept a string or a nonempty array of strings. Output uses a
scalar for one value and an array for repeated values. Missing terms are omitted;
unknown keys and nested literal objects are rejected. Per-value language tags
are dropped with a warning; `language` remains an independent resource property.
This is a chosen representation, not an official DCMI JSON encoding or JSON-LD.
