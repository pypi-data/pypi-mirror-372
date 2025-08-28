# THIS SCRIPT NEEDS TO BE RUN AT THE START OF EACH PROJECT
# IT HANDLES THE RETRIEVAL OF THE V4PY PACKAGE FROM S3 AND INSTALLS IT
#!/bin/bash

# Specify the S3 bucket, package name, and desired version
bucket="sagemaker-ds-dev1-churn"
package_name="v4py"
desired_version=""

# Confirm AWSCLI is installed
sudo yum install awscli -y

# If a version is specified, find the file for that version
if [ -n "$desired_version" ]
then
    file_path=$(aws s3 ls "s3://$bucket/$package_name/" --recursive | grep "$desired_version" | awk '{print $4}')
else
    # If no version is specified, find the most recent version
    file_path=$(aws s3 ls "s3://$bucket/$package_name/" --recursive | awk '{print $4}' | sort -V | tail -n 1)
fi

if [ -z "$file_path" ]
then
    echo "No $package_name file found in S3 bucket $bucket"
    exit 1
fi

# Download the file from S3
aws s3 cp "s3://$bucket/$file_path" .

# Check if the download was successful
if [ $? -eq 0 ]
then
    echo "File $file_path downloaded successfully from $bucket"
else
    echo "File download failed"
    exit 1
fi

# Extract the version from the file name
version=$(basename $file_path | cut -d'-' -f2)

# Echo the version
echo "Installing version $version of $package_name"

# Install the wheel file using pip
pip install "./$(basename $file_path)" --force-reinstall

# Check if the installation was successful
if [ $? -eq 0 ]
then
    echo "File $(basename $file_path) installed successfully"
else
    echo "File installation failed"
    exit 1
fi

# Remove the wheel file
rm "./$(basename $file_path)"

# Check if the file was removed successfully
if [ $? -eq 0 ]
then
    echo "File $(basename $file_path) removed successfully"
else
    echo "File removal failed"
    exit 1
fi