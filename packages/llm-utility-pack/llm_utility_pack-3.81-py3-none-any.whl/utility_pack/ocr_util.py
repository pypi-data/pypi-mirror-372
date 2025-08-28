import os

os.environ['OMP_THREAD_LIMIT'] = "1"

import pytesseract, cv2, numpy as np, os
from tempfile import NamedTemporaryFile
from deskew import determine_skew
from PIL import Image, ImageOps
from pytesseract import Output
from skimage import filters

from utility_pack.logger import log_exception

def detect_if_darkmode_image(image, threshold=0.5):
    try:
        # Convert Pillow image to NumPy array
        np_image = np.array(image)

        # Convert to grayscale using OpenCV
        # Check if the image is already grayscale.  If not, convert it.
        if len(np_image.shape) > 2 and np_image.shape[2] > 1:
            gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = np_image # If already grayscale, no conversion needed.

        if gray_image is None:
            raise ValueError("Could not open the image file.")

        # Normalize pixel values between 0 and 1
        normalized = gray_image / 255.0

        # Calculate the mean pixel intensity
        mean_intensity = np.mean(normalized)

        # If the mean intensity is lower than threshold, assume black background
        return mean_intensity < threshold
    except Exception:
        log_exception()

    return False

def invert_image(input_pil_image):
    return ImageOps.invert(input_pil_image.convert("RGB"))

def array_img(img, denoise=True):
    pil_image_rgb = img.convert('RGB')
    img = np.array(pil_image_rgb)

    if len(img.shape) == 3:
        if img.shape[2] > 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if denoise:
        img = cv2.fastNlMeansDenoising(img, None)

    return img

def rotate_image(pil_image, angle):
    return pil_image.rotate(angle, expand=True)

def sauvola_binarization(pil_image, window_size=15, k=0.2):
    # Open the image using Pillow
    pil_image = pil_image.convert('L')
    
    # Convert Pillow image to numpy array
    img_array = np.array(pil_image)
    
    # Perform Sauvola thresholding
    threshold = filters.threshold_sauvola(img_array, window_size=window_size, k=k)
    
    # Apply the threshold to create a binary image
    binary = img_array > threshold
    
    # Convert back to Pillow Image
    result = Image.fromarray((binary * 255).astype(np.uint8))
    
    return result

def raw_ocr_with_topbottom_leftright(image, lang='por'):
    # Raw extraction
    data = pytesseract.image_to_data(image, lang=lang, output_type=Output.DATAFRAME)
    
    # Clean the data
    data = data.dropna(subset=['text'])
    data['text'] = data['text'].str.strip()

    # Sort by top position, then left position
    data_sorted = data.sort_values(['top', 'left'])

    # Group by top position (approximately) to get lines
    data_sorted['line_num'] = (data_sorted['top'] / 10).astype(int)

    # Concatenate text for each line
    result = data_sorted.groupby('line_num')['text'].apply(' '.join).reset_index()

    # Final text output
    text = '\n'.join(result['text'])

    return text

def raw_ocr_auto_psm(image, lang='por', psm=4):
    # Raw extraction with specified PSM
    data = pytesseract.image_to_data(image, lang=lang, config=f'--psm {psm}', output_type=Output.DATAFRAME)
    
    # Clean the data
    data = data.dropna(subset=['text'])
    data['text'] = data['text'].str.strip()
    data = data[data['text'] != '']  # Remove empty strings
    
    # Group by block_num and par_num to keep text blocks together
    # Sort by top position first to maintain reading order
    data_sorted = data.sort_values(['top', 'left'])
    
    # Group by block and paragraph to maintain text block structure
    grouped = data_sorted.groupby(['block_num', 'par_num'], sort=False)
    
    blocks = []
    for (block_num, par_num), group in grouped:
        # Within each block/paragraph, sort by line and word position
        group_sorted = group.sort_values(['line_num', 'word_num'])
        
        # Join words within the same line
        lines = group_sorted.groupby('line_num')['text'].apply(' '.join)
        
        # Join lines within the block/paragraph
        block_text = '\n'.join(lines.values)
        
        # Store with the top position for final sorting
        blocks.append({
            'text': block_text,
            'top': group['top'].min(),
            'block_num': block_num,
            'par_num': par_num
        })
    
    # Sort blocks by their top position to maintain top-to-bottom order
    blocks_sorted = sorted(blocks, key=lambda x: x['top'])
    
    # Extract just the text and join with double newlines to separate blocks
    text = '\n\n'.join([block['text'] for block in blocks_sorted])
    
    return text

def resize_image(pil_image, percentage_resize=0.1):
    width, height = pil_image.size
    new_width = int(width * (1 - percentage_resize))
    new_height = int(height * (1 - percentage_resize))
    resized_image = pil_image.resize((new_width, new_height))
    return resized_image

