import json
import os

def extract_levels_1_and_2(json_file_path):
    if not os.path.exists(json_file_path):
        print(f"Error: File '{json_file_path}' not found.")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    print(f"{'Level':<6} | {'ID':<10} | {'Chapter':<8} | {'Title'}")
    print("-" * 60)

    for item in data:
        level = item.get('level')
        if level in [1, 2, 3]:
            item_id = item.get('id', '')
            chapter = item.get('chapter', '')
            title = item.get('title', '')
            
            indent = "" if level == 1 else "  "
            prefix = "Chapter " if level == 1 else "Section "
            
            print(f"{level:<6} | {item_id:<10} | {chapter:<8} | {indent}{prefix}{title}")

if __name__ == "__main__":
    json_path = "aisc360-22.json"
    extract_levels_1_and_2(json_path)
