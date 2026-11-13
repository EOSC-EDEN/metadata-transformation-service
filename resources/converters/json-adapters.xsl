<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:d="http://datacite.org/schema/kernel-4" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:map="http://www.w3.org/2005/xpath-functions/map" version="3.0" exclude-result-prefixes="#all">
  <!-- Representation helpers shared by demo crosswalks. Not a generic XML/JSON converter. -->
  <xsl:template name="from-json">
    <xsl:param name="data"/>
    <xsl:param name="schema"/>
    <xsl:choose>
      <xsl:when test="$schema='datacite-4.1'">
        <resource xmlns="http://datacite.org/schema/kernel-4">
          <identifier identifierType="{$data?identifier?identifierType}">
            <xsl:value-of select="$data?identifier?identifier"/>
          </identifier>
          <creators>
            <xsl:for-each select="$data?creators?*">
              <creator>
                <creatorName>
                  <xsl:value-of select="?creatorName"/>
                </creatorName>
              </creator>
            </xsl:for-each>
          </creators>
          <titles>
            <xsl:for-each select="$data?titles?*">
              <title>
                <xsl:if test="map:contains(., 'lang')">
                  <xsl:attribute name="xml:lang" select="?lang"/>
                </xsl:if>
                <xsl:value-of select="?title"/>
              </title>
            </xsl:for-each>
          </titles>
          <publisher>
            <xsl:value-of select="$data?publisher"/>
          </publisher>
          <publicationYear>
            <xsl:value-of select="$data?publicationYear"/>
          </publicationYear>
          <resourceType resourceTypeGeneral="{$data?resourceType?resourceTypeGeneral}">
            <xsl:value-of select="$data?resourceType?resourceType"/>
          </resourceType>
        </resource>
      </xsl:when>
      <xsl:when test="$schema='oai-dc'">
        <oai_dc:dc>
          <xsl:for-each select="sort(map:keys($data))">
            <xsl:variable name="field" select="."/>
            <xsl:for-each select="if ($data($field) instance of array(*)) then $data($field)?* else $data($field)">
              <xsl:element name="dc:{$field}" namespace="http://purl.org/dc/elements/1.1/">
                <xsl:value-of select="."/>
              </xsl:element>
            </xsl:for-each>
          </xsl:for-each>
        </oai_dc:dc>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message terminate="yes">No example JSON adapter for this schema. Supply your own stylesheet or adapter.</xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="to-json">
    <xsl:param name="document"/>
    <xsl:param name="schema"/>
    <xsl:choose>
      <xsl:when test="$schema='datacite-4.1'">
        <xsl:variable name="r" select="$document/d:resource"/>
        <xsl:sequence select="map {     'identifier': map {'identifier': string($r/d:identifier), 'identifierType': string($r/d:identifier/@identifierType)},     'creators': array { $r/d:creators/d:creator ! map {'creatorName': string(d:creatorName)} },     'titles': array { $r/d:titles/d:title ! (if (@xml:lang) then map {'title': string(.), 'lang': string(@xml:lang)} else map {'title': string(.)}) },     'publisher': string($r/d:publisher), 'publicationYear': string($r/d:publicationYear),     'resourceType': map {'resourceType': string($r/d:resourceType), 'resourceTypeGeneral': string($r/d:resourceType/@resourceTypeGeneral)}    }"/>
      </xsl:when>
      <xsl:when test="$schema='oai-dc'">
        <xsl:if test="$document/oai_dc:dc//@xml:lang">
          <xsl:message>Language annotations (xml:lang) were omitted from flat Dublin Core JSON; the resource language field was not inferred.</xsl:message>
        </xsl:if>
        <xsl:sequence select="map:merge(for $key in distinct-values($document/oai_dc:dc/*/local-name()) return&#10; map:entry($key, if (count($document/oai_dc:dc/*[local-name()=$key])=1)&#10; then string($document/oai_dc:dc/*[local-name()=$key])&#10; else array { $document/oai_dc:dc/*[local-name()=$key] ! string(.) }))"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message terminate="yes">No example JSON adapter for this schema. Supply your own stylesheet or adapter.</xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
