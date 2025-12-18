
import os
import math
from pypdf import PdfReader, PdfWriter

def split_pdf(file_path, output_dir, chunk_size=30):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        num_chunks = math.ceil(total_pages / chunk_size)

        for i in range(num_chunks):
            start_page = i * chunk_size
            end_page = min((i + 1) * chunk_size, total_pages)
            
            writer = PdfWriter()
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_filename = f"AISC 360-22w_part_{i+1}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            print(f"Saved {output_filename} (pages {start_page+1}-{end_page})")
            
        print("PDF splitting completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    source_file = "aisc360-22/AISC 360-22w.pdf"
    output_directory = "aisc360-22"
    split_pdf(source_file, output_directory)
