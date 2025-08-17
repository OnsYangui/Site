import os, json, re, google.generativeai as genai
from bs4 import BeautifulSoup

# 1️⃣ Configuration API Gemini
API_KEY = "AIzaSyDthyIdxlZDZIahx2Mx4j5e8jSAZcWrK5Q"  # <-- Mets ta clé API ici
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# 2️⃣ Extraction d'infos importantes de la page HTML
def extract_page_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    title = (soup.title.string or "").strip() if soup.title else ""
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and "content" in meta_desc_tag.attrs else ""
    headings = " ".join([h.get_text(separator=" ", strip=True) for h in soup.find_all(re.compile("^h[1-6]$"))])
    paragraphs = " ".join([p.get_text(separator=" ", strip=True) for p in soup.find_all("p")])
    img_alts = " ".join([img.get("alt", "") for img in soup.find_all("img")])

    full_text = f"{title} {meta_desc} {headings} {paragraphs} {img_alts}"
    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "text": full_text[:4000],  # Limite à 4000 caractères
        "images_alt": img_alts
    }

# 3️⃣ Prompt SEO pour le LLM
def build_prompt(page_info):
    return f"""
Tu es un expert SEO. Analyse ce contenu et retourne uniquement un JSON de la forme :
{{"tags":["mot1","mot2","mot3",...]}}
Ne mets aucune explication en dehors du JSON.

Titre : {page_info['title']}
Meta description : {page_info['meta_description']}
Headings : {page_info['headings']}
Texte : {page_info['text']}
Images ALT : {page_info['images_alt']}
"""

# 4️⃣ Appel au LLM avec extraction du vrai JSON
def get_tags_from_llm(prompt):
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Extraire uniquement le JSON avec regex
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return match.group(0)
    else:
        print("⚠ Aucun JSON trouvé, réponse brute :", raw_text)
        return "{}"

# 5️⃣ Mise à jour du HTML avec les meta tags
def update_html_with_tags(html_content, tags_list, new_description):
    soup = BeautifulSoup(html_content, "html.parser")

    # Meta keywords
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if not meta_keywords:
        meta_keywords = soup.new_tag("meta")
        meta_keywords.attrs["name"] = "keywords"
        soup.head.append(meta_keywords)
    meta_keywords.attrs["content"] = ", ".join(tags_list)

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if not meta_desc:
        meta_desc = soup.new_tag("meta")
        meta_desc.attrs["name"] = "description"
        soup.head.append(meta_desc)
    meta_desc.attrs["content"] = new_description

    return str(soup)

# 6️⃣ Script principal
def main():
    for filename in os.listdir("."):
        if filename.endswith(".html") and filename not in ["404.html"]:
            print(f"📄 Traitement de {filename} ...")

            with open(filename, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Extraction infos
            page_info = extract_page_info(html_content)
            prompt = build_prompt(page_info)

            # Récupération tags depuis LLM
            llm_result = get_tags_from_llm(prompt)

            try:
                tags_json = json.loads(llm_result)
                tags_list = tags_json.get("tags", [])
            except json.JSONDecodeError as e:
                print(f"⚠ Erreur parsing JSON pour {filename} : {e}")
                continue

            # Affichage de tous les tags générés
            print(f"🔹 Tags générés pour {filename} :")
            for i, tag in enumerate(tags_list, start=1):
                print(f"   {i}. {tag}")

            # Si pas de meta description, on prend le début du texte
            new_description = page_info["meta_description"] or page_info["text"][:160]

            # Mise à jour HTML
            updated_html = update_html_with_tags(html_content, tags_list, new_description)

            # Sauvegarde fichier
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_html)

            print(f"✅ {filename} mis à jour avec {len(tags_list)} tags.\n")

if __name__ == "__main__":
    main()