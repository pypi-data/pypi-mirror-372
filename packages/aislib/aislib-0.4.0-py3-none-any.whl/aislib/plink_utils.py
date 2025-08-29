from pathlib import Path

import numpy as np
from sklearn.preprocessing import OneHotEncoder

from aislib.misc_utils import get_logger

logger = get_logger(__name__, False)


def get_plink_raw_encoder():
    enc = OneHotEncoder(categories="auto")
    enc.fit(np.array([0, 1, 2, 9]).reshape(-1, 1))

    return enc


def plink_raw_to_one_hot(
    raw_fpath: Path,
    output_folder: str | Path,
    encoder: OneHotEncoder,
    log_interval: int = 2000,
) -> None:
    """
    Takes in a file where each line is a SNP profile for an individual. Converts
    the sequence to one-hot vectors.  Currently uses a hard-coded mapping,
    [0, 1, 2, 9] for the SNPs, but easy to add as an argument later.

    :param raw_fpath: Recoded file path.
    :param output_folder: Where to save the one hot encoded sequences.
    :param encoder: Encoder object to encode the sequences with.
    :param label_fpath: Path to label file for adding class to fname.
    :param log_interval: Interval of processed observations to log no processed.
    """

    with open(str(raw_fpath)) as infile:
        # skip header
        infile.readline()
        for idx, line in enumerate(infile):
            line = line.strip().split(" ")

            sample_id = line[1]

            genotype = line[6:]
            genotype = ["9" if i == "NA" else i for i in genotype]
            genotype = np.array(genotype, dtype=np.uint8)

            encoded_sequence = encoder.transform(genotype.reshape(-1, 1)).toarray().T
            encoded_sequence = encoded_sequence.astype(np.uint8)

            # check that one hot is correct format
            assert (encoded_sequence.sum(axis=0) != 1).sum() == 0

            cur_outpath = output_folder / f"{sample_id}.npy"
            if cur_outpath.exists():
                raise FileExistsError(
                    f"It seems that there are duplicated IIDs in {raw_fpath},"
                    f"please make sure they are unique to avoid "
                    f"overwriting sample arrays."
                )

            np.save(cur_outpath, encoded_sequence)

            if idx % log_interval == 0:
                logger.info("Converted %d samples to final format.", idx)
