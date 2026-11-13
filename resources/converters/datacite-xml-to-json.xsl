<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:d="http://datacite.org/schema/kernel-4" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" version="3.0" exclude-result-prefixes="d dc oai_dc">
  <!-- A minimal Invenio-shaped DataCite JSON representation, not the full schema. -->
  <xsl:output method="json" indent="yes"/>
  <xsl:template match="/">
    <xsl:variable name="r" select="d:resource"/>
    <!-- Reject unsupported content rather than claiming lossless conversion. -->
    <xsl:if test="$r/*[not(self::d:identifier or self::d:creators or self::d:titles or self::d:publisher or self::d:publicationYear or self::d:resourceType)] or $r/d:creators/d:creator/*[not(self::d:creatorName)] or $r//@*[not(. is $r/d:identifier/@identifierType or . is $r/d:resourceType/@resourceTypeGeneral or (local-name()='lang' and namespace-uri()='http://www.w3.org/XML/1998/namespace' and parent::d:title) or namespace-uri()='http://www.w3.org/2001/XMLSchema-instance')]">
      <xsl:message terminate="yes">This JSON example supports only the documented minimal DataCite fields and attributes.</xsl:message>
    </xsl:if>
    <xsl:sequence select="map {   'identifier': map {'identifier': string($r/d:identifier), 'identifierType': string($r/d:identifier/@identifierType)},   'creators': array { $r/d:creators/d:creator ! map {'creatorName': string(d:creatorName)} },   'titles': array { $r/d:titles/d:title ! (if (@xml:lang) then map {'title': string(.), 'lang': string(@xml:lang)} else map {'title': string(.)}) },   'publisher': string($r/d:publisher),   'publicationYear': string($r/d:publicationYear),   'resourceType': map {'resourceType': string($r/d:resourceType), 'resourceTypeGeneral': string($r/d:resourceType/@resourceTypeGeneral)}  }"/>
  </xsl:template>
</xsl:stylesheet>
