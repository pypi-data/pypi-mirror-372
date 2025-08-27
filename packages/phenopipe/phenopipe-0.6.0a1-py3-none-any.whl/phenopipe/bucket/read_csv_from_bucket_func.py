import os
from typing import Optional
import polars as pl
from .ls_bucket_func import ls_bucket
from .copy_from_bucket_func import copy_from_bucket


def read_csv_from_bucket(
    files: str,
    lazy: Optional[bool] = True,
    cache: Optional[bool] = True,
    bucket_id: Optional[str] = None,
    verbose: Optional[bool] = True,
    **kwargs,
) -> pl.DataFrame:
    """Copies and reads csv file(s) from bucket

    :param file: the name of the file. Python globbing patterns can be used to read multiple files into one dataframe
    :param lazy: Either to read or scan csv file. Check polars documentation for this behaviour. Defaults to True.
    :param cache: Either to check a copy of the file(s) in working environment and use those if available.
    :param bucket_id: The bucket id to read the file from. Defaults to environment variable WORKSPACE_BUCKET.
    :param **kwargs: any other kwargs are passed to polars read/scan functions
    :returns: Polars Dataframe is returned. Read might be set to lazy to scan the csv instead of reading. Check polars documentation for this behaviour.

    Example:
    --------
    df = read_csv_from_bucket(files = 'fitbit.csv')
    """

    if bucket_id is None:
        bucket_id = os.getenv("WORKSPACE_BUCKET")

    file_list = ls_bucket(files, bucket_id=bucket_id, return_list=True, recursive=True)
    file_list = list(filter(lambda x: not x.endswith("/"), file_list))

    if len(file_list) == 0:
        raise ValueError("No mathching files with given pattern")

    exts = [f.split(".")[-1] for f in file_list]
    if len(set(exts)) > 1 or "csv" not in exts:
        raise ValueError(
            "read_csv_from_bucket accepts a csv path or a pattern matching csv files."
        )

    if not (
        cache
        and all([os.path.isfile(f.replace(bucket_id, "bucket_io")) for f in file_list])
    ):
        copy_from_bucket(
            files=files,
            target_folder="bucket_io",
            bucket_id=bucket_id,
            nested=True,
            verbose=verbose,
        )

    if lazy:
        return pl.scan_csv("bucket_io/" + files, **kwargs)
    else:
        return pl.read_csv("bucket_io/" + files, **kwargs)
