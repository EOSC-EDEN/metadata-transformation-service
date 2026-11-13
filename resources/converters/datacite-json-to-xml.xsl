<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.0">
  <xsl:include href="json-adapters.xsl"/>
  <xsl:output method="xml" indent="yes"/>
  <xsl:param name="json-text"/>
  <xsl:template name="main">
    <xsl:call-template name="from-json">
      <xsl:with-param name="data" select="parse-json($json-text)"/>
      <xsl:with-param name="schema" select="'datacite-4.1'"/>
    </xsl:call-template>
  </xsl:template>
</xsl:stylesheet>
