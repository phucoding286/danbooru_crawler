import numpy as np
import cv2


def center_crop(image: np.ndarray, crop_w: int, crop_h: int) -> np.ndarray:
    """
    Center crop ảnh theo kích thước (crop_w, crop_h)
    image: np.ndarray (H, W, C)
    """
    h, w = image.shape[:2]

    if crop_w > w or crop_h > h:
        raise ValueError("Crop size lớn hơn kích thước ảnh")

    x0 = (w - crop_w) // 2
    y0 = (h - crop_h) // 2

    return image[y0:y0 + crop_h, x0:x0 + crop_w]


def rescale_short_edge(image: np.ndarray, target: int) -> np.ndarray:
    """
    Rescale sao cho cạnh ngắn = target, giữ nguyên aspect ratio
    """
    h, w = image.shape[:2]

    if h < w:
        scale = target / h
    else:
        scale = target / w

    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )