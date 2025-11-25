# AWS CDK Examples - Infrastructure as Code

This directory contains AWS CDK (Cloud Development Kit) examples written in Python. These demonstrate **production-ready Infrastructure as Code** practices, in contrast to the boto3 scripts which are for learning AWS APIs.

## What is AWS CDK?

AWS CDK lets you define cloud infrastructure using familiar programming languages (Python, TypeScript, etc.) instead of YAML/JSON templates. It generates CloudFormation templates under the hood.

### Why CDK over boto3 scripts?

| Feature | boto3 Scripts | AWS CDK |
|---------|--------------|---------|
| Purpose | Learning & automation | Production infrastructure |
| Idempotency | Manual | Automatic |
| State Management | None | CloudFormation |
| Dependencies | Manual ordering | Automatic |
| Drift Detection | No | Yes (via CloudFormation) |
| Reusability | Limited | High (constructs) |
| Type Safety | No | Yes |
| Rollback | Manual | Automatic |

## Prerequisites

### 1. Install AWS CDK CLI

The CDK CLI is needed to deploy stacks. You have two options:

**Option A: Using npx (no installation needed):**
```bash
npx aws-cdk --version
```

**Option B: Install globally:**
```bash
npm install -g aws-cdk
cdk --version
```

### 2. Bootstrap your AWS account (one-time setup)

CDK needs to bootstrap your AWS account to create resources for deployments:

```bash
# Using npx
npx aws-cdk bootstrap aws://ACCOUNT-ID/us-east-2

# Or if installed globally
cdk bootstrap aws://ACCOUNT-ID/us-east-2
```

Replace `ACCOUNT-ID` with your AWS account ID, or use:
```bash
npx aws-cdk bootstrap --profile default
```

## Project Structure

```
cdk/
├── app.py           # CDK app entry point
├── vpc_stack.py     # VPC stack definition
├── cdk.json         # CDK configuration
└── README.md        # This file
```

## Available Stacks

### VPC Stack - Network Infrastructure

**File:** `vpc_stack.py`

Creates the same infrastructure as `scripts/01_vpc_tutorial.py` but using IaC:
- VPC with 10.0.0.0/16 CIDR
- 2 public subnets across different AZs
- 1 private isolated subnet
- Internet Gateway (automatic)
- Route tables and associations (automatic)
- Proper tagging

**Key differences from boto3 script:**
- Declarative (describe what you want, not how to create it)
- Automatic dependency management
- Idempotent (can apply multiple times safely)
- Rollback on failure
- Track changes over time

## CDK Commands

All commands should be run from the `cdk/` directory:

```bash
cd cdk
```

### 1. Synthesize CloudFormation Template

See what CloudFormation template CDK will generate:

```bash
npx aws-cdk synth
```

This is useful for:
- Reviewing infrastructure before deployment
- Debugging
- Understanding what CDK does under the hood

### 2. Show What Will Change (Diff)

Before deploying, see what will change:

```bash
npx aws-cdk diff
```

### 3. Deploy Stack

Deploy the infrastructure to AWS:

```bash
npx aws-cdk deploy

# Or deploy with auto-approval (skip confirmation)
npx aws-cdk deploy --require-approval never
```

This will:
- Create a CloudFormation stack
- Deploy all resources
- Show outputs (VPC ID, subnet IDs, etc.)
- Wait for completion

**Expected output:**
```
✅ TutorialVpcStack

Outputs:
TutorialVpcStack.VpcId = vpc-xxxxx
TutorialVpcStack.VpcCidr = 10.0.0.0/16
TutorialVpcStack.PublicSubnetIds = subnet-xxxxx,subnet-yyyyy
TutorialVpcStack.PrivateSubnetIds = subnet-zzzzz
```

### 4. List Stacks

See all deployed CDK stacks:

```bash
npx aws-cdk list
```

### 5. Destroy Stack (Cleanup)

Delete all resources created by the stack:

```bash
npx aws-cdk destroy

# With auto-approval
npx aws-cdk destroy --force
```

**⚠️ Warning:** This will delete all resources. Make sure you want to do this!

## Development Workflow

### Typical workflow for making infrastructure changes:

1. **Modify the stack** (edit `vpc_stack.py`)
2. **Synthesize** to check it compiles: `npx aws-cdk synth`
3. **Diff** to see what will change: `npx aws-cdk diff`
4. **Deploy** the changes: `npx aws-cdk deploy`
5. **Verify** in AWS Console or via outputs

### Hot reload during development:

```bash
npx aws-cdk watch
```

This automatically deploys changes as you edit files (for rapid iteration).

## Comparing boto3 vs CDK

### boto3 script (01_vpc_tutorial.py):
```python
# Imperative - tell AWS HOW to do it
vpc = ec2_resource.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "tutorial-vpc"}])
vpc.wait_until_available()
```

### CDK (vpc_stack.py):
```python
# Declarative - tell AWS WHAT you want
vpc = ec2.Vpc(
    self, "TutorialVpc",
    vpc_name="tutorial-vpc-cdk",
    ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
    max_azs=2,
)
```

**CDK benefits:**
- No manual waiting or state tracking
- Automatic dependency ordering
- Type-safe with IDE autocomplete
- Rollback on failure
- Can apply same code multiple times safely

## Cost Management

- VPC and related networking resources are **FREE**
- No charges for subnets, route tables, or Internet Gateways
- CloudFormation is free (just pay for resources it creates)

## Troubleshooting

### "CDK CLI not found"
```bash
# Install CDK CLI
npm install -g aws-cdk

# Or use npx (no installation)
npx aws-cdk --version
```

### "Need to perform AWS calls for account..."
You need to bootstrap CDK in your account:
```bash
npx aws-cdk bootstrap
```

### "Stack already exists"
If you want to update:
```bash
npx aws-cdk deploy
```

If you want to start fresh:
```bash
npx aws-cdk destroy
npx aws-cdk deploy
```

### Check CloudFormation Console
CDK uses CloudFormation under the hood. Check the CloudFormation console in AWS for detailed error messages:
- AWS Console → CloudFormation → Stacks → TutorialVpcStack → Events

## Best Practices

1. **Always run `cdk diff` before deploying** to preview changes
2. **Use `cdk synth` to validate** your code compiles
3. **Tag all resources** for cost tracking and organization
4. **Use constructs** (L2/L3) when available for simpler code
5. **Store `cdk.out/` in .gitignore** (already done)
6. **Version control your CDK code** (not the generated templates)
7. **Use separate stacks** for different environments (dev/staging/prod)

## Next Steps

### Add more stacks:
- EC2 instances with security groups
- RDS databases
- Lambda functions
- S3 buckets with policies

### Learn about:
- **CDK Constructs** - Reusable infrastructure components
- **CDK Aspects** - Apply cross-cutting concerns (tagging, security)
- **CDK Pipelines** - CI/CD for infrastructure
- **Testing** - Unit test your infrastructure code

## Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [CDK Workshop](https://cdkworkshop.com/)
- [CDK Patterns](https://cdkpatterns.com/)
- [AWS Construct Hub](https://constructs.dev/)

## Comparison: boto3 vs CDK Decision Guide

**Use boto3 scripts when:**
- Learning AWS services
- Operational automation (backups, cleanup, monitoring)
- Dynamic operations based on runtime data
- Quick prototypes or one-off tasks

**Use AWS CDK when:**
- Defining production infrastructure
- Need repeatability and consistency
- Want state management and drift detection
- Building infrastructure as part of CI/CD
- Managing infrastructure across environments
