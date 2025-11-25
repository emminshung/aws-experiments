#!/usr/bin/env python3
"""
EC2 Tutorial - Learn AWS Elastic Compute Cloud basics

This script demonstrates:
- Creating EC2 key pairs
- Creating security groups
- Launching EC2 instances
- Managing instance state (start, stop, terminate)
- Using user data for initialization
- Connecting to instances
- Working with tags and filters
"""

import boto3
import time
import os
from botocore.exceptions import ClientError

# Initialize EC2 client and resource
ec2_client = boto3.client('ec2', region_name='us-east-2')
ec2_resource = boto3.resource('ec2', region_name='us-east-2')


def create_key_pair(key_name):
    """Create an EC2 key pair for SSH access"""
    print(f"Creating key pair: {key_name}...")

    try:
        response = ec2_client.create_key_pair(KeyName=key_name)

        # Save private key to file
        key_file = f"{key_name}.pem"
        with open(key_file, 'w') as f:
            f.write(response['KeyMaterial'])

        # Set proper permissions (readable only by owner)
        os.chmod(key_file, 0o400)

        print(f"✓ Key pair created and saved to {key_file}")
        print(f"  Keep this file safe - you'll need it to SSH into instances")
        return key_name, key_file

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
            print(f"✓ Key pair already exists: {key_name}")
            return key_name, f"{key_name}.pem"
        else:
            print(f"Error creating key pair: {e}")
            raise


def create_security_group(group_name, description, vpc_id=None):
    """Create a security group with SSH and HTTP access"""
    print(f"\nCreating security group: {group_name}...")

    try:
        # Create security group
        if vpc_id:
            response = ec2_client.create_security_group(
                GroupName=group_name,
                Description=description,
                VpcId=vpc_id
            )
        else:
            response = ec2_client.create_security_group(
                GroupName=group_name,
                Description=description
            )

        sg_id = response['GroupId']

        # Add inbound rules
        # Allow SSH from anywhere (in production, restrict this!)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH from anywhere'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP from anywhere'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS from anywhere'}]
                }
            ]
        )

        print(f"✓ Security group created: {sg_id}")
        print(f"  Inbound rules:")
        print(f"    - SSH (22) from 0.0.0.0/0")
        print(f"    - HTTP (80) from 0.0.0.0/0")
        print(f"    - HTTPS (443) from 0.0.0.0/0")

        return sg_id

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            # Get existing security group ID
            response = ec2_client.describe_security_groups(GroupNames=[group_name])
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"✓ Security group already exists: {sg_id}")
            return sg_id
        else:
            print(f"Error creating security group: {e}")
            raise


def get_latest_amazon_linux_ami():
    """Get the latest Amazon Linux 2023 AMI ID"""
    print("\nFinding latest Amazon Linux 2023 AMI...")

    try:
        response = ec2_client.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['al2023-ami-2023*-x86_64']},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'architecture', 'Values': ['x86_64']},
            ]
        )

        # Sort by creation date and get the latest
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)

        if images:
            ami_id = images[0]['ImageId']
            ami_name = images[0]['Name']
            print(f"✓ Found AMI: {ami_id} ({ami_name})")
            return ami_id
        else:
            print("No Amazon Linux AMI found, using default")
            # Fallback to a known AMI (this may be outdated)
            return 'ami-0c55b159cbfafe1f0'

    except ClientError as e:
        print(f"Error finding AMI: {e}")
        raise


def launch_instance(ami_id, instance_type, key_name, security_group_id, name):
    """Launch an EC2 instance"""
    print(f"\nLaunching EC2 instance: {name}...")
    print(f"  AMI: {ami_id}")
    print(f"  Instance Type: {instance_type}")

    # User data script to run on first boot
    user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# Create a simple web page
