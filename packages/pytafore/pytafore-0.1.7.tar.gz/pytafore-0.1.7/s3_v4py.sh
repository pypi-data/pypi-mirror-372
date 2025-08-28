# BEFORE RUNNING THIS SCRIPT, ENSURE THE VERSION HAS BEEN UPDATED
# THIS SCRIPT WILL NOT UPLOAD DUPLICATE DISTRIBUTIONS TO S3
# Upload the wheel file for the distribtuion to s3.

# THIS SCRIPT DOES NOT NEED TO BE SOURCED
#!/bin/bash

# Specify the S3 bucket
bucket="sagemaker-ds-dev1-churn/v4py"

# Find the most recent .whl file in the dist directory
file=$(ls -t dist/v4py-*.whl | head -n 1)

if [ -z "$file" ]
then
    echo "No .whl file found in dist directory"
    exit 1
fi

# Get the filename without the directory
filename=$(basename "$file")

# Check if the file already exists in the S3 bucket
output=$(aws s3 ls "s3://$bucket/$filename" 2>&1)

if [ -z "$output" ]
then
    # File does not exist in the S3 bucket, upload it
    aws s3 cp "$file" "s3://$bucket/"
    
    # Check if the upload was successful
    if [ $? -eq 0 ]
    then
        echo "File $file uploaded successfully to $bucket"
    else
        echo "File upload failed"
        exit 1
    fi
else
    # File already exists in the S3 bucket, print an error message and exit
    echo "Error: File $filename already exists in S3 bucket $bucket"
    exit 1
fi