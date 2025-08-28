from utility_pack.ocr_util import is_photo, ocr_page
import fitz, uuid, os, io
from enum import Enum
from PIL import Image

def perform_caption(img: Image):
    return "Dummy Caption"

def subtitle_images_from_pdf(pdf_path: str, caption_fn) -> str:
    """
    Extracts images from each page of a PDF, obtains captions via caption_fn(image),
    and inserts them as invisible text below each image.

    "caption_fn" should be a function that takes a Pillow Image and returns the caption as string.
    """
    pdf = fitz.open(pdf_path)
    for page_index, page in enumerate(pdf):
        infos = page.get_image_info()
        imgs  = page.get_images(full=True)
        for idx, info in enumerate(infos, start=1):
            bbox = fitz.Rect(info['bbox'])
            # Find matching xref by bbox containment
            xref = None
            for img in imgs:
                for rect in page.get_image_rects(img):
                    if rect.contains(bbox):
                        xref = img[0]
                        break
                if xref:
                    break
            if not xref:
                continue
            try:
                data = pdf.extract_image(xref)["image"]
                if not data:
                    continue
                img = Image.open(io.BytesIO(data))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                try:
                    caption = caption_fn(img)
                except Exception:
                    caption = ""
                # Calculate textbox
                y0 = bbox.y1 + 5
                y1 = min(page.rect.y1 - 5, y0 + 30)
                rect = fitz.Rect(bbox.x0, y0, bbox.x1, y1)
                page.insert_textbox(rect, caption,
                                    fontsize=11,
                                    fontname="helv",
                                    render_mode=3)
            except Exception:
                continue

    out_path = f"/tmp/modified_{uuid.uuid4().hex}_{os.path.basename(pdf_path)}"
    pdf.save(out_path)
    pdf.close()
    return out_path

def get_pdf_page_as_image(pdf_path, page_num, zoom_factor=4):
    # 1 - Read PDF
    pdf_document = fitz.open(pdf_path)

    # 2 - Convert page to image
    page = pdf_document.load_page(page_num)

    # Define the zoom factor for the image resolution. Higher values mean more pixels.
    mat = fitz.Matrix(zoom_factor, zoom_factor)

    # Render the page to an image (pixmap)
    pix_image = page.get_pixmap(matrix=mat)

    return pix_image

class OcrStrategy(str, Enum):
    Always = "always"
    Never = "never"
    Auto = "auto"

def pdf_to_text(filepath, strategy_ocr: OcrStrategy, zoom_factor=3.5):
    pdf_document = fitz.open(filepath)

    page_texts = []

    for page_number in range(pdf_document.page_count):
        print(f'Processando página {page_number + 1}', flush=True)

        page = pdf_document.load_page(page_number)
        page_text = page.get_text("text")

        if strategy_ocr == OcrStrategy.Never:
            pass
        elif strategy_ocr == OcrStrategy.Always:
            pix_image = get_pdf_page_as_image(filepath, page_number, zoom_factor)
            page_text = ocr_page(pix_image)
        else:
            pix_image = get_pdf_page_as_image(filepath, page_number, zoom_factor)
            if len(page_text.split(' ')) < 10 or is_photo(pix_image) or strategy_ocr == OcrStrategy.Always:
                page_text = ocr_page(pix_image)

        while '\n\n' in page_text:
            page_text = page_text.replace('\n\n', '\n')

        page_texts.append(page_text)

    return {
        "full_text": "\n".join(page_texts),
        "text_per_page": [{
            "page": idx + 1,
            "text": text
        } for idx, text in enumerate(page_texts)]
    }

def redact_pdf_and_convert_to_images(pdf_path, search_strings, output_dir="output", output_images=True):
    """
    Process a PDF by redacting specified text and optionally converting pages to images.
    
    Args:
        pdf_path (str): Path to the input PDF file
        search_strings (list): List of strings to search for and redact
        output_dir (str): Directory to save output files
        output_images (bool): If True, output as images; if False, output as PDF
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PDF
    try:
        doc = fitz.open(pdf_path)
        print(f"Loaded PDF: {pdf_path}")
        print(f"Number of pages: {doc.page_count}")
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return
    
    # Get all text from the PDF
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        full_text += page.get_text()
    
    print(f"Total characters in PDF: {len(full_text)}")
    
    # Count occurrences of all search strings
    total_occurrences = 0
    for search_string in search_strings:
        occurrences = full_text.count(search_string)
        print(f"Found '{search_string}' {occurrences} times in the PDF")
        total_occurrences += occurrences
    
    if total_occurrences == 0:
        action = "converting pages to images" if output_images else "saving as PDF"
        print(f"No occurrences found. {action.capitalize()} without redaction.")
    
    # Process each page
    images = []
    total_redactions = 0
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Search for all strings on this page
        page_redactions = 0
        redaction_areas = []  # Store all redaction rectangles for this page
        
        for search_string in search_strings:
            text_instances = page.search_for(search_string)
            page_redactions += len(text_instances)
            
            if len(text_instances) > 0:
                print(f"Page {page_num + 1}: Found {len(text_instances)} instance(s) of '{search_string}'")
                
                # Collect redaction areas
                for inst in text_instances:
                    # Create a rectangle with padding
                    rect = fitz.Rect(inst)
                    rect.x0 -= 1
                    rect.y0 -= 1
                    rect.x1 += 1
                    rect.y1 += 1
                    redaction_areas.append(rect)
        
        # Apply redactions (removes text from text layer and adds black rectangles)
        if redaction_areas:
            # Create redaction annotations that will remove the text
            for rect in redaction_areas:
                redact_annot = page.add_redact_annot(rect)
                # Set the redaction to be filled with black
                redact_annot.set_colors(fill=(0, 0, 0))
                redact_annot.update()
            
            # Apply all redactions on this page (this removes the text from the text layer)
            page.apply_redactions()
            
            # For visual output, also draw black rectangles to ensure complete coverage
            for rect in redaction_areas:
                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))
        
        total_redactions += page_redactions
        
        if output_images:
            # Convert page to image
            # Higher resolution for better quality (default is 72 DPI, we use 150)
            mat = fitz.Matrix(150/72, 150/72)  # 150 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Save the image
            img_filename = f"page_{page_num + 1:03d}.png"
            img_path = os.path.join(output_dir, img_filename)
            img.save(img_path, "PNG")
            
            images.append(img_path)
            print(f"Saved: {img_path}")
    
    if output_images:
        # Close the PDF
        doc.close()
        
        print(f"\nProcessing complete!")
        print(f"Total redactions made: {total_redactions}")
        print(f"Images saved to: {output_dir}")
        print(f"Generated {len(images)} image files")
        
        return images
    else:
        # Apply redactions on all pages to ensure text layer removal
        for page in doc:
            page.apply_redactions()

        # Save the redacted PDF with full cleanup
        output_pdf_path = os.path.join(output_dir, "redacted_" + os.path.basename(pdf_path))
        doc.save(output_pdf_path, garbage=4, deflate=True)
        doc.close()
        
        print(f"\nProcessing complete!")
        print(f"Total redactions made: {total_redactions}")
        print(f"Redacted PDF saved to: {output_pdf_path}")
        
        return output_pdf_path
