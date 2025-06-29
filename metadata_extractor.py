from PIL import Image, ExifTags
import os
import hashlib
from datetime import datetime

def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image.getexif()
        metadata_info = {}

        # ✅ EXIF Metadata
        if exif_data and len(exif_data) > 0:
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                metadata_info[tag_name] = str(value)
        else:
            metadata_info["Message"] = "No EXIF metadata found."

        # ✅ Additional metadata
        with open(image_path, "rb") as f:
            file_data = f.read()
            file_hash = hashlib.md5(file_data).hexdigest()

        stats = os.stat(image_path)
        metadata_info.update({
            "File Name": os.path.basename(image_path),
            "File Size (Bytes)": stats.st_size,
            "Last Modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "File Hash (MD5)": file_hash,
            "Image Format": image.format,
            "Image Mode": image.mode,
            "Image Size": f"{image.width}x{image.height}",
        })

        return metadata_info

    except Exception as e:
        return {"Error": f"Metadata extraction failed: {str(e)}"}