
# s3-lifecycle

![PyPI](https://img.shields.io/pypi/v/s3-lifecycle?label=PyPI&color=blue)
![TestPyPI](https://img.shields.io/badge/TestPyPI-v0.1.1-orange)

A small Python library to **compute and apply policies** on AWS S3 lifecycle policies—especially focused on safe, declarative **storage class transitions**—with dry-run, validation, and minimal disruption.

---

## Problem

AWS S3 lifecycle policies are typically applied by overwriting the entire configuration. That makes automated changes brittle, error-prone, and risky when you only want to tweak transitions (e.g., change from `STANDARD` → `GLACIER` after 90 days) without accidentally deleting other rules.

This library:

- Introspects the current lifecycle policy
- Compares it to the desired policy
- Shows what would change (dry-run)
- Validates rules
- Applies only the intended change safely

---

## Features

- Declarative lifecycle policy definitions (via Python / JSON)
- Diff engine: detects rule adds / updates / deletes
- Safe apply with `dry-run`
- Validation of transition semantics (e.g., non-decreasing days)
- Idempotent behavior
- Pluggable for custom validation or rule logic

---

## Quickstart

### 1. Set Up AWS Environment

Before using `s3-lifecycle`, configure AWS credentials.

#### a) Using AWS CLI

```bash
aws configure
```

Provide:

```
AWS Access Key ID [None]: <YOUR_ACCESS_KEY>
AWS Secret Access Key [None]: <YOUR_SECRET_KEY>
Default region name [None]: <YOUR_DEFAULT_REGION>  # e.g., us-east-1
Default output format [None]: json
```

#### b) Using environment variables

**Linux/macOS:**

```bash
export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY>
export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_KEY>
export AWS_DEFAULT_REGION=us-east-1
```

**Windows (PowerShell):**

```powershell
setx AWS_ACCESS_KEY_ID "<YOUR_ACCESS_KEY>"
setx AWS_SECRET_ACCESS_KEY "<YOUR_SECRET_KEY>"
setx AWS_DEFAULT_REGION "us-east-1"
```

> ⚠️ Ensure your IAM user has `s3:GetLifecycleConfiguration` and `s3:PutLifecycleConfiguration` permissions.

---

### 2. Install the Library

```bash
git clone https://github.com/FernandoOLI/s3-lifecycle.git
cd s3-lifecycle
pip install -e .
```

---

### 3. Basic Usage

```python
from s3_lifecycle import LifecyclePolicy, LifecycleManager, validate_policy, ValidationError, ApplyError

# Example lifecycle policy dictionary
desired_policy_dict = {
    "Rules": [
        {
            "ID": "archive-log",
            "Filter": {"Prefix": "logs/"},
            "Status": "Enabled",
            "Transitions": [
                {"Days": 300, "StorageClass": "GLACIER"},
                {"Days": 390, "StorageClass": "DEEP_ARCHIVE"}
            ],
            "Expiration": {'Days': 500},
            "NoncurrentVersionTransitions": [
                {"NoncurrentDays": 30, "StorageClass": "GLACIER"},
                {"NoncurrentDays": 150, "StorageClass": "DEEP_ARCHIVE"}
            ],
            "NoncurrentVersionExpiration": {'NoncurrentDays': 700}
        }
    ]
}

def main():
    try:
        # Create and validate policy
        policy = LifecyclePolicy.from_dict(desired_policy_dict)
        validate_policy(policy)

        bucket = "lifecycle-management-bucket"

        # Initialize manager (will create boto3 client if not passed)
        manager = LifecycleManager()

        # Compute input vs current S3 bucket policy
        diff_result = manager.compute(bucket, policy)

        # Apply changes safely (dry_run=True prints summary only)
        manager.apply(bucket, diff_result, policy, dry_run=True)

    except ValidationError as ve:
        print(f"Policy validation error: {ve}, details: {ve.details}")
    except ApplyError as ae:
        print(f"Failed to apply lifecycle policy: {ae}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

---

### 4. Notes

- `dry_run=True` only prints changes; no modifications are applied.  
- Always validate IAM permissions before running `apply`.  
- Supports declarative JSON/Python policy definitions for safe incremental updates.

---

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/my-feature`)  
3. Make your changes  
4. Run tests and ensure coverage  
5. Submit a Pull Request  

---

## License

MIT License