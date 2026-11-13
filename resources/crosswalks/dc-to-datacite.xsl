<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:d="http://datacite.org/schema/kernel-4" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" version="3.0" exclude-result-prefixes="d dc oai_dc">
  <!-- Explicit profile: identifier is a DOI, date is YYYY, type is a DataCite enum. -->
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <xsl:if test="count(oai_dc:dc/dc:identifier) != 1 or count(oai_dc:dc/dc:publisher) != 1 or count(oai_dc:dc/dc:date) != 1 or count(oai_dc:dc/dc:type) != 1 or not(starts-with(oai_dc:dc/dc:identifier, '10.')) or not(matches(oai_dc:dc/dc:date, '^\d{4}$'))">
      <xsl:message terminate="yes">Supply exactly one DOI identifier, publisher, YYYY date, and DataCite resource type.</xsl:message>
    </xsl:if>
    <resource xmlns="http://datacite.org/schema/kernel-4">
      <identifier identifierType="DOI">
        <xsl:value-of select="oai_dc:dc/dc:identifier"/>
      </identifier>
      <creators>
        <xsl:for-each select="oai_dc:dc/dc:creator">
          <creator>
            <creatorName>
              <xsl:value-of select="."/>
            </creatorName>
          </creator>
        </xsl:for-each>
      </creators>
      <titles>
        <xsl:for-each select="oai_dc:dc/dc:title">
          <title>
            <xsl:copy-of select="@xml:lang"/>
            <xsl:value-of select="."/>
          </title>
        </xsl:for-each>
      </titles>
      <publisher>
        <xsl:value-of select="oai_dc:dc/dc:publisher"/>
      </publisher>
      <publicationYear>
        <xsl:value-of select="oai_dc:dc/dc:date"/>
      </publicationYear>
      <resourceType resourceTypeGeneral="{oai_dc:dc/dc:type}">
        <xsl:value-of select="oai_dc:dc/dc:type"/>
      </resourceType>
    </resource>
  </xsl:template>
</xsl:stylesheet>
