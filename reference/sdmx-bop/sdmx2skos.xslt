<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                xmlns:owl="http://www.w3.org/2002/07/owl#"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
                xmlns:dct="http://purl.org/dc/terms/"
                xmlns:skos="http://www.w3.org/2004/02/skos/core#"
                xmlns:xkos="http://rdf-vocabulary.ddialliance.org/xkos#"
                xmlns:cl_area="http://gss-data.org.uk/def/concept-scheme/sdmx-bop/cl_area/"
                xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
                xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
                xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
>
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/mes:Structure/mes:Structures/str:Codelists/str:Codelist[@id='CL_AREA']">
    <rdf:RDF xml:base="http://gss-data.org.uk/def/concept-scheme/sdmx-bop/cl_area">
      <skos:ConceptScheme about="">
        <rdfs:label xml:lang="{com:Name/@xml:lang}"><xsl:value-of select="com:Name"/></rdfs:label>
      </skos:ConceptScheme>
      <xsl:apply-templates select="str:Code" mode="gen"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="str:Code" mode="gen">
    <skos:Concept rdf:about="cl_area/{@id}">
      <rdfs:label xml:lang="{com:Name/@xml:lang}"><xsl:value-of select="com:Name"/></rdfs:label>
      <xsl:if test="com:Description != ''">
        <rdfs:comment xml:lang="{com:Description/@xml:lang}"><xsl:value-of select="com:Description"/></rdfs:comment>
      </xsl:if>
      <skos:inScheme rdf:resource=""/>
      <skos:notation><xsl:value-of select="@id"/></skos:notation>
      <skos:topConceptOf rdf:resource=""/>
    </skos:Concept>
  </xsl:template>

  <xsl:template match="text()|@*"></xsl:template>

</xsl:stylesheet>
