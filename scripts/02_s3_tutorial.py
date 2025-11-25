#!/usr/bin/env python3
"""
S3 Tutorial - Learn AWS Simple Storage Service basics

This script demonstrates:
- Creating S3 buckets
- Uploading and downloading files
- Listing bucket contents
- Working with object metadata
- Setting bucket policies and permissions
- Versioning and lifecycle policies
"""

import boto3
import json
import os
import tempfile
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize S3 client and resource
s3_client = boto3.client('s3', region_name='us-east-2')
s3_resource = boto3.resource('s3', region_name='us-east-2')


def create_bucket(bucket_name):
    """Create an S3 bucket in us-east-2"""
    print(f"Creating bucket: {bucket_name}...")

    try:
        # Note: us-east-1 doesn't need LocationConstraint, but other regions do
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        print(f"✓ Bucket created: {bucket_name}")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✓ Bucket already exists: {bucket_name}")
            return True
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f"✗ Bucket name taken globally: {bucket_name}")
            return False
        else:
            print(f"Error creating bucket: {e}")
            raise


def upload_file(bucket_name, file_path, object_key=None):
    """Upload a file to S3 bucket"""
    if object_key is None:
        object_key = os.path.basename(file_path)

    print(f"\nUploading {file_path} to {bucket_name}/{object_key}...")

    try:
        # Upload with metadata
        s3_client.upload_file(
            file_path,
            bucket_name,
            object_key,
            ExtraArgs={
                'Metadata': {
                    'uploaded-by': 'tutorial-script',
                    'upload-date': datetime.now().isoformat()
                }
            }
        )
        print(f"✓ File uploaded successfully")
        return object_key

    except ClientError as e:
        print(f"Error uploading file: {e}")
        raise


def download_file(bucket_name, object_key, download_path=None):
    """Download a file from S3 bucket"""
    if download_path is None:
        download_path = f"/tmp/downloaded_{object_key}"

    print(f"\nDownloading {bucket_name}/{object_key} to {download_path}...")

    try:
        s3_client.download_file(bucket_name, object_key, download_path)
        print(f"✓ File downloaded successfully to {download_path}")
        return download_path

    except ClientError as e:
        print(f"Error downloading file: {e}")
        raise


def list_bucket_objects(bucket_name):
    """List all objects in a bucket"""
    print(f"\nListing objects in {bucket_name}:")

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        if 'Contents' not in response:
            print("  (empty bucket)")
            return []

        objects = []
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            print(f"  - {obj['Key']}")
            print(f"    Size: {size_kb:.2f} KB")
            print(f"    Last Modified: {obj['LastModified']}")
            objects.append(obj['Key'])

        return objects

    except ClientError as e:
        print(f"Error listing objects: {e}")
        raise


def get_object_metadata(bucket_name, object_key):
    """Get metadata for an object"""
    print(f"\nGetting metadata for {bucket_name}/{object_key}...")

    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)

        print(f"  Content-Type: {response.get('ContentType', 'N/A')}")
        print(f"  Content-Length: {response.get('ContentLength', 0)} bytes")
        print(f"  ETag: {response.get('ETag', 'N/A')}")
        print(f"  Last Modified: {response.get('LastModified', 'N/A')}")

        if 'Metadata' in response and response['Metadata']:
            print(f"  Custom Metadata:")
            for key, value in response['Metadata'].items():
                print(f"    {key}: {value}")

        return response

    except ClientError as e:
        print(f"Error getting metadata: {e}")
        raise


def enable_versioning(bucket_name):
    """Enable versioning on a bucket"""
    print(f"\nEnabling versioning on {bucket_name}...")

    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✓ Versioning enabled")

    except ClientError as e:
        print(f"Error enabling versioning: {e}")
        raise


def add_lifecycle_policy(bucket_name):
    """Add a lifecycle policy to transition objects to cheaper storage"""
    print(f"\nAdding lifecycle policy to {bucket_name}...")

    try:
        lifecycle_policy = {
            'Rules': [
                {
                    'ID': 'Move old objects to IA',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': ''},
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER'
                        }
                    ],
                    'NoncurrentVersionTransitions': [
                        {
                            'NoncurrentDays': 30,
                            'StorageClass': 'GLACIER'
                        }
                    ],
                    'NoncurrentVersionExpiration': {
                        'NoncurrentDays': 90
                    }
                }
            ]
        }

        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )

        print(f"✓ Lifecycle policy added:")
        print(f"  - Objects older than 30 days → STANDARD_IA")
        print(f"  - Objects older than 90 days → GLACIER")
        print(f"  - Old versions deleted after 90 days")

    except ClientError as e:
        print(f"Error adding lifecycle policy: {e}")
        raise


