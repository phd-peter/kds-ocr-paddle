import base64
import os
import requests

API_URL = "https://oeocy5w7q4f7ufe1.aistudio-app.com/layout-parsing"
TOKEN = "891405228ff58e8d5b37fd3adee87616227fe625"

INPUT_DIR = "data/chunks/design-parsed"
OUTPUT_ROOT = "data/output/design-parsed"

def process_file(file_path, output_dir):
    print(f"Processing: {file_path} -> {output_dir}")
    
    with open(file_path, "rb") as file:
        file_bytes = file.read()
        file_data = base64.b64encode(file_bytes).decode("ascii")

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    # For PDF documents, set `fileType` to 0; for images, set `fileType` to 1
    payload = {
        "file": file_data,
        "fileType": 0,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }

    try:
        # Note: Added verify=False as a workaround for local certificate verification issues.
        response = requests.post(API_URL, json=payload, headers=headers, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error processing {file_path}: {response.text}")
            return

        result = response.json()["result"]
        os.makedirs(output_dir, exist_ok=True)

        for i, res in enumerate(result["layoutParsingResults"]):
            md_filename = os.path.join(output_dir, f"doc_{i}.md")
            with open(md_filename, "w") as md_file:
                md_file.write(res["markdown"]["text"])
            print(f"Markdown document saved at {md_filename}")
            
            for img_path, img in res["markdown"]["images"].items():
                full_img_path = os.path.join(output_dir, img_path)
                os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
                img_bytes = requests.get(img, verify=False).content
                with open(full_img_path, "wb") as img_file:
                    img_file.write(img_bytes)
                print(f"Image saved to: {full_img_path}")
                
            for img_name, img in res["outputImages"].items():
                img_response = requests.get(img, verify=False)
                if img_response.status_code == 200:
                    # Save image to local
                    filename = os.path.join(output_dir, f"{img_name}_{i}.jpg")
                    with open(filename, "wb") as f:
                        f.write(img_response.content)
                    print(f"Image saved to: {filename}")
                else:
                    print(f"Failed to download image: {img_name}, status code: {img_response.status_code}")

    except Exception as e:
        print(f"Exception occurred while processing {file_path}: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory '{INPUT_DIR}' does not exist.")
        return

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")])
    
    if not files:
        print(f"No PDF files found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files)} PDF files to process.")

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        # Create a specific folder for this PDF in the output root
        # Using filename without extension as the folder name
        folder_name = os.path.splitext(filename)[0]
        output_dir = os.path.join(OUTPUT_ROOT, folder_name)
        
        process_file(file_path, output_dir)
        print("-" * 50)

if __name__ == "__main__":
    main()
