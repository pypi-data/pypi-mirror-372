import os
import shutil
from typing import Optional
import polars as pl
from .copy_to_bucket_func import copy_to_bucket


def write_csv_to_bucket(
    dat: pl.DataFrame,
    file: str,
    chunk_number: Optional[int] = None,
    bucket_id: Optional[str] = None,
) -> None:
    """Writes the given file to the given bucket location

    :param dat: Polars DataFrame to write to the bucket
    :param file: Path to write the file
    :param chunk_number: the number of chunks to divide the dataframe for large files
    :param bucket_id: The bucket id to write the file. Defaults to environment variable WORKSPACE_BUCKET.

    Example:
    --------
    write_to_bucket(fitbit_dat, 'datasets/fitbit.csv')
    """

    if file.endswith("/"):
        file = file[:-1]
    if len(file.split("/")) == 1:
        target_folder = None
    else:
        target_folder = "/".join(file.split("/")[:-1])
    file_name = file.split("/")[-1]
    if not os.path.isdir("bucket_io/tmp"):
        os.makedirs("bucket_io/tmp")
    if not chunk_number:
        dat.write_csv(f"bucket_io/tmp/{file_name}")
        copy_to_bucket(
            f"bucket_io/tmp/{file_name}",
            target_folder=target_folder,
            nested=False,
            bucket_id=bucket_id,
        )
        os.remove(f"bucket_io/tmp/{file_name}")
    else:
        n = len(str(dat.shape[0]))
        try:
            os.makedirs(f"bucket_io/tmp/{file}")
        except FileExistsError:
            shutil.rmtree(f"bucket_io/tmp/{file}")
            os.makedirs(f"bucket_io/tmp/{file}")
        dat = dat.with_row_index().with_columns((pl.col("index") % chunk_number))
        for i, s in enumerate(dat.partition_by("index")):
            s.drop("index").write_csv(
                f"bucket_io/tmp/{file}/{file_name}_{str(i).zfill(n)}.csv"
            )
        copy_to_bucket(
            f"bucket_io/tmp/{file}",
            target_folder=target_folder,
            nested=False,
            bucket_id=bucket_id,
        )
        shutil.rmtree(f"bucket_io/tmp/{file}")
