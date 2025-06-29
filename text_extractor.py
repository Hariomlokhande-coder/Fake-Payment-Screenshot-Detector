import cv2
import pytesseract
import numpy as np

# Windows ke liye Tesseract ka path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found!")
        return

    # 1. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Binarization (thresholding) for better contrast
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. (Optional) Noise removal
    denoised = cv2.medianBlur(thresh, 3)

    # 4. OCR extraction (use denoised image)
    extracted_text = pytesseract.image_to_string(denoised, lang='eng', config='--psm 6')

    print("📌 Extracted Text from Screenshot:\n")
    print(extracted_text)

# Example usage
extract_text("lakshtransaction1.jpg")
