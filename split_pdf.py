
import os
import math
import argparse
from pypdf import PdfReader, PdfWriter

def split_pdf(file_path, output_dir, chunk_size=30, prefix=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        num_chunks = math.ceil(total_pages / chunk_size)
        
        base_name = prefix or os.path.splitext(os.path.basename(file_path))[0]
        generated_files = []

        for i in range(num_chunks):
            start_page = i * chunk_size
            end_page = min((i + 1) * chunk_size, total_pages)
            
            writer = PdfWriter()
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_filename = f"{base_name}_part_{i+1:02d}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            print(f"Saved {output_filename} (pages {start_page+1}-{end_page})")
            generated_files.append(output_path)
            
        print("PDF splitting completed successfully.")
        return generated_files

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a PDF into smaller chunks.")
    parser.add_argument("file_path", help="Path to the source PDF file")
    parser.add_argument("--output_dir", default="data/chunks", help="Directory to save the chunks")
    parser.add_argument("--chunk_size", type=int, default=30, help="Number of pages per chunk")
    parser.add_argument("--prefix", help="Prefix for the output filenames")

    args = parser.parse_args()
    
    # If output_dir is data/chunks, create a subfolder with the file name
    final_output_dir = args.output_dir
    if args.output_dir == "data/chunks":
        name = os.path.splitext(os.path.basename(args.file_path))[0]
        final_output_dir = os.path.join(args.output_dir, name)

    split_pdf(args.file_path, final_output_dir, args.chunk_size, args.prefix)
