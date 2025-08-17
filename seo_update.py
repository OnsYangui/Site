import os
import json
import re
import google.generativeai as genai
from bs4 import BeautifulSoup

# 1️⃣ Configuration API Gemini
API_KEY = "AIzaSyC-53uJdF2CKMaFhdh-xQjryJXcV1fGx4A" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# 2️⃣ Extraction d'infos SEO
def extract_page_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and "content" in meta_desc_tag.attrs else ""
    headings = " ".join([h.get_text(" ", strip=True) for h in soup.find_all(re.compile("^h[1-6]$"))])
    paragraphs = " ".join([p.get_text(" ", strip=True) for p in soup.find_all("p")])
    img_alts = " ".join([img.get("alt", "") for img in soup.find_all("img")])

    full_text = f"{title} {meta_desc} {headings} {paragraphs} {img_alts}"
    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "text": full_text[:4000],
        "images_alt": img_alts
    }

# 3️⃣ Construire un prompt global
def build_global_prompt(pages_info):
    prompt = (
        "Tu es un expert SEO. Analyse l'ensemble du contenu des pages suivantes et retourne un JSON unique "
        "de la forme {\"tags\": [\"mot1\", \"mot2\", ...]} avec la liste globale de tous les tags SEO pertinents.\n\n"
    )
    for filename, info in pages_info.items():
        prompt += f"Page: {filename}\n"
        prompt += f"Titre : {info['title']}\n"
        prompt += f"Meta description : {info['meta_description']}\n"
        prompt += f"Headings : {info['headings']}\n"
        prompt += f"Texte : {info['text']}\n"
        prompt += f"Images ALT : {info['images_alt']}\n\n"
    return prompt

# 4️⃣ Récupérer les tags
def get_tags_from_llm(prompt):
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    return match.group(0) if match else "{}"

# 5️⃣ Mise à jour HTML
def update_html_with_tags(html_content, tags_list, new_description):
    soup = BeautifulSoup(html_content, "html.parser")

    # Title : si vide → générer un nouveau
    if not soup.title:
        new_title = soup.new_tag("title")
        new_title.string = tags_list[0] if tags_list else "Site Optimisé SEO"
        soup.head.append(new_title)

    # Meta keywords
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if not meta_keywords:
        meta_keywords = soup.new_tag("meta", attrs={"name": "keywords"})
        soup.head.append(meta_keywords)
    meta_keywords["content"] = ", ".join(tags_list)

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if not meta_desc:
        meta_desc = soup.new_tag("meta", attrs={"name": "description"})
        soup.head.append(meta_desc)
    meta_desc["content"] = new_description

    return str(soup)

# 6️⃣ Script principal
def main():
    pages_info = {}

    for filename in os.listdir("."):
        if filename.endswith(".html") and filename != "404.html":
            with open(filename, "r", encoding="utf-8") as f:
                html_content = f.read()
            pages_info[filename] = extract_page_info(html_content)

    prompt_global = build_global_prompt(pages_info)
    llm_result = get_tags_from_llm(prompt_global)

    try:
        tags_json = json.loads(llm_result)
        global_tags = tags_json.get("tags", [])
    except json.JSONDecodeError as e:
        print("⚠ Erreur JSON :", e)
        return

    print("\n📌 Tags globaux SEO générés :")
    for i, tag in enumerate(global_tags, 1):
        print(f"{i}. {tag}")

    for filename, info in pages_info.items():
        new_description = info["meta_description"] or info["text"][:160]
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        updated_html = update_html_with_tags(html_content, global_tags, new_description)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print(f"✅ {filename} mis à jour avec {len(global_tags)} tags.")

if __name__ == "__main__":
    main()