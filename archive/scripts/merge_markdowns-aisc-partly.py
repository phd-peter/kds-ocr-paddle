import os
import re
import shutil

# Configuration
SOURCE_DIRS = ["aisc360-22-markdown/AISC 360-22w_part_18"]
TARGET_IMG_DIR = "merged_aisc_partly_images"
TARGET_MD_FILE = "merged_aisc_partly_output.md"

def numeric_sort_key(filename):
    """Sort mechanism for doc_X.md files"""
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else 0

def process_markdown_files():
    # Create target directories
    if not os.path.exists(TARGET_IMG_DIR):
        os.makedirs(TARGET_IMG_DIR)
        print(f"Created directory: {TARGET_IMG_DIR}")
    
    # Open output file
    with open(TARGET_MD_FILE, 'w', encoding='utf-8') as outfile:
        
        for source_dir in SOURCE_DIRS:
            if not os.path.exists(source_dir):
                print(f"Warning: {source_dir} not found. Skipping.")
                continue
                
            print(f"Processing {source_dir}...")
            
            # Use a safe name for the directory prefix in images
            safe_source_name = source_dir.replace("/", "_").replace("\\", "_")

            # Find all doc_*.md files
            files = [f for f in os.listdir(source_dir) if f.startswith("doc_") and f.endswith(".md")]
            # Sort them numerically
            files.sort(key=numeric_sort_key)
            
            for filename in files:
                file_path = os.path.join(source_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    
                # Function to replace image paths
                def replace_image_link(match):
                    # Determine regex type
                    full_match = match.group(0)
                    
                    # Check for Markdown style ![alt](path)
                    if match.re.pattern.startswith(r'\!\[') or match.re.pattern.startswith(r'!\[') :
                        alt_text = match.group(1)
                        img_path = match.group(2)
                        is_html = False
                    # Check for HTML style <img src="path">
                    else:
                        img_path = match.group(1)
                        is_html = True
                    
                    # Extract just the filename
                    img_filename = os.path.basename(img_path)
                    
                    # Logic 1: Ignore layout_*.jpg
                    if img_filename.startswith("layout_"):
                        print(f"  Skipping layout image: {img_filename}")
                        return "" # Remove the image tag entirely
                    
                    # Logic 2: Move and rename image
                    # Construct source path. Assumes path in md is relative e.g. "imgs/foo.jpg"
                    # We need to resolve it relative to the markdown file
                    # Usually "output-X/imgs/foo.jpg"
                    
                    # Careful: img_path might be "imgs/foo.jpg" or "./imgs/foo.jpg"
                    src_img_full_path = os.path.join(source_dir, img_path)
                    
                    if not os.path.exists(src_img_full_path):
                        print(f"  Warning: Image not found at {src_img_full_path}")
                        # Return original if not found, or maybe keep it? Let's keep original for safety but warn
                        return full_match
                        
                    # New filename to avoid collisions: safe_source_name_originalName.jpg
                    new_filename = f"{safe_source_name}_{img_filename}"
                    dst_img_full_path = os.path.join(TARGET_IMG_DIR, new_filename)
                    
                    # Copy file
                    shutil.copy2(src_img_full_path, dst_img_full_path)
                    
                    # Return new link
                    if is_html:
                        return f'<img src="{TARGET_IMG_DIR}/{new_filename}" >'
                    else:
                        return f'![{alt_text}]({TARGET_IMG_DIR}/{new_filename})'

                # Regex for Markdown images: ![alt](path)
                # Note: This is a simple regex, might need adjustment for complex paths
                content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image_link, content)
                
                # Regex for HTML images: <img src="path" ... >
                # We need to capture src. Simplistic approach assuming src is first or we find it.
                # Let's match specific pattern seen in files: <img src="imgs/..." >
                # Supporting optional other attributes widely is harder with partial regex, 
                # but let's try to capture 'src="([^"]+)"'
                
                def replace_html_img(m):
                    # m.group(0) is whole tag
                    # We need to find src attribute within it
                    src_match = re.search(r'src="([^"]+)"', m.group(0))
                    if src_match:
                        # Construct a fake match object to reuse logic, or just call logic directly
                        old_src = src_match.group(1)
                        filename = os.path.basename(old_src)
                        
                        if filename.startswith("layout_"):
                            print(f"  Skipping layout image (HTML): {filename}")
                            return ""
                            
                        src_full = os.path.join(source_dir, old_src)
                        if not os.path.exists(src_full):
                             print(f"  Warning: Image not found {src_full}")
                             return m.group(0)
                        
                        new_name = f"{safe_source_name}_{filename}"
                        dst_full = os.path.join(TARGET_IMG_DIR, new_name)
                        shutil.copy2(src_full, dst_full)
                        
                        # Replace just the src part in the tag
                        new_tag = m.group(0).replace(old_src, f"{TARGET_IMG_DIR}/{new_name}")
                        return new_tag
                    return m.group(0)

                content = re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', replace_html_img, content)

                # Append content
                outfile.write(f"\n\n<!-- Source: {source_dir}/{filename} -->\n\n")
                outfile.write(content)

    print(f"Done. Merged markdown saved to {TARGET_MD_FILE}")

if __name__ == "__main__":
    process_markdown_files()
