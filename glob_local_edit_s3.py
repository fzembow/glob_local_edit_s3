import argparse
import boto3
import os
import subprocess

from botocore.exceptions import NoCredentialsError
from colorama import Fore, Style
from pathlib import PurePath


# Which command to edit files with
EDITOR = os.environ.get("EDITOR", "code")


def print_status_text(action, bucket, key):
    print(
        f"{Fore.LIGHTBLACK_EX}{action}: s3://{bucket}/{Style.BRIGHT}{key}{Style.NORMAL}{Style.RESET_ALL}"
    )


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Update Google Analytics tags in HTML files in an S3 bucket."
    )
    parser.add_argument(
        "bucket_and_path",
        type=str,
        help='Bucket name and path filter in the format "some.bucket.name/some/glob/*/pattern.html"',
    )
    args = parser.parse_args()

    bucket, path = args.bucket_and_path.split("/", 1)
    update_files_in_bucket(bucket, path)


def update_files_in_bucket(bucket, pattern):
    try:
        s3 = boto3.client("s3")

        # List all objects (files) in the bucket
        response = s3.list_objects_v2(Bucket=bucket)

        while "Contents" in response:
            # Iterate over each object and download for manual update
            for obj in response["Contents"]:
                key = obj["Key"]
                if not PurePath(key).match(pattern):
                    continue

                needs_update = input(
                    f"Do you want to update s3://{bucket}/{key}? (y/N): "
                )
                if needs_update == "" or needs_update.lower() == "n":
                    print_status_text("Skipping file", bucket, key)
                    continue

                edit_file_locally(s3, bucket, key)

            # Check if there are more objects to retrieve
            if "NextContinuationToken" in response:
                response = s3.list_objects_v2(
                    Bucket=bucket, ContinuationToken=response["NextContinuationToken"]
                )
            else:
                break

    except NoCredentialsError:
        print("Unable to access AWS credentials. Please configure your credentials.")

    except Exception as e:
        print(f"Error updating files in bucket: {bucket}\n{str(e)}")


def edit_file_locally(s3, bucket, key):
    # Create a temporary directory
    temp_dir = "/tmp/ga_update"
    os.makedirs(temp_dir, exist_ok=True)

    # Download the file to the temporary directory
    local_filename = key.replace("/", "_")
    local_file = os.path.join(temp_dir, local_filename)
    with open(local_file, "wb") as file:
        s3.download_fileobj(bucket, key, file)

    local_last_modified = os.path.getmtime(local_file)

    # Open the file in editor for manual update
    subprocess.Popen([EDITOR, local_file])

    input("\nPress Enter when done editing...\n")

    # Get the last modified time of the local file after editing
    updated_local_last_modified = os.path.getmtime(local_file)

    # Compare the last modified times
    if local_last_modified != updated_local_last_modified:
        # Retrieve the content-type of the original object
        head_response = s3.head_object(Bucket=bucket, Key=key)
        content_type = head_response["ContentType"]

        # Upload the modified file back to S3
        s3.upload_file(
            local_file,
            bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        print_status_text("Updated file", bucket, key)
    else:
        print_status_text("No changes made, skipping file", bucket, key)

    # Remove the temporary file
    os.remove(local_file)


if __name__ == "__main__":
    main()