def sequential_resize(pil_image):
    # Resize image iteratively until it is close to 1500 pixels wide, 2100 pixels tall
    target_width = 1500
    target_height = 2100
    current_image = pil_image
    resize_factor = 0.03  # Start with a 10% reduction

    while current_image.width > target_width * 1.1 or current_image.height > target_height * 1.1:
        current_image = resize_image(current_image, resize_factor)
        # Optionally adjust the resize factor if the image is still much larger
        if current_image.width > target_width * 2 or current_image.height > target_height * 2:
            resize_factor = 0.1
        else:
            resize_factor = 0.03 # Reset to smaller factor for finer adjustments

    return current_image

def ensure_pil_image_type(input_data):
    """
    Converts various data types to a PIL Image.

    Args:
        input_data: The data to convert.  Can be a NumPy array,
                    a boolean NumPy array, a PIL Image, or a list/tuple.

    Returns:
        PIL.Image.Image: A PIL Image object. Returns None on Error.
    """
    if input_data is None:
        return None

    if isinstance(input_data, Image.Image):
        return input_data  # Already a PIL Image

    if isinstance(input_data, np.ndarray):
        if input_data.dtype == np.bool_:
            # Convert boolean array to 8-bit grayscale (0 or 255)
            img_uint8 = (input_data * 255).astype(np.uint8)
            return Image.fromarray(img_uint8)
        elif input_data.dtype in [np.uint8, np.uint16, np.int16, np.int32, np.float32, np.float64]:
            # Handle different data types, scaling if necessary.
            # Find min and max, and scale to 0-255.  Handle the case where min == max.
            min_val = np.min(input_data)
            max_val = np.max(input_data)
            if min_val == max_val:
                # Create a uniform image.  Choose 128 as the gray level.
                img_uint8 = np.full_like(input_data, 128, dtype=np.uint8)
            else:
                scaled_data = ((input_data - min_val) / (max_val - min_val)) * 255
                img_uint8 = scaled_data.astype(np.uint8)
            # Handle grayscale and RGB images.  Assume grayscale if last dimension is 1.
            if len(input_data.shape) == 2 or (len(input_data.shape) == 3 and input_data.shape[2] == 1):
                return Image.fromarray(img_uint8)
            elif len(input_data.shape) == 3 and input_data.shape[2] in [3, 4]:
                 return Image.fromarray(img_uint8.astype(np.uint8), mode='RGB') #Assume RGB
            else:
                print(f"Numpy Array Shape: {input_data.shape}")
                print(f"Numpy Array dtype: {input_data.dtype}")
                raise ValueError("Cannot convert NumPy array with this shape to PIL Image.")
        else:
            print(f"Numpy Array dtype: {input_data.dtype}")
            raise ValueError("NumPy array of this data type cannot be converted to PIL Image.")

    elif isinstance(input_data, (list, tuple)):
        # Attempt to convert to a NumPy array and then to a PIL Image
        try:
            np_array = np.array(input_data)
            return ensure_pil_image_type(np_array)  # Recursive call
        except Exception as e:
            raise ValueError(f"Cannot convert list/tuple to PIL Image: {e}")
        
    elif isinstance(input_data, str):
        # Assume it's a file path
        return Image.open(input_data)

    else:
        raise ValueError(f"Cannot convert data of type {type(input_data)} to PIL Image.")

def ocr_image_pipeline(pil_image, enhance_psm_grouping=False):
    try:
        text = ""

        pil_image = ensure_pil_image_type(pil_image)

        if detect_if_darkmode_image(pil_image):
            pil_image = invert_image(pil_image)

        # Binarize by default
        image_sauvola = sauvola_binarization(pil_image, window_size=15, k=0.1)

        # Resize to optimal size, sequentially
        image_sauvola = sequential_resize(image_sauvola)

        # Detect rotation
        angle = determine_skew(array_img(image_sauvola, denoise=False)) * 0.85

        if angle != 0:
            image_sauvola = rotate_image(image_sauvola, angle)

        if text == "":
            text = raw_ocr_with_topbottom_leftright(image_sauvola) if not enhance_psm_grouping else raw_ocr_auto_psm(image_sauvola)
            text = text.replace('\x0c', '').strip()

        while '  ' in text:
            text = text.replace('  ', ' ')
        
        while '\n ' in text:
            text = text.replace('\n ', '\n')
        
        while '\n\n' in text:
            text = text.replace('\n\n', '\n')

        return text
    except Exception as e:
        log_exception()

    return ""

def is_photo(pix_image, threshold=0.6):
    # Convert to PIL image
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_image:
        pix_image.save(temp_image)

        # Open the image
        img = Image.open(temp_image.name)
        
        # Convert to grayscale
        img_gray = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img_gray)

        # Calculate the percentage of white pixels
        white_pixels = np.sum(img_array > 200)

        # Calculate the percentage of white pixels
        total_pixels = img_array.size

        # Calculate the percentage of white pixels
        white_pixel_ratio = white_pixels / total_pixels

        return not (white_pixel_ratio > threshold)

def ocr_page(pix_image):
    # Convert to PIL image
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_image:
        pix_image.save(temp_image)
        image = Image.open(temp_image.name)
        return ocr_image_pipeline(image)
