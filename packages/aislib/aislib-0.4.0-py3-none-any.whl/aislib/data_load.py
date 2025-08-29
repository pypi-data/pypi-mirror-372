from collections.abc import Callable, Iterable
from pathlib import Path

import numpy as np

from .misc_utils import get_logger

logger = get_logger(__name__)


def iter_loadtxt(
    filename: str,
    delimiter: str = " ",
    skiprows: int = 0,
    dtype: type = int,
    custom_splitter: Callable = None,
) -> np.ndarray:
    """
    Used to quickly and memory-efficiently load a file into a np array.

    :param filename: Which file to load arrays from.
    :param delimiter: What to split on.
    :param skiprows: Number of rows to skip in beginning.
    :param dtype: What type to cast loaded elements to.
    :param custom_splitter: Callable to do custom splits on the loaded lines.
    :return: np.array of loaded data.
    """

    def iter_func():
        with open(filename) as infile:
            for _ in range(skiprows):
                next(infile)
            for line in infile:
                if custom_splitter:
                    line = custom_splitter(line)
                else:
                    line = line.rstrip().split(delimiter)

                for item in line:
                    yield dtype(item)

        iter_loadtxt.row_length = len(line)

    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, iter_loadtxt.row_length))
    return data


def load_np_packbits_from_folder(
    folder: Path, input_height: int, dtype: type = bool, verbose: bool = False
) -> tuple[np.ndarray, list[str]]:
    """
    Note that it is faster to allocate np arrays to a python list first and then
    convert that to a np.array, as adding iteratively to a np array seems to
    introduce some continuous memory allocation overhead.

    :param folder: Which folder to load packbits from.
    :param input_height: Expected height of samples.
    :param input_width: Expected width of samples.
    :param dtype: Which data type to cast samples to while loading.
    :param verbose: If ``True``, log results while loading.
    :return: A tuple of loaded arrays IDs (file names).
    """
    obs_array = []
    ids_list = []

    if verbose:
        logger.info("Loading samples from %s", folder)
    for idx, raw_obs_path in enumerate(Path(folder).iterdir()):
        unpacked_obs = np.unpackbits(np.load(raw_obs_path)).astype(dtype)
        reshaped_obs = unpacked_obs.reshape(input_height, -1)

        obs_array.append(reshaped_obs)
        ids_list.append(raw_obs_path.stem)

        if verbose:
            if (idx + 1) % 2000 == 0:
                logger.info("Loaded %d observations into memory.", idx + 1)

    logger.info("All samples loaded.")
    return np.array(obs_array), ids_list


def load_np_arrays_from_folder(folder: Path, dtype: type = float) -> np.ndarray:
    """
    Loads numpy arrays from a given folder.

    :param folder: Which folder to load arrays from.
    :param dtype: Data type to cast samples to.
    :return: Array of elements loaded from the folder.
    """
    obs_array = np.array([np.load(i).astype(dtype) for i in folder.iterdir()])
    return obs_array


def get_labels_from_folder(
    folder: Path, delimiter: str = "_", position: int = 1
) -> list[str]:
    """
    Used to extract labels from files in folder, assuming the labels are in the
    filename.

    :param folder: Path to folder which to load fnames from.
    :param delimiter: What to split on.
    :param position: What position we expect the label to be in.
    :return: A list of labels in the order Python's .iterdir() goes over folder.
    """

    label_list = []
    for obs_file in Path(folder).iterdir():
        label = obs_file.stem.split(delimiter)[position:]
        label = "_".join(label)
        label_list.append(label)

    return label_list


def get_labels_from_iterable(
    iterable: Iterable[str], delimiter: str = "_", position: int = 1
) -> list[str]:
    """
    Used to extract labels from iterable of strings, assumes labels are in the
    iterable elements.

    :param iterable: A Python iterable.
    :param delimiter: What to split on.
    :param position: What position we expect the label to be in.
    :return: A list of labels in the order of the iterable.
    """
    label_list = []

    for item in iterable:
        label = item.split(delimiter)[position:]
        label = "_".join(label)
        label_list.append(label)

    return label_list


def files_to_train_test_incides(
    input_path: Path, percent_train: float = 0.9, sample_suffix=".npy"
) -> tuple[np.ndarray, np.ndarray]:
    no_obs = 0
    for i in input_path.iterdir():
        if i.suffix == sample_suffix:
            no_obs += 1

    indices = np.random.permutation(no_obs)
    no_train = int(percent_train * no_obs)
    train_idxs, test_idxs = indices[:no_train], indices[no_train:]

    return train_idxs, test_idxs
