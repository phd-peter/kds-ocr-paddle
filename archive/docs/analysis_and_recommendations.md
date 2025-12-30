# Markdown Parsing & Vector Embedding Analysis

## 1. Current Data Structure Analysis
Based on the review of `output/KDS143105/doc_48.md` and `output-0/doc_13.md`:

### Tables
- **Format**: HTML `<table>` tags are used instead of standard Markdown tables.
- **Complexity**: Tables include `rowspan` and `colspan`, indicating complex headers and merged cells.
- **Styling**: Inline CSS (`style='...'`) is used for layout.
- **Captions**: Captions are provided in `<div>` tags immediately preceding the tables (e.g., `<div style="text-align: center;">표 3.4-1 ...</div>`).

### Images
- **References**: No direct image links (e.g., `![]()` or `<img>`) were found within the markdown text itself in the sampled files.
- **Files**: Images exist in the `imgs` directory and as `layout_det_res_X.jpg` (likely layout detection results).
- **Context**: If images are not explicitly linked in the text, associating them with the correct text chunk will require inferring relationships (e.g., by file naming convention or page number if available).

## 2. Parsing Recommendations for Vector Embedding

To prepare this data for vector embedding (RAG), simple text extraction is insufficient. Here is a recommended strategy:

### A. Table Parsing Strategy
Standard text splitters often mangle HTML tables.
1.  **Convert to Structured Text**: Use a library like `BeautifulSoup` to parse the HTML.
2.  **Linearization**: Convert each row into a self-contained string.
    *   *Example*: "Row 1: Strength=Fy, Thickness=100mm or less, HSB380=380, HSB460=460..."
    *   *Why*: This preserves the relationship between headers and values even if the table is chunked.
3.  **Preserve Context**: Ensure the "Caption" (e.g., "Table 3.4-1") is embedded *with* the table data.
4.  **LLM-Friendly Format**: For complex tables, converting to JSON or a Markdown table (if simple enough) is often better for LLMs to understand than raw HTML.

### B. Image Parsing Strategy
Since images are not directly embedded in the text:
1.  **Association**: You need a logic to map `layout_det_res_X.jpg` to the corresponding `doc_X.md` content.
2.  **Embedding**:
    *   **Option 1 (Multimodal)**: Use a multimodal embedding model (like CLIP or Google's multimodal embeddings) to embed the image directly.
    *   **Option 2 (Captioning)**: Use a VLM (Vision Language Model) like GPT-4o or a local model to generate a detailed text description of the image (especially for diagrams/charts). Embed this text description.
    *   **Option 3 (OCR Text)**: If the images just contain text (which seems to be the case for `layout_det_res`), ensure that text is already in the markdown. If so, the image might be redundant for embedding, serving only as a visual reference.

### C. Chunking Strategy
1.  **Semantic Chunking**: Split by headers (`#### 4.2.1`).
2.  **Table Integrity**: **Do not** split a table in the middle. Treat the entire table (or logical rows) as a single unit.
3.  **Metadata Injection**: When embedding a chunk, inject metadata:
    *   Source Filename
    *   Section Header (e.g., "4.2.1 General Regulations")
    *   Table Caption (if applicable)

## 3. Recommended Workflow
1.  **Preprocessing Script**: Write a Python script to iterate through `doc_X.md` files.
2.  **HTML Extraction**: Detect `<table>` blocks. Parse them into a structured format (JSON/CSV).
3.  **Text Cleaning**: Remove HTML tags (`<div>`, `<table>`) from the main text but keep the content.
4.  **Embedding**: Embed the cleaned text and the structured table data separately or as enriched chunks.

## 4. Answers to Your Questions

### Q1: Should HTML tables be changed to Markdown/JSON/CSV?
**Yes, for the purpose of embedding (search).**
*   **Reason**: Vector embedding models work best with semantic text. Raw HTML contains many tokens (`<tr>`, `<td>`, `style=...`) that dilute the semantic meaning.
*   **Recommendation**: Convert the table to a **Markdown** format or a **Linearized Text** format (e.g., "Row 1: Column A is X, Column B is Y") for the embedding step. This ensures the model understands the *content* of the table.

### Q2: How to handle images inside a table?
*   **Current Status**: My analysis of your files showed **no images currently inside the tables**.
*   **Strategy (If they exist)**: If you do have images in tables (e.g., `<img src="...">` inside a `<td>`):
    1.  **Extraction**: Detect the `<img>` tag during parsing.
    2.  **Description**: Use a VLM (like GPT-4o) to generate a text description of that image (e.g., "Figure showing stress distribution").
    3.  **Replacement**: Replace the `<img>` tag in your *embedding text* with a placeholder like `[Image: Description of stress distribution]`.
    4.  **Preservation**: Keep the original `<img>` tag in the *metadata* (see "Alias Strategy" below) so it displays correctly in the chatbot.

### Q3: What about an "Alias" strategy (Search vs. Display)?
This is an excellent and highly recommended pattern, often called **"Hybrid Search"** or **"Decoupled Embedding"**.

**The Strategy:**
1.  **The "Alias" (for Search)**: You create a simplified, semantic representation of the table.
    *   *Format*: Markdown table, CSV, or a natural language summary generated by an LLM.
    *   *Role*: This is what you **vectorize**. The search engine uses this to find the relevant chunk.
2.  **The "Original" (for Display)**: You store the original raw HTML.
    *   *Role*: This is stored in the **metadata** of the vector chunk, NOT used for the vector calculation itself.
3.  **The Chatbot Flow**:
    *   **Step 1**: User asks a question.
    *   **Step 2**: System searches using the "Alias" vector.
    *   **Step 3**: System retrieves the matching chunk.
    *   **Step 4**: System extracts the `original_html` from the metadata.
    *   **Step 5**: Chatbot receives the `original_html` in its context and displays it to the user.

**Example Data Structure for Vector DB:**
```json
{
  "id": "doc_48_table_1",
  "text_vector": [0.12, -0.45, ...], // Embedding of the "Alias" (Markdown/Summary)
  "metadata": {
    "source": "doc_48.md",
    "type": "table",
    "original_html": "<table>...</table>", // The raw HTML for display
    "image_refs": ["layout_det_res_10.jpg"] // Any associated images
  }
}
```
