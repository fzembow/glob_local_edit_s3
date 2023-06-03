# Glob local edit s3

This script allows making updates to files stored in an Amazon S3 bucket, downloading files matching a glob pattern locally, letting you modify them in your editor, and then automatically upload changed files back to the bucket.

It's helpful for when you need to make a difficult-to-automate tweak to a bunch of files at once. You could of course use `aws s3 sync` to make a local copy of the bucket contents, but then you're probably downloading a whole lot of data that you don't need.

## Prerequisites

- Python 3.9+
- AWS credentials configured on the machine and available in the environment
- Pipenv

## Usage

Clone the repository or download the script.py file.

Install the required dependencies and set up your environment by running the following command:

```shell
pipenv install
pipenv shell
```

Modify the AWS credentials on your machine or configure them using environment variables as per the Boto3 documentation.

Run the script using the following command:

```shell
python glob_local_edit_s3.py "<bucket-name>/<path-filter>"
```

Replace <bucket-name> with the name of your S3 bucket and <path-filter> with the glob filter pattern for the files you want to update. The filter pattern should be relative to the root of the bucket and can include wildcards (e.g., projects/\*.html).

The script will download each matching file to a temporary directory. It will then open the file in Visual Studio Code, allowing you to manually modify the contents.

After you make the necessary changes in Visual Studio Code and save the file, the script will automatically upload the updated file back to the S3 bucket, preserving the original content-type.

## Configuration

The script uses the `code` command to open the HTML files in Visual Studio Code. Make sure Visual Studio Code is installed and available in your system's PATH. If you'd like to use another editor, you can specify it using the `EDITOR` environment variable.
