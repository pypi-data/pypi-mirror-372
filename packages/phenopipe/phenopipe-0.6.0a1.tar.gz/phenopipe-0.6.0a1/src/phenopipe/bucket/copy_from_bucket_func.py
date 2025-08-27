import os
import subprocess
from typing import Optional, List
import concurrent.futures
import warnings
from .ls_bucket_func import ls_bucket


def copy_from_bucket(
    files: str | List[str],
    target_folder: Optional[str] = None,
    nested: Optional[bool] = True,
    bucket_id: Optional[str] = None,
    verbose: Optional[bool] = True,
) -> None:
    """
    Copies file(s) from specified bucket into the target folder in enviroment workspace.

    :param files: Path to the file or a list of files to copy from bucket. It accepts a string pattern valid for gcloud storage ls command.
    :param target_folder: Path of the folder to copy the files to
    :param nested: Either to mirror folder structure onto the workspace
    :param bucket_id: The bucket id to copy the file from. Defaults to the environment variable 'WORKSPACE_BUCKET'.

    Example:
    --------
    copy_from_bucket('datasets/fitbit.csv')
    """

    if target_folder is None:
        target_folder = "."
    if bucket_id is None:
        bucket_id = os.getenv("WORKSPACE_BUCKET")

    if not (
        isinstance(files, str)
        or (isinstance(files, list) and all([isinstance(f, str) for f in files]))
    ):
        raise ValueError("The files parameter must be a string or list of string")

    if isinstance(files, str):
        files = ls_bucket(files, recursive=False, bucket_id=bucket_id, return_list=True)
    if nested:
        target_files = [f.replace(bucket_id, target_folder) for f in files]
    else:
        target_files = [
            f"{target_folder}/{f.split('/')[-1]}"
            if not f.endswith("/")
            else f"{target_folder}/{f.split('/')[-2]}"
            for f in files
        ]
    target_dirs = set(["/".join(t.split("/")[:-1]) for t in target_files])
    for target_dir in target_dirs:
        if target_dir != ".":
            os.makedirs(target_dir, exist_ok=True)

    if len(files) > 100 and not nested:
        warnings.warn(
            "More than 100 files/folders matched with files parameter and all will be copied in target folder since nested is set to False!"
        )

    def cp_file(file, target):
        if file.endswith("/"):
            subprocess.check_output(
                [
                    "gcloud",
                    "storage",
                    "cp",
                    "-r",
                    "--no-user-output-enabled",
                    "--gzip-in-flight-all",
                    file,
                    "/".join(target.split("/")[:-2]),
                ]
            )
        else:
            subprocess.check_output(
                [
                    "gcloud",
                    "storage",
                    "cp",
                    "--no-user-output-enabled",
                    "--gzip-in-flight-all",
                    file,
                    target,
                ]
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_file = {
            executor.submit(cp_file, f, t): (f, t) for f, t in zip(files, target_files)
        }
        for future in concurrent.futures.as_completed(future_to_file):
            f = future_to_file[future][0]
            t = future_to_file[future][1]
            try:
                future.result()
            except subprocess.CalledProcessError:
                warnings.warn(f"Failed to copy {f} to {t}")
            else:
                if verbose:
                    print(f"Succesfully copied {f} to {t}")
