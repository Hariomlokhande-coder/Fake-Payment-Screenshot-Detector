from PIL import Image, ImageChops, ImageEnhance
import os

def error_level_analysis(image_path, output_path="ela_output.jpg", quality=90):
    """
    Performs Error Level Analysis (ELA) on a given image and saves the result.
    
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the ELA result.
        quality (int): JPEG compression quality (lower means higher difference).
    """
    try:
        # Open and convert image to RGB
        original = Image.open(image_path).convert('RGB')

        # Save with reduced quality for ELA
        temp_jpeg_path = "temp_ela_compressed.jpg"
        original.save(temp_jpeg_path, "JPEG", quality=quality)

        # Re-open the compressed image
        recompressed = Image.open(temp_jpeg_path)

        # Compute pixel-wise difference
        diff = ImageChops.difference(original, recompressed)

        # Enhance brightness of difference
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0 / max_diff if max_diff else 1
        diff = ImageEnhance.Brightness(diff).enhance(scale)

        # Save result
        diff.save(output_path)
        print(f"🟢 ELA output saved to: {output_path}")

        # Clean up temp file
        if os.path.exists(temp_jpeg_path):
            os.remove(temp_jpeg_path)

    except Exception as e:
        print(f"[ERROR] ELA failed: {e}")