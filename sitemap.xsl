<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <xsl:template match="/">
    <html>
      <head>
        <title>Sitemap</title>
        <style>
          body { font-family: Arial, sans-serif; }
          table { border-collapse: collapse; width: 80%; margin: 20px auto; }
          th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
          th { background-color: #f0f0f0; }
        </style>
      </head>
      <body>
        <h1 style="text-align:center;">Sitemap</h1>
        <table>
          <tr>
            <th>URL</th>
            <th>Last Modified</th>
          </tr>
          <xsl:for-each select="urlset/url">
            <tr>
              <td><xsl:value-of select="loc"/></td>
              <td><xsl:value-of select="lastmod"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