cat > /var/www/html/index.html <<EOF
<html>
<head><title>EC2 Tutorial Instance</title></head>
<body>
<h1>Hello from EC2!</h1>
<p>Instance ID: $(ec2-metadata --instance-id | cut -d " " -f 2)</p>
<p>Availability Zone: $(ec2-metadata --availability-zone | cut -d " " -f 2)</p>
<p>Instance Type: $(ec2-metadata --instance-type | cut -d " " -f 2)</p>
</body>
</html>
EOF
"""

    try:
        instances = ec2_resource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=[security_group_id],
            UserData=user_data_script,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': name},
                        {'Key': 'Purpose', 'Value': 'tutorial'},
                    ]
                }
            ]
        )

        instance = instances[0]
        print(f"✓ Instance launched: {instance.id}")
        print(f"  Waiting for instance to be running...")

        # Wait for instance to be running
        instance.wait_until_running()

        # Reload to get the latest state
        instance.reload()

        print(f"✓ Instance is running!")
        print(f"  Instance ID: {instance.id}")
        print(f"  Public IP: {instance.public_ip_address}")
        print(f"  Private IP: {instance.private_ip_address}")
        print(f"  State: {instance.state['Name']}")

        return instance

    except ClientError as e:
        print(f"Error launching instance: {e}")
        raise


def get_instance_status(instance_id):
    """Get detailed status of an instance"""
    print(f"\nGetting status for instance {instance_id}...")

    try:
        instance = ec2_resource.Instance(instance_id)

        print(f"  State: {instance.state['Name']}")
        print(f"  Instance Type: {instance.instance_type}")
        print(f"  Public IP: {instance.public_ip_address}")
        print(f"  Private IP: {instance.private_ip_address}")
        print(f"  Availability Zone: {instance.placement['AvailabilityZone']}")
        print(f"  Launch Time: {instance.launch_time}")

        # Get tags
        if instance.tags:
            print(f"  Tags:")
            for tag in instance.tags:
                print(f"    {tag['Key']}: {tag['Value']}")

        return instance

    except ClientError as e:
        print(f"Error getting instance status: {e}")
        raise


def stop_instance(instance_id):
    """Stop a running instance"""
    print(f"\nStopping instance {instance_id}...")

    try:
        instance = ec2_resource.Instance(instance_id)
        instance.stop()

        print(f"  Waiting for instance to stop...")
        instance.wait_until_stopped()

        print(f"✓ Instance stopped")
        return True

    except ClientError as e:
        print(f"Error stopping instance: {e}")
        raise


def start_instance(instance_id):
    """Start a stopped instance"""
    print(f"\nStarting instance {instance_id}...")

    try:
        instance = ec2_resource.Instance(instance_id)
        instance.start()

        print(f"  Waiting for instance to start...")
        instance.wait_until_running()

        instance.reload()
        print(f"✓ Instance started")
        print(f"  Public IP: {instance.public_ip_address}")
        return True

    except ClientError as e:
        print(f"Error starting instance: {e}")
        raise


def terminate_instance(instance_id):
    """Terminate an instance"""
    print(f"\nTerminating instance {instance_id}...")

    try:
        instance = ec2_resource.Instance(instance_id)
        instance.terminate()

        print(f"  Waiting for instance to terminate...")
        instance.wait_until_terminated()

        print(f"✓ Instance terminated")
        return True

    except ClientError as e:
        print(f"Error terminating instance: {e}")
        raise


def list_instances():
    """List all instances with their states"""
    print("\nListing all EC2 instances:")

    try:
        instances = ec2_resource.instances.all()

        instance_list = []
        for instance in instances:
            name = 'N/A'
            if instance.tags:
                name = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'), 'N/A')

            print(f"  - {instance.id}: {name}")
            print(f"    State: {instance.state['Name']}")
            print(f"    Type: {instance.instance_type}")
            print(f"    Public IP: {instance.public_ip_address or 'N/A'}")

            instance_list.append(instance.id)

        if not instance_list:
            print("  (no instances found)")

        return instance_list

    except ClientError as e:
        print(f"Error listing instances: {e}")
        raise


def cleanup_resources(instance_id, key_name, security_group_id):
    """Clean up all created resources"""
    print(f"\n{'='*60}")
    print("CLEANUP - Deleting resources")
    print(f"{'='*60}")

    try:
        # Terminate instance
        if instance_id:
            terminate_instance(instance_id)

        # Delete security group
        if security_group_id:
            print(f"\nDeleting security group {security_group_id}...")
            ec2_client.delete_security_group(GroupId=security_group_id)
            print(f"✓ Security group deleted")

        # Delete key pair
        if key_name:
            print(f"\nDeleting key pair {key_name}...")
            ec2_client.delete_key_pair(KeyName=key_name)
            print(f"✓ Key pair deleted")

            # Delete local key file
            key_file = f"{key_name}.pem"
            if os.path.exists(key_file):
                os.remove(key_file)
                print(f"✓ Local key file deleted: {key_file}")

        print("\n✓ Cleanup complete!")

    except ClientError as e:
        print(f"Error during cleanup: {e}")
        raise


def main():
    """Main tutorial workflow"""
    print("="*60)
    print("AWS EC2 Tutorial")
    print("="*60)

    key_name = f"tutorial-key-{int(time.time())}"
    security_group_name = f"tutorial-sg-{int(time.time())}"
    instance_id = None
    security_group_id = None
    key_file = None

    try:
        # Step 1: Create key pair
        key_name, key_file = create_key_pair(key_name)

        # Step 2: Create security group
        security_group_id = create_security_group(
            security_group_name,
            "Tutorial security group for EC2 instances"
        )

        # Step 3: Get latest Amazon Linux AMI
        ami_id = get_latest_amazon_linux_ami()

        # Step 4: Launch instance
        instance = launch_instance(
            ami_id=ami_id,
            instance_type='t3.micro',  # Free tier eligible
            key_name=key_name,
            security_group_id=security_group_id,
            name='tutorial-instance'
        )
        instance_id = instance.id

        # Step 5: Show connection instructions
        print(f"\n{'='*60}")
        print("Connection Instructions")
        print(f"{'='*60}")
        print(f"\nTo connect to your instance via SSH:")
        print(f"  ssh -i {key_file} ec2-user@{instance.public_ip_address}")
        print(f"\nTo view the web page (wait ~2 minutes for setup):")
        print(f"  http://{instance.public_ip_address}")

        # Step 6: Wait a bit, then show status
        print(f"\nWaiting 10 seconds before showing status...")
        time.sleep(10)
        get_instance_status(instance_id)

        # Step 7: List all instances
        list_instances()

        # Cleanup prompt
        print(f"\n{'='*60}")
        response = input("\nDo you want to clean up all resources? (yes/no): ").strip().lower()

        if response == 'yes':
            cleanup_resources(instance_id, key_name, security_group_id)
        else:
            print(f"\nResources left running:")
            print(f"  Instance ID: {instance_id}")
            print(f"  Security Group: {security_group_id}")
            print(f"  Key Name: {key_name}")
            print(f"  Key File: {key_file}")
            print(f"\nIMPORTANT: Don't forget to terminate resources to avoid charges!")
            print(f"To clean up later, run:")
            print(f"  cleanup_resources('{instance_id}', '{key_name}', '{security_group_id}')")

    except Exception as e:
        print(f"\nError: {e}")
        if instance_id or security_group_id or key_name:
            print(f"\nTo clean up, you can run:")
            print(f"  cleanup_resources('{instance_id}', '{key_name}', '{security_group_id}')")
        raise


if __name__ == "__main__":
    main()
