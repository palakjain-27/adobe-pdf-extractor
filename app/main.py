import os
import json
import pdfplumber

# Fixed paths - these should be absolute paths in the container
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def is_heading(text, font_size, font_name):
    # Heuristics to classify heading level
    if font_size >= 18:
        return "H1"
    elif font_size >= 14:
        return "H2"
    elif font_size >= 11:
        return "H3"
    return None

def extract_outline(pdf_path):
    outline = []
    title = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            for word in words:
                heading_level = is_heading(word["text"], word["size"], word["fontname"])
                if heading_level:
                    if not title and heading_level == "H1":
                        title = word["text"]
                    outline.append({
                        "level": heading_level,
                        "text": word["text"],
                        "page": page_num
                    })

    return {
        "title": title or "Untitled Document",
        "outline": outline
    }

def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Looking for PDFs in: {INPUT_DIR}")
    print(f"Files found: {os.listdir(INPUT_DIR) if os.path.exists(INPUT_DIR) else 'Directory not found'}")
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing: {pdf_path}")
            result = extract_outline(pdf_path)
            json_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Processed: {filename} → {json_path}")

if __name__ == "__main__":
    main()