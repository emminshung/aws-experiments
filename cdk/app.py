#!/usr/bin/env python3
"""
AWS CDK App - Entry Point

This is the main entry point for the CDK application.
It instantiates the CDK app and creates stacks.
"""

import aws_cdk as cdk
from vpc_stack import TutorialVpcStack

# Create the CDK app
app = cdk.App()

# Create the VPC stack
TutorialVpcStack(
    app,
    "TutorialVpcStack",
    description="Tutorial VPC with public and private subnets",
    env=cdk.Environment(
        region="us-east-2",
    ),
)

# Synthesize the CloudFormation template
app.synth()
