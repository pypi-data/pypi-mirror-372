import os
import subprocess
from typing import List, Optional


def remove_from_bucket(
    files: str | List[str],
    recursive: Optional[bool] = False,
    bucket_id: Optional[str] = None,
) -> None:
    """Removes the file(s) from the bucket

    :param files: Path to file(s) or a list of files to remove.
    :param recursive: Either to remove files recursively (this parameter is passed to gcloud util as -r flag)
    :param bucket_id: The bucket id to remove the file from. Defaults to environment variable WORKSPACE_BUCKET.

    Example:
    --------
    remove_from_bucket('datasets/fitbit.csv')
    """
    if bucket_id is None:
        bucket_id = os.getenv("WORKSPACE_BUCKET")

    if not (
        isinstance(files, str)
        or (isinstance(files, list) and all([isinstance(f, str) for f in files]))
    ):
        raise ValueError("The files parameter must be a string or list of string")

    cmd = (
        ["gcloud", "storage", "rm", "-r"] if recursive else ["gcloud", "storage", "rm"]
    )
    if isinstance(files, str):
        subprocess.check_output(cmd + [f"{bucket_id}/{files}"])
    else:
        for file in files:
            subprocess.Popen(cmd + [f"{bucket_id}/{file}"])
