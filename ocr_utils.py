import base64
import os
import requests
import time

API_URL = "https://oeocy5w7q4f7ufe1.aistudio-app.com/layout-parsing"
TOKEN = "891405228ff58e8d5b37fd3adee87616227fe625"

def process_file_via_api(file_path, output_dir, file_type=0):
    """
    Processes a file (PDF or image) via the layout-parsing API.
    file_type: 0 for PDF, 1 for image.
    """
    print(f"Processing: {file_path} -> {output_dir}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False

    with open(file_path, "rb") as file:
        file_bytes = file.read()
        file_data = base64.b64encode(file_bytes).decode("ascii")

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "file": file_data,
        "fileType": file_type,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }

    try:
        # Note: Added verify=False as a workaround for local certificate verification issues.
        # In a production environment, proper certificates should be configured.
        response = requests.post(API_URL, json=payload, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"Error processing {file_path}: {response.status_code} - {response.text}")
            return False

        result = response.json().get("result")
        if not result:
            print(f"No result found in API response for {file_path}")
            return False

        os.makedirs(output_dir, exist_ok=True)

        for i, res in enumerate(result["layoutParsingResults"]):
            md_text = res.get("markdown", {}).get("text", "")
            md_filename = os.path.join(output_dir, f"doc_{i}.md")
            with open(md_filename, "w", encoding="utf-8") as md_file:
                md_file.write(md_text)
            print(f"Markdown document saved at {md_filename}")
            
            # Save images in markdown
            markdown_images = res.get("markdown", {}).get("images", {})
            for img_path, img_url in markdown_images.items():
                full_img_path = os.path.join(output_dir, img_path)
                os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
                try:
                    img_bytes = requests.get(img_url, verify=False).content
                    with open(full_img_path, "wb") as img_file:
                        img_file.write(img_bytes)
                    print(f"Image saved to: {full_img_path}")
                except Exception as img_e:
                    print(f"Failed to save markdown image {img_path}: {img_e}")
                
            # Save output images
            output_images = res.get("outputImages", {})
            for img_name, img_url in output_images.items():
                try:
                    img_response = requests.get(img_url, verify=False)
                    if img_response.status_code == 200:
                        filename = os.path.join(output_dir, f"{img_name}_{i}.jpg")
                        with open(filename, "wb") as f:
                            f.write(img_response.content)
                        print(f"Output image saved to: {filename}")
                    else:
                        print(f"Failed to download output image: {img_name}, status code: {img_response.status_code}")
                except Exception as out_img_e:
                    print(f"Failed to save output image {img_name}: {out_img_e}")

        return True

    except Exception as e:
        print(f"Exception occurred while processing {file_path}: {e}")
        return False
