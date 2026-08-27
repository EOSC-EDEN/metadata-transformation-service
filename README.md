# Metadata Transformation Service

The Metadata Transformation Service (MTS) is an EOSC EDEN specification for a service that transforms metadata between different metadata schemas, schema versions, and serialization formats.

The MTS provides a reusable interface for metadata transformation using managed metadata crosswalks. This supports interoperability between repository systems, preservation services, and other research data infrastructure.

> **Note**
>
> This repository contains a proposed specification, not a service implementation.

## Overview

The Metadata Transformation Service enables clients to submit metadata for transformation and specify the required source and target metadata representations.

Transformations may include:

* transformation between metadata schemas;
* transformation between different versions of a schema;
* transformation between serialization formats such as JSON and XML; and
* transformations using metadata crosswalks registered and managed by external services such as the Metadata Schema and Crosswalk Registry (MSCR).

The specification defines the service model and API independently of a particular MTS implementation.

## Documentation

* [Metadata Transformation Service specification](docs/specification.md)
* [Contributing guidelines](CONTRIBUTING.md)
* [License](LICENSE)

