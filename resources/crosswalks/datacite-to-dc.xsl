<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:d="http://datacite.org/schema/kernel-4" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" version="3.0" exclude-result-prefixes="d dc oai_dc">
  <!-- A deliberately small crosswalk. Catalog warnings document information loss. -->
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <oai_dc:dc>
      <xsl:for-each select="d:resource/d:identifier">
        <dc:identifier>
          <xsl:value-of select="."/>
        </dc:identifier>
      </xsl:for-each>
      <xsl:for-each select="d:resource/d:creators/d:creator/d:creatorName">
        <dc:creator>
          <xsl:value-of select="."/>
        </dc:creator>
      </xsl:for-each>
      <xsl:for-each select="d:resource/d:titles/d:title">
        <dc:title>
          <xsl:copy-of select="@xml:lang"/>
          <xsl:value-of select="."/>
        </dc:title>
      </xsl:for-each>
      <dc:publisher>
        <xsl:value-of select="d:resource/d:publisher"/>
      </dc:publisher>
      <dc:date>
        <xsl:value-of select="d:resource/d:publicationYear"/>
      </dc:date>
      <dc:type>
        <xsl:value-of select="d:resource/d:resourceType/@resourceTypeGeneral"/>
      </dc:type>
    </oai_dc:dc>
  </xsl:template>
</xsl:stylesheet>
