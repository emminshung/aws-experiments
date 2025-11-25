"""
VPC Stack - Infrastructure as Code using AWS CDK

This stack creates the same VPC infrastructure as the boto3 tutorial (01_vpc_tutorial.py),
but using AWS CDK for proper Infrastructure as Code practices.

What this creates:
- VPC with CIDR block 10.0.0.0/16
- 2 public subnets in different availability zones
- 1 private subnet
- Internet Gateway
- Route tables with proper associations
- All resources tagged appropriately
"""

from aws_cdk import (
    Stack,
    Tags,
    aws_ec2 as ec2,
)
from constructs import Construct


class TutorialVpcStack(Stack):
    """
    CDK Stack that creates a VPC with public and private subnets.

    This demonstrates Infrastructure as Code best practices:
    - Declarative infrastructure definition
    - Automatic dependency management
    - Idempotent deployments
    - State management via CloudFormation
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public and private subnets
        # CDK automatically creates:
        # - Internet Gateway
        # - NAT Gateways (if private subnets specified)
        # - Route tables and associations
        # - DNS settings
        vpc = ec2.Vpc(
            self,
            "TutorialVpc",
            vpc_name="tutorial-vpc-cdk",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,  # Use 2 availability zones
            nat_gateways=0,  # No NAT gateways to keep it simple and free
            subnet_configuration=[
                # Public subnets (with Internet Gateway access)
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,  # Creates 10.0.0.0/24, 10.0.1.0/24
                ),
                # Private subnets (isolated, no internet access)
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,  # Creates 10.0.10.0/24
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        # Add tags to the VPC
        Tags.of(vpc).add("Name", "tutorial-vpc-cdk")
        Tags.of(vpc).add("Purpose", "tutorial")
        Tags.of(vpc).add("ManagedBy", "CDK")

        # Export VPC ID for use by other stacks (if needed)
        self.vpc = vpc

        # Add outputs for easy reference
        from aws_cdk import CfnOutput

        CfnOutput(
            self,
            "VpcId",
            value=vpc.vpc_id,
            description="VPC ID",
            export_name="TutorialVpcId",
        )

        CfnOutput(
            self,
            "VpcCidr",
            value=vpc.vpc_cidr_block,
            description="VPC CIDR block",
        )

        # Output public subnet IDs
        public_subnet_ids = [subnet.subnet_id for subnet in vpc.public_subnets]
        CfnOutput(
            self,
            "PublicSubnetIds",
            value=",".join(public_subnet_ids),
            description="Public subnet IDs",
        )

        # Output private subnet IDs
        private_subnet_ids = [subnet.subnet_id for subnet in vpc.isolated_subnets]
        CfnOutput(
            self,
            "PrivateSubnetIds",
            value=",".join(private_subnet_ids),
            description="Private subnet IDs",
        )
