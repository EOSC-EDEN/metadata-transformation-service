# Metadata Transformation Service specification

## Abstract

This specification defines the functional and technical requirements for the Metadata Transformation Service within the EOSC EDEN ecosystem. The Metadata Transformation Service provides a standardized mechanism for transforming metadata between supported metadata schemas, schema versions, and serialization formats. It enables interoperability by applying managed metadata crosswalks to map metadata elements between source and target schemas, and, where requested, by converting metadata between supported serialization formats (e.g., XML, JSON, JSON-LD, CSV).

The service supports the complete metadata transformation workflow, including the submission and validation of metadata,  execution of appropriate metadata crosswalks, optional serialization format conversion, validation of the transformed metadata against the target schema, and the return of the transformed metadata together with transformation status and diagnostic information. By separating metadata transformation from metadata schema and crosswalk management, the service provides a reusable, implementation-independent capability that enables consistent and interoperable metadata exchange across the EOSC EDEN ecosystem and beyond.

## Status of This Document

This document is a proposed specification for EOSC EDEN. It is currently open for review by the public.

## Rationale

The Metadata Transformation Service addresses interoperability challenges resulting from differences in metadata schemas, vocabularies, data representations, and formatting standards used by repositories, research infrastructures, archives, and other information systems. 

Rather than requiring every application to implement its own metadata mappings, the service provides a centralized capability for executing metadata crosswalks. This allows metadata to be transformed consistently between supported standards, reducing duplication of effort, simplifying system integration, and improving the quality and consistency of exchanged metadata.

For end users, the service enables metadata created in one system to be reused by other systems without requiring manual reformatting or schema-specific knowledge. This facilitates data sharing, repository interoperability, metadata aggregation, preservation workflows, and discovery services.

## Introduction

Research data ecosystems rely on a wide range of metadata standards, community profiles, repository-specific schemas, and serialization formats. Although these standards often describe similar information, differences in structure, terminology, controlled vocabularies, and representation frequently prevent metadata from being exchanged directly between systems. As a result, repositories, preservation systems, discovery services, and research infrastructures must implement numerous custom metadata mappings, leading to duplicated effort, inconsistent transformations, and reduced interoperability.

The Metadata Transformation Service (MTS) addresses this challenge by providing a standardized service for transforming metadata between supported metadata schemas, schema versions, and serialization formats, through the execution of managed metadata crosswalks and serialization transformation. Rather than embedding transformation logic within individual applications, the MTS provides a reusable capability that can be invoked by other EOSC EDEN services, external repositories, individual users, and preservation platforms, through a common REST API or a web-based user interface.

By separating crosswalk management from crosswalk execution, the architecture enables metadata mappings to be governed independently of transformation services while allowing implementations to operate either as standalone deployments using locally managed crosswalks or as federated services integrated with the EOSC ecosystem. 

## Scope

The Metadata Transformation Service is responsible for transforming metadata records between supported metadata schemas, standards, and system-specific representations, through the application of managed metadata crosswalks.

**In scope:**

The following capabilities are within the scope of this specification:

* Submission of metadata records to the service for transformation through supported interfaces, including a REST API and a web-based user interface.   
* Execution of metadata transformations using predefined metadata crosswalks between supported source and target schemas.  
* Validation of input metadata against the declared source schema prior to transformation.  
* Validation of transformed metadata against the target schema to ensure the transformation has produced valid output.  
* Support for metadata transformations between supported serialization formats (e.g., JSON, JSON-LD, XML, CSV, ), where applicable.  
* Support for value mappings, controlled vocabulary mappings, structural transformations, and metadata normalization, as defined by the selected crosswalk.  
* Publication of supported metadata schemas, serialization formats, and available metadata crosswalks, allowing clients to determine whether a requested transformation is supported.  
* Versioning of metadata crosswalks to support evolving metadata standards while maintaining compatibility with existing transformations.  
* A web interface that enables users to upload metadata, select source and target schemas, execute transformations, inspect transformation results, and download the transformed metadata.   
* A REST API protocol that provides an implementation-independent interface for interacting with the service. The API specification should enable client implementations to communicate with different instances of the Metadata Transformation Service without modification.


**Out of scope:**

