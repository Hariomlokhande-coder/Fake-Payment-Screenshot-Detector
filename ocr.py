import pytesseract
from PIL import Image
import os

# ✅ Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Path to the image (update this as needed)
image_path = r"E:\detector\Fake-Payment-Screenshot-Detector-main\dataset\real\hariom.jpg"

# ✅ Check if file exists
if not os.path.exists(image_path):
    print(f"[ERROR] Image not found: {image_path}")
else:
    # ✅ Load and extract text
    img = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(img)

    print("Extracted Text:")
    print(extracted_text)