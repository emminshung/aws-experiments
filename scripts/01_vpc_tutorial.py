#!/usr/bin/env python3
"""
VPC Tutorial - Learn AWS Virtual Private Cloud basics

This script demonstrates:
- Creating a VPC with CIDR block
- Creating public and private subnets
- Setting up an Internet Gateway
- Configuring route tables
- Tagging resources for easy identification
"""

import boto3
from botocore.exceptions import ClientError

# Initialize EC2 client
ec2 = boto3.client('ec2', region_name='us-east-2')
ec2_resource = boto3.resource('ec2', region_name='us-east-2')


def create_vpc():
    """Create a VPC with a /16 CIDR block"""
    print("Creating VPC...")

    try:
        vpc = ec2_resource.create_vpc(CidrBlock='10.0.0.0/16')
        vpc.create_tags(Tags=[{"Key": "Name", "Value": "tutorial-vpc"}])
        vpc.wait_until_available()

        # Enable DNS hostname support
        ec2.modify_vpc_attribute(
            VpcId=vpc.id,
            EnableDnsHostnames={'Value': True}
        )

        print(f"✓ VPC created: {vpc.id}")
        return vpc

    except ClientError as e:
        print(f"Error creating VPC: {e}")
        raise


def create_internet_gateway(vpc):
    """Create and attach an Internet Gateway to the VPC"""
    print("\nCreating Internet Gateway...")

    try:
        igw = ec2_resource.create_internet_gateway()
        igw.create_tags(Tags=[{"Key": "Name", "Value": "tutorial-igw"}])
        vpc.attach_internet_gateway(InternetGatewayId=igw.id)

        print(f"✓ Internet Gateway created and attached: {igw.id}")
        return igw

    except ClientError as e:
        print(f"Error creating Internet Gateway: {e}")
        raise


def create_subnet(vpc, cidr, availability_zone, name, is_public=False):
    """Create a subnet in the specified availability zone"""
    print(f"\nCreating {'public' if is_public else 'private'} subnet: {name}...")

    try:
        subnet = vpc.create_subnet(
            CidrBlock=cidr,
            AvailabilityZone=availability_zone
        )
        subnet.create_tags(Tags=[{"Key": "Name", "Value": name}])

        # Auto-assign public IPs for public subnets
        if is_public:
            ec2.modify_subnet_attribute(
                SubnetId=subnet.id,
                MapPublicIpOnLaunch={'Value': True}
            )

        print(f"✓ Subnet created: {subnet.id} ({cidr})")
        return subnet

    except ClientError as e:
        print(f"Error creating subnet: {e}")
        raise


def create_route_table(vpc, name, igw=None, subnet=None):
    """Create a route table and optionally add routes"""
    print(f"\nCreating route table: {name}...")

    try:
        route_table = vpc.create_route_table()
        route_table.create_tags(Tags=[{"Key": "Name", "Value": name}])

        # Add route to Internet Gateway if provided (for public subnets)
        if igw:
            route_table.create_route(
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw.id
            )
            print(f"  ✓ Added route to Internet Gateway")

        # Associate with subnet if provided
        if subnet:
            route_table.associate_with_subnet(SubnetId=subnet.id)
            print(f"  ✓ Associated with subnet {subnet.id}")

        print(f"✓ Route table created: {route_table.id}")
        return route_table

    except ClientError as e:
        print(f"Error creating route table: {e}")
        raise


def list_vpc_resources(vpc_id):
    """List all resources associated with the VPC"""
    print(f"\n{'='*60}")
    print("VPC Resources Summary")
    print(f"{'='*60}")

    # Get VPC details
    vpc = ec2_resource.Vpc(vpc_id)
    print(f"\nVPC: {vpc_id}")
    print(f"  CIDR Block: {vpc.cidr_block}")
    print(f"  State: {vpc.state}")

    # List subnets
    print(f"\nSubnets:")
    for subnet in vpc.subnets.all():
        name = next((tag['Value'] for tag in subnet.tags if tag['Key'] == 'Name'), 'N/A')
        print(f"  - {subnet.id}: {name} ({subnet.cidr_block}) in {subnet.availability_zone}")

    # List route tables
    print(f"\nRoute Tables:")
    for rt in vpc.route_tables.all():
        name = next((tag['Value'] for tag in rt.tags if tag['Key'] == 'Name'), 'Main')
        print(f"  - {rt.id}: {name}")
        for route in rt.routes:
            if route.destination_cidr_block != vpc.cidr_block:
                dest = route.gateway_id or route.nat_gateway_id or 'local'
                print(f"    → {route.destination_cidr_block} -> {dest}")

    # List Internet Gateways
    print(f"\nInternet Gateways:")
    for igw in vpc.internet_gateways.all():
        name = next((tag['Value'] for tag in igw.tags if tag['Key'] == 'Name'), 'N/A')
        print(f"  - {igw.id}: {name}")