- Transformation or modification of the underlying information content referenced by metadata.  
- Packaging, unpackaging, or restructuring of Submission Information Packages (SIPs), Archival Information Packages (AIPs), or other information packages.  
- Long-term storage, archival, or lifecycle management of metadata records or transformation results.  
- Definition, standardization, or ownership of metadata schemas, vocabularies, or community standards.  
- Manual creation, curation, or editing of metadata records.  
- Semantic reconciliation where no valid mapping exists between the source and target metadata schemas. 

## Conformance

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119 ([https://www.rfc-editor.org/rfc/rfc2119](https://www.rfc-editor.org/rfc/rfc2119)).

## Core-Preservation Processes

The Metadata Transformation Service primarily supports the **Metadata Ingest and Management (CPP-016)**[^1]  Core Preservation Process (CPP)[^2] by enabling metadata to be transformed between supported metadata schemas, representations, and formats through the execution of managed metadata crosswalks. The service facilitates the integration of metadata originating from different repositories and information systems into preservation workflows, by ensuring that metadata conforms to the requirements of the target metadata schema.

The service can complement metadata management and preservation workflows by allowing preservation systems and other EOSC EDEN services to consume metadata in a consistent and interoperable manner.

Metadata Transformation Service implementations may support one or more of the following Core Preservation Processes:

* **Metadata Ingest and Management (CPP-016)** through the validation, transformation, normalization, and management of metadata during ingest and interoperability workflows.  
* **Data Quality Assessment (CPP-019[^3])** by validating metadata against supported schemas and reporting validation errors, inconsistencies, incomplete mappings, or transformation warnings.  
* **Enabling Discovery (CPP-024)** by transforming metadata into standardized schemas that improve interoperability, indexing, and discoverability across repositories and services.

## Normative Requirements

### Requirement Group 1 - Metadata Submission

* {{ MTS-REQ-1-01 }} \- The service MUST allow users to submit metadata for transformation using a REST API.  
* {{ MTS-REQ-1-02 }} \- The service SHOULD provide a web-based user interface for submitting metadata transformation requests.  
* {{ MTS-REQ-1-03 }} \- The service MUST support the submission of metadata in one or more supported serialization formats (e.g. JSON, JSON-LD, XML, CSV).  
* {{ MTS-REQ-1-04 }} \- The service MUST validate that submitted metadata conforms to one of the supported source metadata schemas before processing begins.  
* {{ MTS-REQ-1-05 }} \- The service MUST reject transformation requests where the submitted metadata cannot be parsed or does not conform to the declared source schema.  
* {{ MTS-REQ-1-06 }} \- The service SHOULD return validation errors in a machine-readable format.  
* {{ MTS-REQ-1-07 }} \- The service MUST define and enforce a maximum size for metadata submitted in a single transformation request. The maximum request size MUST be configurable by the service operator and SHOULD be published through the service documentation or API description.   
* {{ MTS-REQ-1-08 }} \- The service MUST reject metadata submissions that exceed the configured maximum request size and SHOULD return a machine-readable error indicating that the permitted size has been exceeded.

### Requirement Group 2 - Metadata Transformation

* {{ MTS-REQ-2-01 }} \- The service MUST transform metadata using a supported metadata crosswalk.  
* {{ MTS-REQ-2-02 }} \- The requester MUST be able to specify the target metadata schema.  
* {{ MTS-REQ-2-03 }} \- The requester SHOULD specify the source metadata schema.  
* {{ MTS-REQ-2-04 }} \- The service MUST validate that a supported crosswalk exists between the requested source and target schemas before starting the transformation.  
* {{ MTS-REQ-2-05 }} \- The service MUST return an error if no supported metadata crosswalk exists.  
* {{ MTS-REQ-2-06 }} \- The service MUST preserve metadata values unless explicitly modified by the selected crosswalk.  
* {{ MTS-REQ-2-07 }} \- The service MAY perform metadata normalization where this forms part of the selected crosswalk.  
* {{ MTS-REQ-2-08 }} \- The service MAY perform metadata enrichment where defined by the selected crosswalk.  
* {{ MTS-REQ-2-09 }} \- The service MUST validate the transformed metadata against the requested target schema before returning the result.  
* {{ MTS-REQ-2-10 }} \- The service SHOULD return warnings where metadata elements cannot be mapped completely.  
* {{ MTS-REQ-2-11 }} \- The service MUST support transformation between one or more metadata serialization formats.  
* {{ MTS-REQ-2-12 }} \- The requester MUST be able to specify the desired output serialization format.  
* {{ MTS-REQ-2-13 }} \- The requester MAY specify the input serialization format. If omitted, the service MAY attempt to determine the serialization format automatically.  
* {{ MTS-REQ-2-14 }} \- The service MUST distinguish between metadata schema transformation and metadata serialization transformation.  
* {{ MTS-REQ-2-15 }} \- The service MAY perform metadata serialization transformation without applying a metadata crosswalk when the source and target metadata schemas are identical.  
* {{ MTS-REQ-2-16 }} \- The service MUST preserve the semantic meaning and information content of metadata during serialization transformation.  
* {{ MTS-REQ-2-17 }} \- The service SHOULD support common metadata serialization formats including XML, CSV, JSON, and JSON-LD.  
* {{ MTS-REQ-2-19 }} \- The service MUST return an error when the requested serialization format is not supported or when conversion between the requested serialization formats cannot be performed.  
* {{ MTS-REQ-2-20 }} \- The service SHOULD indicate in the transformation report whether the request involved metadata schema transformation, metadata serialization transformation, or both.

### Requirement Group 3 - Crosswalk Management

* {{ MTS-REQ-3-01 }} \- The service MUST publish the metadata schemas it supports.  
* {{ MTS-REQ-3-02 }} \- The service MUST publish the metadata crosswalks it supports.  
* {{ MTS-REQ-3-03 }} \- The service MAY obtain metadata schemas and crosswalk definitions from the Metadata Schema and Crosswalk Registry (MSCR).   
* {{ MTS-REQ-3-04 }} \- The service MAY support locally managed metadata schemas and crosswalk definitions.   
* {{ MTS-REQ-3-05 }} \- The service SHOULD publish version information for supported metadata schemas and crosswalks.  
* {{ MTS-REQ-3-06 }} \- The service SHOULD expose the source of the selected crosswalk (e.g. local repository or MSCR) in transformation reports.   
* {{ MTS-REQ-3-07 }} \- The service SHOULD publish the supported serialization formats for each metadata schema.  
* {{ MTS-REQ-3-08 }} \- The service MAY support multiple versions of the same metadata crosswalk.

### Requirement Group 4 - Transformation Results

* {{ MTS-REQ-4-01 }} \- The service MUST return the transformed metadata in the requested serialization format.  
* {{ MTS-REQ-4-02 }} \- The service MUST indicate whether the transformation completed successfully, completed with warnings, or failed.  
* {{ MTS-REQ-4-03 }} \- The service SHOULD provide a transformation report describing the mappings applied during the transformation.  
* {{ MTS-REQ-4-04 }} \- The service SHOULD identify metadata elements that could not be transformed.  
* {{ MTS-REQ-4-05 }} \- The service MAY provide provenance information describing which metadata crosswalk and version were used.

### Requirement Group 5 - Service Interfaces

* {{ MTS-REQ-5-01 }} \- The service MUST expose its functionality through a REST API.  
* {{ MTS-REQ-5-02 }} \- The REST API MUST be documented using an OpenAPI specification.  
* {{ MTS-REQ-5-03 }} \- The service SHOULD support asynchronous processing for long-running transformation requests.  
* {{ MTS-REQ-5-04 }} \- For asynchronous processing, the service MUST return a job identifier that can be used to retrieve the transformation status.  
* {{ MTS-REQ-5-05 }} \- The service MAY support callback notifications (e.g. webhooks) upon completion of asynchronous transformations.  
* {{ MTS-REQ-5-06 }} \- The service MAY provide a web-based user interface.  
* {{ MTS-REQ-5-07 }} \- The web interface MUST allow users to upload or paste metadata for transformation.  
* {{ MTS-REQ-5-08 }} \- The web interface MUST allow users to select the source and target metadata schemas.  
* {{ MTS-REQ-5-09 }} \- The web interface SHOULD allow users to preview transformed metadata before downloading it.  
* {{ MTS-REQ-5-10 }} \- The web interface SHOULD display validation errors and transformation warnings in a human-readable form.  
* {{ MTS-REQ-11 }} \- The web interface MAY visualize the metadata crosswalk that was applied during the transformation.

### Requirement Group 6 - Security

* {{ MTS-REQ-7-01 } \- The service MAY permit anonymous transformation requests.   
* {{ MTS-REQ-7-02 }} \- The service SHOULD support authenticated transformation requests.  
* {{ MTS-REQ-7-03 }} \- Communication with the service MUST be encrypted using HTTPS/TLS.  
* {{ MTS-REQ-7-04 }} \- The service SHOULD support integration with the EOSC Federated AAI (e.g. OIDC, OAuth2, SAML2).  
* {{ MTS-REQ-7-05 }} \- The service SHOULD ensure that users can only access transformation jobs they have submitted.  
* {{ MTS-REQ-7-06 }} \- Implementations MAY apply different quotas, rate limits, or resource limits to anonymous and authenticated requests. 

### Requirement Group 7 - Deployment

* {{ MTS-REQ-8-01 }} \- The service MAY be deployed as a cloud-hosted service (e.g. SaaS) or as an on-premises deployment.  
* {{ MTS-REQ-8-02 }} \- The service SHOULD support containerized (local) deployment (e.g. Docker or Kubernetes).  
* {{ MTS-REQ-8-03 }} \- The service MUST publish the metadata schemas, serialization formats, and metadata crosswalks supported by the deployed instance.

## Non-normative Guidance

### Integration with the Metadata Schema and Crosswalk Registry (MSCR)[^4]

To avoid duplication of functionality and promote reuse, implementations are encouraged to make use of the EOSC Metadata Schema and Crosswalk Registry (MSCR).

The MSCR should act as the authoritative registry for metadata schemas, schema versions, and metadata crosswalk definitions, while the Metadata Transformation Service is responsible for executing those crosswalks.

The Metadata Transformation Service may obtain information from the MSCR, including:

* Metadata schemas  
* Metadata crosswalks  
* Version information for schemas and crosswalks  
* Supported source and target schema combinations

While implementations are encouraged to use the MSCR, they may also provide locally managed metadata schemas and crosswalk definitions.

## Traceability to EOSC EDEN Requirements

### INTEROPERABILITY-TECHNICAL-REQ-019

*The Trusted Digital Archive (TDA) must perform metadata crosswalks from external standards to its local metadata schema during package transformations. This ensures that descriptive, administrative, and preservation metadata retain their meaning and comply with local semantic rules.* Addressed by: MTS-REQ-2-01, MTS-REQ-2-02, MTS-REQ-2-04, MTS-REQ-2-06, MTS-REQ-2-09

### INTEROPERABILITY-TECHNICAL-REQ-037

*As a Consumer I want to query a registry of metadata schemas and crosswalks so that I can align my metadata with others across heterogeneous repositories and systems..* Addressed by: MTS-REQ-3-01, MTS-REQ-3-02, MTS-REQ-3-03, MTS-REQ-3-05, MTS-REQ-3-07

### INTEROPERABILITY-TECHNICAL-REQ-038

*As a Producer I want to publish data and research objects in my preferred format and have them automatically transformed into interoperable standards so that they can be preserved and shared.* Addressed by: MTS-REQ-1-03, MTS-REQ-2-01, MTS-REQ-2-02, MTS-REQ-2-09, MTS-REQ-2-11, MTS-REQ-2-12, MTS-REQ-4-01 

### INTEROPERABILITY-TECHNICAL-REQ-039

*As a Consumer I want to access transformation endpoints so that I can retrieve data in formats compatible with my tools and workflows.* Addressed by: MTS-REQ-1-01, MTS-REQ-2-02, MTS-REQ-2-11, MTS-REQ-2-12, MTS-REQ-4-01, MTS-REQ-5-01 

## References

[^1]: https://github.com/EOSC-EDEN/wp1-cpp-descriptions/blob/main/CPP-016/EOSC-EDEN_CPP-016_Metadata_Ingest_and_Management.pdf

[^2]: EOSC EDEN T1.2, Lindlar, M., Caron, B., Benauer, M., Kylander, J., Dekeyser, K., Addis, M., Levlin, M., Laukkanen, M., Lehtonen, J., Burger, F., Koho, T., Schwab, F., Molloy, L., & Zhang, F. (2025). EOSC EDEN M1.1 – Report on Identification of Core Preservation Processes. Zenodo. [https://doi.org/10.5281/zenodo.16992452](https://doi.org/10.5281/zenodo.16992452)

[^3]:  [https://github.com/EOSC-EDEN/wp1-cpp-descriptions/blob/main/CPP-010/EOSC-EDEN\_CPP-010\_File\_Format\_Validation.pdf](https://github.com/EOSC-EDEN/wp1-cpp-descriptions/blob/main/CPP-010/EOSC-EDEN_CPP-010_File_Format_Validation.pdf) 

[^4]:  [https://mscr-release.2.rahtiapp.fi/](https://mscr-release.2.rahtiapp.fi/)