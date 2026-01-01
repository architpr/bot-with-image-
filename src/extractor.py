from unstructured.partition.pdf import partition_pdf
from src.config import ASSETS_DIR
import os

class PDFExtractor:
    def __init__(self):
        pass

    def extract(self, pdf_path):
        """
        Extracts text and images using Unstructured.
        Strictly links 'image_path' metadata to Text chunks on the same page.
        """
        print(f"Starting Unstructured partition for {pdf_path}...")
        
        # 1. Partition PDF (Extract images to ASSETS_DIR)
        elements = partition_pdf(
            filename=pdf_path,
            extract_images_in_pdf=True,
            extract_image_block_output_dir=ASSETS_DIR,
            infer_table_structure=True,
        )

        # 2. Organize Images by Page
        page_image_map = {}
        text_elements = []

        for el in elements:
            page_num = el.metadata.page_number
            
            # Identify if it's an Image
            if "Image" in str(type(el)):
                # Get path from metadata
                img_path = getattr(el.metadata, "image_path", None)
                
                if img_path:
                    # Unstructured saves absolute paths usually if output_dir is absolute
                    if page_num not in page_image_map:
                        page_image_map[page_num] = []
                    page_image_map[page_num].append(img_path)
            
            # Collect Text/Table elements to be chunks
            if "Text" in str(type(el)) or "Table" in str(type(el)) or "Title" in str(type(el)) or "NarrativeText" in str(type(el)):
                 # Filter out very short noise
                 if len(str(el)) > 20: 
                    text_elements.append({
                        "content": str(el),
                        "page": page_num,
                        "type": str(type(el)).split("'")[1] # Clean type name
                    })

        # 3. Create Final Data with Linked Metadata
        final_data = []
        for item in text_elements:
            page = item["page"]
            
            # Strict Linking: If images exist on this page, add them to metadata
            linked_images = page_image_map.get(page, [])
            
            # The Requirement: "add a metadata key called 'image_path' that contains the local file path"
            # We will store the LIST of paths.
            
            final_data.append({
                "type": item["type"],
                "content": item["content"],
                "metadata": {
                    "page": page,
                    "image_path": linked_images # Requirement specified 'image_path' key
                }
            })
            
        return final_data