def cleanup_vpc(vpc_id):
    """
    Clean up all VPC resources
    Note: This is provided for learning purposes. Be careful when deleting resources!
    """
    print(f"\n{'='*60}")
    print("CLEANUP - Deleting VPC and associated resources")
    print(f"{'='*60}")

    try:
        vpc = ec2_resource.Vpc(vpc_id)

        # Delete subnets
        print("\nDeleting subnets...")
        for subnet in vpc.subnets.all():
            subnet.delete()
            print(f"  ✓ Deleted subnet: {subnet.id}")

        # Detach and delete Internet Gateways
        print("\nDeleting Internet Gateways...")
        for igw in vpc.internet_gateways.all():
            vpc.detach_internet_gateway(InternetGatewayId=igw.id)
            igw.delete()
            print(f"  ✓ Deleted Internet Gateway: {igw.id}")

        # Delete route tables (except main)
        print("\nDeleting route tables...")
        for rt in vpc.route_tables.all():
            if not rt.associations_attribute or not any(a.get('Main') for a in rt.associations_attribute):
                rt.delete()
                print(f"  ✓ Deleted route table: {rt.id}")

        # Delete VPC
        print("\nDeleting VPC...")
        vpc.delete()
        print(f"✓ Deleted VPC: {vpc_id}")

        print("\n✓ Cleanup complete!")

    except ClientError as e:
        print(f"Error during cleanup: {e}")
        raise


def main():
    """Main tutorial workflow"""
    print("="*60)
    print("AWS VPC Tutorial")
    print("="*60)

    vpc_id = None

    try:
        # Step 1: Create VPC
        vpc = create_vpc()
        vpc_id = vpc.id

        # Step 2: Create Internet Gateway
        igw = create_internet_gateway(vpc)

        # Step 3: Create subnets
        # Public subnet in us-east-2a
        public_subnet_1 = create_subnet(
            vpc,
            cidr='10.0.1.0/24',
            availability_zone='us-east-2a',
            name='tutorial-public-subnet-1',
            is_public=True
        )

        # Public subnet in us-east-2b (for high availability)
        public_subnet_2 = create_subnet(
            vpc,
            cidr='10.0.2.0/24',
            availability_zone='us-east-2b',
            name='tutorial-public-subnet-2',
            is_public=True
        )

        # Private subnet in us-east-2a
        private_subnet_1 = create_subnet(
            vpc,
            cidr='10.0.10.0/24',
            availability_zone='us-east-2a',
            name='tutorial-private-subnet-1',
            is_public=False
        )

        # Step 4: Create route tables
        # Public route table with internet access
        public_rt = create_route_table(
            vpc,
            name='tutorial-public-rt',
            igw=igw,
            subnet=public_subnet_1
        )

        # Associate second public subnet with public route table
        public_rt.associate_with_subnet(SubnetId=public_subnet_2.id)
        print(f"  ✓ Associated public route table with {public_subnet_2.id}")

        # Private route table (no internet access)
        private_rt = create_route_table(
            vpc,
            name='tutorial-private-rt',
            subnet=private_subnet_1
        )

        # Step 5: Display summary
        list_vpc_resources(vpc_id)

        # Prompt for cleanup
        print(f"\n{'='*60}")
        response = input("\nDo you want to clean up these resources? (yes/no): ").strip().lower()

        if response == 'yes':
            cleanup_vpc(vpc_id)
        else:
            print(f"\nResources left running. VPC ID: {vpc_id}")
            print("To clean up later, run: cleanup_vpc('{vpc_id}')")

    except Exception as e:
        print(f"\nError: {e}")
        if vpc_id:
            print(f"\nTo clean up, you can run: cleanup_vpc('{vpc_id}')")
        raise


if __name__ == "__main__":
    main()
