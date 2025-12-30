# Implementation Plan - Merge Markdown and Images

## Goal

Detailed consolidation of markdown files from `output-0` through `output-5` into a single `merged_output.md` file in the root directory. Simultaneously, extract all referenced images into a new `merged_images` directory, updating the links in the merged markdown file. Explicitly exclude `layout_*.jpg` files.

## User Review Required
>
> [!IMPORTANT]
>
> - The script assumes `output-0` to `output-5` folders exist in the root.
> - Images are expected to be in an `imgs` subdirectory or referenced relatively.
> - `layout_*.jpg` files will be ignored during the copy process, and references to them (if any) will be removed or skipped.
> - Image filenames will be prefixed with the source folder name (e.g., `output-0_image.jpg`) to prevent collisions.

## Proposed Changes

### Root Directory

#### [NEW] [merge_markdowns.py](file:///Users/peter/Projects/kds-ocr-paddle/merge_markdowns.py)

- **Logic**:
    1. Define source directories: `output-0` to `output-5`.
    2. Create target directory: `merged_images`.
    3. Open target markdown file: `merged_output.md`.
    4. Iterate through each source directory.
        - Find and sort `doc_*.md` files numerically (e.g., `doc_1.md`, `doc_2.md`, `doc_10.md`).
    5. For each markdown file:
        - Read content.
        - Parse for image references using Regex.
            - Support Markdown syntax: `![alt](path)`
            - Support HTML syntax: `<img src="path">`
        - For each found image:
            - Check if filename starts with `layout_`. If so, remove the image reference/tag from content.
            - Construct source path (e.g., `output-0/imgs/foo.jpg`).
            - Construct destination path `merged_images/output-0_foo.jpg`.
            - Copy file if it exists.
            - Update reference in content to `merged_images/output-0_foo.jpg`.
        - Append processed content to `merged_output.md` with a newline separator.
    6. Print summary of processed files and images.

## Verification Plan

### Automated Tests

- Run the generated script: `python3 merge_markdowns.py`
- Check if `merged_output.md` exists and is non-empty.
- Check if `merged_images` directory exists and contains images.
- Verify `layout_` files are NOT in `merged_images`.

### Manual Verification

- Open `merged_output.md` and preview it to ensure images render correctly.
- Check a few image links to ensure they point to `merged_images/`.
