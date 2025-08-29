import pydicom
import numpy as np


def preprocess_pixel_array(dcm: pydicom.FileDataset) -> np.ndarray:
    # extract the pixel array and apply the VOI LUT transformation
    img = pydicom.pixels.apply_voi_lut(dcm.pixel_array, dcm, index=0)

    # cast to float32, then normalize and cast to uint16
    img = img.astype(np.float32)
    img = (65535 * ((img - img.min()) / np.ptp(img))).astype(np.uint16)
    return img