def make_object_public(bucket_name, object_key):
    """Make an object publicly readable"""
    print(f"\nMaking {bucket_name}/{object_key} publicly readable...")

    try:
        s3_client.put_object_acl(
            Bucket=bucket_name,
            Key=object_key,
            ACL='public-read'
        )

        # Generate public URL
        url = f"https://{bucket_name}.s3.us-east-2.amazonaws.com/{object_key}"
        print(f"✓ Object is now public")
        print(f"  URL: {url}")

        return url

    except ClientError as e:
        print(f"Error making object public: {e}")
        print("Note: You may need to disable 'Block all public access' in bucket settings")
        raise


def copy_object(source_bucket, source_key, dest_bucket, dest_key):
    """Copy an object within S3"""
    print(f"\nCopying {source_bucket}/{source_key} to {dest_bucket}/{dest_key}...")

    try:
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=dest_key
        )
        print(f"✓ Object copied successfully")

    except ClientError as e:
        print(f"Error copying object: {e}")
        raise


def delete_object(bucket_name, object_key):
    """Delete an object from S3"""
    print(f"\nDeleting {bucket_name}/{object_key}...")

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"✓ Object deleted")

    except ClientError as e:
        print(f"Error deleting object: {e}")
        raise


def delete_bucket(bucket_name):
    """Delete a bucket and all its contents"""
    print(f"\nDeleting bucket {bucket_name} and all contents...")

    try:
        # First, delete all objects
        bucket = s3_resource.Bucket(bucket_name)

        # Delete all object versions (if versioning is enabled)
        bucket.object_versions.all().delete()

        # Delete the bucket
        bucket.delete()
        print(f"✓ Bucket deleted: {bucket_name}")

    except ClientError as e:
        print(f"Error deleting bucket: {e}")
        raise


def create_sample_files(temp_dir):
    """Create sample files for testing"""
    files = []

    # Create a text file
    text_file = os.path.join(temp_dir, 'sample.txt')
    with open(text_file, 'w') as f:
        f.write("Hello from AWS S3 tutorial!\n")
        f.write(f"Created at: {datetime.now()}\n")
    files.append(text_file)

    # Create a JSON file
    json_file = os.path.join(temp_dir, 'data.json')
    with open(json_file, 'w') as f:
        json.dump({
            'tutorial': 'AWS S3',
            'timestamp': datetime.now().isoformat(),
            'items': ['item1', 'item2', 'item3']
        }, f, indent=2)
    files.append(json_file)

    return files


def main():
    """Main tutorial workflow"""
    print("="*60)
    print("AWS S3 Tutorial")
    print("="*60)

    # Generate unique bucket name (S3 bucket names are globally unique)
    account_id = boto3.client('sts').get_caller_identity()['Account']
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    bucket_name = f"tutorial-bucket-{account_id}-{timestamp}".lower()

    temp_dir = None

    try:
        # Step 1: Create bucket
        if not create_bucket(bucket_name):
            print("Failed to create bucket. Exiting.")
            return

        # Step 2: Create sample files
        temp_dir = tempfile.mkdtemp()
        print(f"\nCreating sample files in {temp_dir}...")
        sample_files = create_sample_files(temp_dir)
        print(f"✓ Created {len(sample_files)} sample files")

        # Step 3: Upload files
        for file_path in sample_files:
            upload_file(bucket_name, file_path)

        # Step 4: List bucket contents
        list_bucket_objects(bucket_name)

        # Step 5: Get metadata for first object
        get_object_metadata(bucket_name, 'sample.txt')

        # Step 6: Download a file
        download_file(bucket_name, 'sample.txt')

        # Step 7: Copy an object
        copy_object(bucket_name, 'sample.txt', bucket_name, 'sample-copy.txt')

        # Step 8: Enable versioning
        enable_versioning(bucket_name)

        # Step 9: Add lifecycle policy
        add_lifecycle_policy(bucket_name)

        # Step 10: Show final state
        print(f"\n{'='*60}")
        print("Final Bucket State")
        print(f"{'='*60}")
        list_bucket_objects(bucket_name)

        # Cleanup prompt
        print(f"\n{'='*60}")
        response = input("\nDo you want to delete the bucket and all contents? (yes/no): ").strip().lower()

        if response == 'yes':
            delete_bucket(bucket_name)
            print("\n✓ Cleanup complete!")
        else:
            print(f"\nBucket left running: {bucket_name}")
            print(f"To delete later, run: delete_bucket('{bucket_name}')")

    except Exception as e:
        print(f"\nError: {e}")
        print(f"\nTo clean up, you can run: delete_bucket('{bucket_name}')")
        raise

    finally:
        # Clean up temporary files
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
