from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom
import os
from datetime import datetime

def generate_sitemap(domain):
    domain = domain.rstrip("/")
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for filename in os.listdir("."):
        if filename.endswith(".html") and filename != "404.html":
            url = SubElement(urlset, "url")
            loc = SubElement(url, "loc")
            loc.text = f"{domain}/{filename}"

            # Ajout de la date de dernière modification
            lastmod = SubElement(url, "lastmod")
            lastmod.text = datetime.now().strftime("%Y-%m-%d")

    rough_string = tostring(urlset, encoding="utf-8", method="xml")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="UTF-8")

    with open("sitemap.xml", "wb") as f:  # b = binaire car UTF-8
        f.write(pretty_xml)

    print("✅ sitemap.xml généré correctement (UTF-8 + lastmod).")

# Exemple
generate_sitemap("https://fancy-pastelito-b9c812.netlify.app")