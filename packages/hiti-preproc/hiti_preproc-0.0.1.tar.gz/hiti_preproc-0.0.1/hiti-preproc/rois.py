import numpy as np


def tissue_pad_patch(img: np.ndarray, roi: list[int], patch_size: int) -> np.ndarray:
    """
    function to tissue pad a patch given an image, a single ROI in the
    form [y_min, x_min, y_max, x_max] and the desired patch size
    """

    # unpack roi
    y_min, x_min, y_max, x_max = roi

    # get the center y, x
    y_center: int = (y_min + y_max) // 2
    x_center: int = (x_min + x_max) // 2

    # get initial patch coords
    half_size: int = patch_size // 2
    patch_y_min: int = y_center - half_size
    patch_x_min: int = x_center - half_size
    patch_y_max: int = y_center + half_size
    patch_x_max: int = x_center + half_size

    # correct the patch coords to make sure they fall within the image
    patch_y_max: int = max(min(patch_y_max, img.shape[0]), patch_size)
    patch_x_max: int = max(min(patch_x_max, img.shape[1]), patch_size)

    # ensure y_min is less than y_max - min_roi_size
    # and greater than 0
    patch_y_min: int = max(min(patch_y_min, patch_y_max - patch_size), 0)
    patch_x_min: int = max(min(patch_x_min, patch_x_max - patch_size), 0)

    return img[patch_y_min:patch_y_max, patch_x_min:patch_x_max]


def black_pad_patch(img: np.ndarray, roi: list[int], patch_size: int) -> np.ndarray:
    """
    function to black pad a patch given an image, a single ROI in the
    form [y_min, x_min, y_max, x_max] and the desired patch size
    """
    # unpack roi
    y_min, x_min, y_max, x_max = roi

    # initialize our patch as an empty array of zeros
    patch: np.ndarray = np.zeros((patch_size, patch_size), dtype=np.uint8)

    half_size: int = patch_size // 2

    # we need to handle cases where the ROI is larger than the patch size
    # check if the height of the roi exceeds the patch size
    if (y_max - y_min) > patch_size:
        # get the center coordinate
        y_center: int = (y_max + y_min) // 2

        # clip to the roi size
        y_min: int = y_center - half_size
        y_max: int = y_center + half_size

    # check if the width of the roi exceeds the patch size
    if (x_max - x_min) > patch_size:
        # get the center coordinate
        x_center: int = int((x_max + x_min) / 2)

        # clip to the roi size
        x_min: int = x_center - half_size
        x_max: int = x_center + half_size

    # this gives us the offset between the patch edge and the roi so we can center it
    patch_height: int = y_max - y_min
    patch_width: int = x_max - x_min
    half_y_diff: int = (patch_size - patch_height) // 2
    half_x_diff: int = (patch_size - patch_width) // 2

    # extract the roi from our original image and center it on the black patch array
    patch_contents: np.ndarray = img[y_min:y_max, x_min:x_max]
    patch[
        half_y_diff : half_y_diff + patch_height,
        half_x_diff : half_x_diff + patch_width,
    ] = patch_contents

    return patch
