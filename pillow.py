from PIL import Image
from PIL.ExifTags import TAGS
import os

# ✅ Image path (update this as needed)
image_path = r"E:\detector\Fake-Payment-Screenshot-Detector-main\dataset\real\hariom.jpg"

# ✅ Check if file exists
if not os.path.exists(image_path):
    print(f"❌ Image not found: {image_path}")
else:
    # ✅ Open image and extract EXIF
    image = Image.open(image_path)
    exif_data = image.getexif()  # Public method

    if exif_data and len(exif_data) > 0:
        print("📸 Extracted EXIF Metadata:")
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            print(f"{tag_name}: {value}")
    else:
        print("❌ No EXIF metadata found!")