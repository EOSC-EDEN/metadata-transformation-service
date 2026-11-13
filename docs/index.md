# Metadata Transformation Service

The Metadata Transformation Service (MTS) is an extensible service that transforms metadata between different metadata schemas, schema versions, and serialization formats, supporting interoperability between research repositories, preservation services, and other research data infrastructure. It is developed as part of EOSC EDEN and supports Core Preservation Process CPP-016, Metadata Transformation.

MTS does the following:

- Transforms metadata between different schemas using metadata crosswalks.
- Converts metadata between supported serialization formats, such as JSON and XML, independently of schema transformations.
- Validates metadata against the applicable schemas during transformation.
- Provides a REST API for submitting metadata transformations and discovering available schemas, crosswalks, and converters.
- Supports extensibility through additional metadata schemas, crosswalks, and converters.

## Scope

MTS focuses on **metadata transformation and validation**. It does not extract metadata from files, manage or curate metadata records, or provide persistent storage for transformed metadata.

The service currently uses locally managed schemas and crosswalks. Integration with external registries, such as the Metadata Schema and Crosswalk Registry (MSCR), is planned.

## Status

!!! warning "Work in progress"
    The [specification](specification.md) is a **draft**, open for review by EDEN technical working groups. The current implementation is a prototype and does not yet cover all requirements in the specification.

## Where to start

| You want to | Read |
|---|---|
| Try the service | [API examples](api-demos.md) |
| Run it | [Run with Docker Compose](https://github.com/EOSC-EDEN/metadata-transformation-service#run-with-docker-compose) |