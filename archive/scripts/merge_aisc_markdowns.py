import os
import re
import shutil

# Configuration
SOURCE_ROOT = "aisc360-22-markdown"
TARGET_IMG_DIR = "merged_aisc_images"
TARGET_MD_FILE = "merged_aisc360-22.md"

def numeric_file_sort_key(filename):
    """Sort mechanism for doc_X.md files"""
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else 0

def numeric_dir_sort_key(dirname):
    """Sort mechanism for subdir_part_X directories"""
    # Expecting format "AISC 360-22w_part_X"
    match = re.search(r'part_(\d+)', dirname)
    return int(match.group(1)) if match else 0

def process_markdown_files():
    # Create target directories
    if not os.path.exists(TARGET_IMG_DIR):
        os.makedirs(TARGET_IMG_DIR)
        print(f"Created directory: {TARGET_IMG_DIR}")
    
    # Open output file
    with open(TARGET_MD_FILE, 'w', encoding='utf-8') as outfile:
        
        # Get list of subdirectories and sort them
        if not os.path.exists(SOURCE_ROOT):
             print(f"Error: Source root {SOURCE_ROOT} not found.")
             return

        subdirs = [d for d in os.listdir(SOURCE_ROOT) if os.path.isdir(os.path.join(SOURCE_ROOT, d)) and "part_" in d]
        subdirs.sort(key=numeric_dir_sort_key)

        print(f"Found {len(subdirs)} parts to process.")

        for subdir in subdirs:
            source_dir_path = os.path.join(SOURCE_ROOT, subdir)
            print(f"Processing {subdir}...")
            
            # Find all doc_*.md files
            files = [f for f in os.listdir(source_dir_path) if f.startswith("doc_") and f.endswith(".md")]
            # Sort them numerically
            files.sort(key=numeric_file_sort_key)
            
            for filename in files:
                file_path = os.path.join(source_dir_path, filename)
                
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
                        # print(f"  Skipping layout image: {img_filename}")
                        return "" # Remove the image tag entirely
                    
                    # Logic 2: Move and rename image
                    # Construct source path. Assumes path in md is relative e.g. "imgs/foo.jpg"
                    # We need to resolve it relative to the markdown file
                    
                    src_img_full_path = os.path.join(source_dir_path, img_path)
                    
                    if not os.path.exists(src_img_full_path):
                        print(f"  Warning: Image not found at {src_img_full_path} in {subdir}/{filename}")
                        return full_match
                        
                    # New filename to avoid collisions: subdir_originalName
                    # Sanitize subdir name slightly if needed, but standard should be fine
                    safe_subdir = subdir.replace(" ", "_")
                    new_filename = f"{safe_subdir}_{img_filename}"
                    dst_img_full_path = os.path.join(TARGET_IMG_DIR, new_filename)
                    
                    # Copy file if it doesn't exist to save IO, or just overwrite
                    if not os.path.exists(dst_img_full_path):
                        shutil.copy2(src_img_full_path, dst_img_full_path)
                    
                    # Return new link
                    # Using relative path for the markdown file to the images dir
                    # Since merged MD is in root and images are in merged_aisc_images/, path is just directory/filename
                    if is_html:
                        return f'<img src="{TARGET_IMG_DIR}/{new_filename}" >'
                    else:
                        return f'![{alt_text}]({TARGET_IMG_DIR}/{new_filename})'

                # Regex for Markdown images: ![alt](path)
                content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image_link, content)
                
                # Regex for HTML images: <img src="path" ... >
                def replace_html_img(m):
                    src_match = re.search(r'src="([^"]+)"', m.group(0))
                    if src_match:
                        old_src = src_match.group(1)
                        filename = os.path.basename(old_src)
                        
                        if filename.startswith("layout_"):
                            return ""
                            
                        src_full = os.path.join(source_dir_path, old_src)
                        if not os.path.exists(src_full):
                             print(f"  Warning: Image not found {src_full}")
                             return m.group(0)
                        
                        safe_subdir = subdir.replace(" ", "_")
                        new_name = f"{safe_subdir}_{filename}"
                        dst_full = os.path.join(TARGET_IMG_DIR, new_name)
                        
                        if not os.path.exists(dst_full):
                            shutil.copy2(src_full, dst_full)
                        
                        # Replace just the src part in the tag and ensure no other attributes break?
                        # Simplest is to reconstruct a simple tag or replace the src attribute.
                        # The prompt regex approach replaces the whole tag if we return new string.
                        # Let's conform to the structure of the previous script which returned a clean tag.
                        return f'<img src="{TARGET_IMG_DIR}/{new_name}" >'
                    return m.group(0)

                content = re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', replace_html_img, content)

                # Append content
                outfile.write(f"\n\n<!-- Source: {subdir}/{filename} -->\n\n")
                outfile.write(content)

    print(f"Done. Merged markdown saved to {TARGET_MD_FILE}")

if __name__ == "__main__":
    process_markdown_files()
