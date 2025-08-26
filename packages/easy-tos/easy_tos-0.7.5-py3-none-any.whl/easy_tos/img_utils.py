from PIL import Image
import numpy as np


class CropToForegroundSquare:
    def __init__(self, padding=0, threshold=10, target_size=None):
        """
        padding: Amount of padding to apply around the cropped square.
        threshold: Intensity threshold to consider a pixel as part of the foreground.
        target_size: Final output size (int or tuple). If int, output will be (target_size, target_size).
        """
        self.padding = padding
        self.threshold = threshold
        self.target_size = target_size if isinstance(target_size, tuple) else (target_size, target_size) if target_size else None

    def __call__(self, img):
        import numpy as np 
        import cv2 
        """
        img: PIL RGB Image (JPG-compatible)
        """
        # Convert to grayscale
        grayscale_image = img.convert("L")
        grayscale_image = np.array(grayscale_image)

        # Threshold and dilate to find foreground
        _, binary_image = cv2.threshold(grayscale_image, 254, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(binary_image, kernel, iterations=1)
        mask = np.where(mask < 255, 1, 0)

        # Find foreground bounds
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not np.any(rows) or not np.any(cols):
            result = img
        else:
            r_min, r_max = np.where(rows)[0][[0, -1]]
            c_min, c_max = np.where(cols)[0][[0, -1]]

            # Apply padding
            r_min = max(r_min - self.padding, 0)
            r_max = min(r_max + self.padding, img.height - 1)
            c_min = max(c_min - self.padding, 0)
            c_max = min(c_max + self.padding, img.width - 1)

            # Square bounding box
            square_size = max(r_max - r_min + 1, c_max - c_min + 1)
            center_h = (r_min + r_max) // 2
            center_w = (c_min + c_max) // 2
            left = max(center_w - square_size // 2, 0)
            top = max(center_h - square_size // 2, 0)
            right = min(left + square_size, img.width)
            bottom = min(top + square_size, img.height)

            # Crop
            square_img = img.crop((left, top, right, bottom))

            # Pad if needed
            if square_img.size != (square_size, square_size):
                padded_img = Image.new('RGB', (square_size, square_size), (0, 0, 0))
                paste_x = (square_size - square_img.width) // 2
                paste_y = (square_size - square_img.height) // 2
                padded_img.paste(square_img, (paste_x, paste_y))
                result = padded_img
            else:
                result = square_img

        # Resize if target_size is set
        if self.target_size:
            result = result.resize(self.target_size, Image.LANCZOS)

        return result