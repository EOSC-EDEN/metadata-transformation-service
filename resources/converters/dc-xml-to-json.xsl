<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.0">
  <xsl:include href="json-adapters.xsl"/>
  <xsl:output method="json" indent="yes"/>
  <xsl:template match="/">
    <xsl:call-template name="to-json">
      <xsl:with-param name="document" select="."/>
      <xsl:with-param name="schema" select="'oai-dc'"/>
    </xsl:call-template>
  </xsl:template>
</xsl:stylesheet>
