# AWS Tutorial Scripts

A collection of hands-on tutorial scripts for learning AWS services. Each script is self-contained and includes detailed comments explaining the concepts.

## Prerequisites

- AWS account with appropriate permissions
- AWS credentials configured (via `aws configure` or environment variables)
- Python 3.13.9 with dependencies installed (`uv sync`)

## Running the Tutorials

Use `uv run` to execute scripts without manually activating the virtual environment:

```bash
# Run VPC tutorial
uv run python scripts/01_vpc_tutorial.py

# Run S3 tutorial
uv run python scripts/02_s3_tutorial.py

# Run EC2 tutorial
uv run python scripts/03_ec2_tutorial.py
```

## Tutorial Overview

### 01. VPC Tutorial - Networking Basics
**File:** `01_vpc_tutorial.py`

Learn AWS Virtual Private Cloud (VPC) fundamentals:
- Creating a VPC with custom CIDR blocks
- Setting up public and private subnets across availability zones
- Configuring Internet Gateways for public access
- Managing route tables and associations
- Tagging resources for organization
- Cleanup and resource management

**What you'll create:**
- 1 VPC (10.0.0.0/16)
- 2 public subnets in different AZs
- 1 private subnet
- 1 Internet Gateway
- Custom route tables

**Estimated cost:** FREE (VPCs and related resources are free)

---

### 02. S3 Tutorial - Object Storage
**File:** `02_s3_tutorial.py`

Learn AWS Simple Storage Service (S3) fundamentals:
- Creating and managing S3 buckets
- Uploading and downloading objects
- Working with object metadata
- Enabling versioning
- Configuring lifecycle policies
- Managing permissions and public access
- Copying and deleting objects

**What you'll create:**
- 1 S3 bucket with unique name
- Sample text and JSON files
- Lifecycle policy (30-day → IA, 90-day → Glacier)
- Versioning configuration

**Estimated cost:** ~$0.01/month for small test files (first 5GB free tier)

---

### 03. EC2 Tutorial - Compute Instances
**File:** `03_ec2_tutorial.py`

Learn AWS Elastic Compute Cloud (EC2) fundamentals:
- Creating EC2 key pairs for SSH access
- Setting up security groups with firewall rules
- Finding the latest AMIs
- Launching EC2 instances
- Using user data for automatic configuration
- Managing instance lifecycle (start, stop, terminate)
- Connecting to instances via SSH

**What you'll create:**
- 1 EC2 key pair (.pem file)
- 1 security group (SSH, HTTP, HTTPS access)
- 1 t2.micro instance (free tier eligible)
- Simple web server via user data

**Estimated cost:** FREE if on free tier, ~$0.01/hour for t2.micro otherwise

---

## Important Notes

### Cost Management
- All tutorials include cleanup prompts at the end
- Always clean up resources when done to avoid unexpected charges
- EC2 instances incur charges while running (even if stopped for EBS-backed instances)
- S3 storage has minimal cost but remember to delete buckets when done

### Security Warnings
- The EC2 tutorial creates security groups open to 0.0.0.0/0 for learning purposes
- In production, always restrict access to specific IP ranges
- Never commit .pem key files to version control
- The tutorials generate unique names to avoid conflicts

### Region Configuration
All tutorials use `us-east-2` (Ohio) region by default. This matches the project configuration.

### Cleanup
Each tutorial asks if you want to clean up resources at the end. If you skip cleanup:
- Resources remain in your AWS account
- You may incur charges (especially for EC2)
- You can manually clean up via AWS Console or re-run the cleanup functions

## Learning Path

Recommended order:
1. **VPC Tutorial** - Understand networking first, as EC2 instances run in VPCs
2. **S3 Tutorial** - Learn object storage (independent of networking)
3. **EC2 Tutorial** - Compute instances that tie everything together

## Troubleshooting

### Authentication Issues
```
Error: Unable to locate credentials
```
**Solution:** Run `aws configure` or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-2
```

### Permission Denied
```
Error: You are not authorized to perform this operation
```
**Solution:** Ensure your IAM user has appropriate permissions (EC2FullAccess, S3FullAccess, etc.)

### Resource Already Exists
```
Error: InvalidGroup.Duplicate or BucketAlreadyExists
```
**Solution:** Most tutorials handle this gracefully. If not, use unique names or clean up existing resources.

### EC2 Instance Won't Start
```
Error: InsufficientInstanceCapacity
```
**Solution:** Try a different availability zone or instance type.

## Next Steps

After completing these tutorials, explore:
- **RDS** - Managed databases
- **Lambda** - Serverless computing
- **CloudFormation** - Infrastructure as Code
- **IAM** - Identity and access management
- **CloudWatch** - Monitoring and logging

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS Free Tier](https://aws.amazon.com/free/)
