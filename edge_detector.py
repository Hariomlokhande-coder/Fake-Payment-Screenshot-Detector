import cv2
import numpy as np

def get_edge_pixel_count(image_path):
    """
    This function reads an image, applies Canny edge detection,
    and returns the count of edge pixels.
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return 0  # Image not found or invalid

        edges = cv2.Canny(image, 50, 150)
        edge_pixel_count = np.sum(edges > 0)
        return edge_pixel_count

    except Exception as e:
        print(f"[ERROR] Edge detection failed: {e}")
        return 0