import os
import json
import pdfplumber
import re
from collections import Counter

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def detect_language(text):
    """Simple language detection based on character patterns"""
    # Japanese patterns
    hiragana = re.compile(r'[\u3040-\u309f]')
    katakana = re.compile(r'[\u30a0-\u30ff]')
    kanji = re.compile(r'[\u4e00-\u9faf]')
    
    # Chinese patterns
    chinese = re.compile(r'[\u4e00-\u9fff]')
    
    # Korean patterns
    korean = re.compile(r'[\uac00-\ud7af]')
    
    # Arabic patterns
    arabic = re.compile(r'[\u0600-\u06ff]')
    
    # Count different script types
    total_chars = len(text.replace(' ', ''))
    if total_chars == 0:
        return 'en'
    
    japanese_count = len(hiragana.findall(text)) + len(katakana.findall(text)) + len(kanji.findall(text))
    korean_count = len(korean.findall(text))
    arabic_count = len(arabic.findall(text))
    chinese_count = len(chinese.findall(text))
    
    # Determine language based on script prevalence
    if japanese_count / total_chars > 0.1:
        return 'ja'
    elif korean_count / total_chars > 0.1:
        return 'ko'
    elif arabic_count / total_chars > 0.1:
        return 'ar'
    elif chinese_count / total_chars > 0.1:
        return 'zh'
    else:
        return 'en'

def is_heading_multilingual(text, font_size, font_name, avg_font_size, language='en'):
    """Enhanced heading detection for multiple languages"""
    
    # Base font size thresholds
    base_thresholds = {
        'H1': 1.5,  # 50% larger than average
        'H2': 1.3,  # 30% larger than average
        'H3': 1.15  # 15% larger than average
    }
    
    # Language-specific adjustments
    if language == 'ja':  # Japanese
        # Japanese text might have different font sizing patterns
        base_thresholds = {
            'H1': 1.4,
            'H2': 1.25,
            'H3': 1.1
        }
    elif language in ['zh', 'ko']:  # Chinese, Korean
        base_thresholds = {
            'H1': 1.4,
            'H2': 1.25,
            'H3': 1.1
        }
    elif language == 'ar':  # Arabic
        base_thresholds = {
            'H1': 1.6,
            'H2': 1.35,
            'H3': 1.2
        }
    
    # Check if font size indicates heading
    if font_size >= avg_font_size * base_thresholds['H1']:
        return "H1"
    elif font_size >= avg_font_size * base_thresholds['H2']:
        return "H2"
    elif font_size >= avg_font_size * base_thresholds['H3']:
        return "H3"
    
    # Additional heuristics for different languages
    if language == 'ja':
        # Japanese headings might be shorter and use specific patterns
        if len(text.strip()) <= 20 and font_size >= avg_font_size * 1.1:
            return "H3"
    
    # Check for common heading patterns (language agnostic)
    heading_patterns = [
        r'^\d+\.?\s*',  # Numbered headings: "1. " or "1 "
        r'^[A-Z\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,}$',  # All caps or CJK
        r'^Chapter\s+\d+',  # Chapter headings
        r'^第\d+章',  # Japanese chapter pattern
        r'^第\d+节',  # Chinese section pattern
    ]
    
    for pattern in heading_patterns:
        if re.match(pattern, text.strip()):
            if font_size >= avg_font_size * 1.1:
                return "H3"
    
    return None

def group_consecutive_words(words, max_gap=5):
    """Group consecutive words that might form a heading"""
    if not words:
        return []
    
    groups = []
    current_group = [words[0]]
    
    for i in range(1, len(words)):
        # Check if words are close enough to be part of same heading
        prev_word = current_group[-1]
        curr_word = words[i]
        
        # Simple proximity check (you can enhance this)
        x_gap = abs(curr_word.get('x0', 0) - prev_word.get('x1', 0))
        y_gap = abs(curr_word.get('top', 0) - prev_word.get('top', 0))
        
        if x_gap <= max_gap and y_gap <= 2:  # Same line, close proximity
            current_group.append(curr_word)
        else:
            if current_group:
                groups.append(current_group)
            current_group = [curr_word]
    
    if current_group:
        groups.append(current_group)
    
    return groups

def extract_outline(pdf_path):
    outline = []
    title = None
    all_font_sizes = []
    
    # First pass: collect all font sizes to calculate average
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=["size", "fontname"])
            for word in words:
                if word.get("size"):
                    all_font_sizes.append(word["size"])
    
    # Calculate average font size
    avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12
    
    # Second pass: extract headings with multilingual support
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["size", "fontname", "x0", "x1", "top", "bottom"])
            
            # Group consecutive words that might form headings
            word_groups = group_consecutive_words(words)
            
            for group in word_groups:
                if not group:
                    continue
                
                # Combine words in group
                combined_text = " ".join([word["text"] for word in group])
                combined_size = max([word.get("size", 0) for word in group])
                combined_font = group[0].get("fontname", "")
                
                # Skip very short or very long texts
                if len(combined_text.strip()) < 2 or len(combined_text.strip()) > 200:
                    continue
                
                # Detect language
                language = detect_language(combined_text)
                
                # Check if it's a heading
                heading_level = is_heading_multilingual(
                    combined_text, 
                    combined_size, 
                    combined_font, 
                    avg_font_size, 
                    language
                )
                
                if heading_level:
                    # Use first H1 as title if not set
                    if not title and heading_level == "H1":
                        title = combined_text.strip()
                    
                    outline.append({
                        "level": heading_level,
                        "text": combined_text.strip(),
                        "page": page_num,
                        "language": language,  # Optional: include detected language
                        "font_size": combined_size
                    })

    return {
        "title": title or "Untitled Document",
        "outline": outline,
        "metadata": {
            "avg_font_size": round(avg_font_size, 2),
            "total_pages": len(pdf.pages) if 'pdf' in locals() else 0
        }
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Looking for PDFs in: {INPUT_DIR}")
    
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input directory not found: {INPUT_DIR}")
        return
    
    files = os.listdir(INPUT_DIR)
    pdf_files = [f for f in files if f.endswith(".pdf")]
    
    print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
    
    for filename in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, filename)
        print(f"Processing: {filename}")
        
        try:
            result = extract_outline(pdf_path)
            json_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Processed: {filename} → {os.path.basename(json_path)}")
            print(f"   Found {len(result['outline'])} headings")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()