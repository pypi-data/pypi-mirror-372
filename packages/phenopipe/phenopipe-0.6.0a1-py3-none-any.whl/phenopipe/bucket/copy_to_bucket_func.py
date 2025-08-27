import os
import glob
import subprocess
import warnings
import concurrent.futures
from typing import List, Optional


def copy_to_bucket(
    files: str | List[str],
    target_folder: Optional[str] = None,
    nested: Optional[bool] = True,
    bucket_id: Optional[str] = None,
    verbose: Optional[bool] = True,
) -> None:
    """Copies file(s) from enviroment workspace to designated bucket folder

    :param files: Path to file in the environment or a list of files to copy to bucket. Python glob patterns or a list can be used to copy multiple files
    :param target_folder: folder path to copy the file
    :param nested: Either to mirror folder structure onto the bucket
    :param bucket_id: The bucket id to copy the file to. Defaults to environment variable WORKSPACE_BUCKET

    Example:
    --------
    copy_from_bucket('fitbit.csv', 'datasets')
    """
    if bucket_id is None:
        bucket_id = os.getenv("WORKSPACE_BUCKET")

    if isinstance(files, str):
        files = glob.glob(files)
    if len(files) == 0:
        raise ValueError("No matching files with given pattern")

    if nested:
        target_files = [
            "/".join(filter(None, [bucket_id, target_folder, f])) for f in files
        ]
    else:
        target_files = [
            "/".join(filter(None, [bucket_id, target_folder, f.split("/")[-1]]))
            for f in files
        ]

    def cp_file(file, target):
        if os.path.isdir(file):
            subprocess.check_output(
                [
                    "gcloud",
                    "storage",
                    "cp",
                    "-r",
                    "--no-user-output-enabled",
                    "--gzip-in-flight-all",
                    file,
                    target,
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
