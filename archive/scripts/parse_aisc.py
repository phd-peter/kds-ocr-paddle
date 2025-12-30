import re
import json
import os

def normalize(text):
    """Normalize text for matching: lower case, strip formatting, single spaces."""
    # Remove markdown headers
    text = re.sub(r'^#+\s*', '', text)
    # Remove source comments
    text = re.sub(r'<!--.*?-->', '', text)
    # Lower case and strip
    text = text.lower().strip()
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    # Normalize IDs like "1 a." -> "1a."
    text = re.sub(r'^(\d+)\s+([a-z]\.)', r'\1\2', text)
    # Remove trailing dots used in TOC
    text = text.rstrip('. ')
    return text

def parse_outline(outline_path):
    sections = []
    current_chapter = None
    
    with open(outline_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Match "ID. Title ..... Page"
            match = re.match(r"^(.*?)\s*\.{5,}\s*(\w+)\s*$", line)
            if not match:
                match = re.match(r"^(.*?)$", line)
            
            full_title = match.group(1).strip()
            
            # Pattern: (ID) (Title)
            # ID can be "APPENDIX 1.", "A.", "A1.", "1.1.", "1.", "1a."
            id_match = re.match(r"^(APPENDIX\s+\d+\.|[A-Z]\.|[A-Z]\d+\.|\d+\.\d+\.|\d+[a-z]?\.)\s+(.*)$", full_title, re.IGNORECASE)
            if id_match:
                item_id = id_match.group(1).rstrip('.').strip()
                item_title = id_match.group(2).strip()
            else:
                item_id = None
                item_title = full_title
            
            # Determine Level
            if item_id and (re.match(r"^[A-Z]$", item_id) or "APPENDIX" in item_id.upper()):
                level = 1 # Chapter
                current_chapter = item_id
            elif item_id and (re.match(r"^[A-Z]\d+$", item_id) or re.match(r"^\d+\.\d+$", item_id)):
                level = 2 # Section
            elif item_id and re.match(r"^\d+[a-z]?$", item_id):
                level = 3 # Subsection
            else:
                level = 4 # Other or deeper
            
            sections.append({
                "id": item_id,
                "title": item_title,
                "level": level,
                "chapter": current_chapter,
                "norm_title": normalize(full_title)
            })
            
    return sections

def get_id_regex(id_str):
    """Create a regex that allows optional spaces between characters of the ID."""
    if not id_str:
        return ""
    # Allow spaces between any characters, especially around letters and numbers
    # e.g. "I1" -> "I\s*1", "1.1" -> "1\s*.\s*1"
    chars = [re.escape(c) for c in id_str]
    return r"\s*".join(chars)

def parse_main_content(content_path, outline, start_line=2561):
    parsed_data = []
    
    with open(content_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip front matter and TOC
    lines = lines[start_line-1:]
    
    current_node = None
    current_content = []
    
    outline_idx = 0
    lookahead_limit = 50
    
    for line in lines:
        raw_line = line.rstrip('\n')
        norm_line = normalize(raw_line)
        
        if not norm_line:
            if current_node:
                current_content.append(raw_line)
            continue
            
        is_header = raw_line.startswith('#')
        
        match_found = False
        
        for lookahead in range(min(lookahead_limit, len(outline) - outline_idx)):
            target = outline[outline_idx + lookahead]
            target_norm = target['norm_title']
            
            # Case 1: Level 1 (Chapter/Appendix)
            if target['level'] == 1:
                id_norm = normalize(target['id']) if target['id'] else ""
                if "APPENDIX" in target['id'].upper():
                    id_regex = get_id_regex(target['id'])
                    if re.match(rf"^#*\s*{id_regex}$", norm_line, re.I) or (id_norm in norm_line and normalize(target['title']) in norm_line):
                        match_found = True
                else:
                    id_regex = get_id_regex(target['id'])
                    chapter_pattern = rf"^chapter\s*{id_regex}\s*{re.escape(normalize(target['title']))}"
                    if re.search(chapter_pattern, norm_line, re.I):
                        match_found = True
                    # Also check for just "CHAPTER X" if it's a short header
                    elif re.match(rf"^chapter\s*{id_regex}$", norm_line, re.I):
                        match_found = True
            
            # Case 2: Headers (Level 2, 3)
            elif is_header:
                if target['id']:
                    id_regex = get_id_regex(target['id'])
                    # We use ^ to ensure it's at the start of the normalized line (after #)
                    # and \b to handle boundaries
                    if re.search(rf"^{id_regex}\b", norm_line, re.I):
                        # Strict check: if it's Level 3, ensure the title also matches roughly
                        if target['level'] == 2 or target_norm in norm_line:
                            match_found = True
                elif target_norm in norm_line:
                    match_found = True
            
            if match_found:
                # Save previous node
                if current_node:
                    current_node['content'] = "\n".join(current_content).strip()
                    parsed_data.append(current_node)
                
                # Start new node
                current_node = {
                    "id": target['id'],
                    "chapter": target['chapter'],
                    "title": target['title'],
                    "level": target['level'],
                    "content": ""
                }
                current_content = []
                outline_idx += lookahead + 1
                break
        
        if not match_found:
            if current_node:
                if not re.match(r'^\s*<!-- Source:.*?-->\s*$', raw_line):
                    # Skip duplicate title headers
                    if not (is_header and (normalize(raw_line) == normalize(current_node['title']) or normalize(raw_line) == normalize((current_node['id'] or "") + " " + current_node['title']))):
                        current_content.append(raw_line)

    # Final save
    if current_node:
        current_node['content'] = "\n".join(current_content).strip()
        parsed_data.append(current_node)
        
    return parsed_data

def main():
    outline_file = "C:\\Users\\Alpha\\Projects\\kds-ocr-paddle\\contents_outline.md"
    content_file = "C:\\Users\\Alpha\\Projects\\kds-ocr-paddle\\aisc360-22_contents.md"
    output_file = "C:\\Users\\Alpha\\Projects\\kds-ocr-paddle\\aisc360-22.json"
    
    print("Loading outline...")
    outline = parse_outline(outline_file)
    
    print("Parsing main content...")
    data = parse_main_content(content_file, outline, start_line=2561)
    
    print(f"Parsed {len(data)} sections.")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
