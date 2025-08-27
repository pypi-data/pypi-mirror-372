import os
import subprocess
from typing import List, Optional


def ls_bucket(
    location: Optional[str] = None,
    recursive: Optional[bool] = False,
    bucket_id: Optional[str] = None,
    return_list: Optional[bool] = False,
) -> None | List[str]:
    """List the files in the given directory in the given bucket

    :param location: Path to folder in the bucket to list the files. Defaults to bucket itself.
    :param recursive: Either to search files recursively (this parameter is passed to gcloud util as -r flag)
    :param bucket_id: The bucket id to list the files from. Defaults to environment variable WORKSPACE_BUCKET.
    :returns: If return_list is set to true a list of files from the given directory is returned

    Example:
    --------
    ls_bucket('datasets')
    """
    if bucket_id is None:
        bucket_id = os.getenv("WORKSPACE_BUCKET")

    if location is not None and not isinstance(location, str):
        raise ValueError("The location parameter must be a string or None")
    cmd = "gcloud storage ls -r" if recursive else "gcloud storage ls"
    if location is None:
        cmd = f"{cmd} {bucket_id}"
    else:
        cmd = f"{cmd} {bucket_id}/{location}"

    res = subprocess.check_output(cmd, shell=True).decode("utf-8").split("\n")
    res = list(filter(lambda x: x != "", res))
    res = [r[:-1] if r.endswith(":") else r for r in res]

    if return_list:
        return res
    else:
        for r in res:
            print(r)
