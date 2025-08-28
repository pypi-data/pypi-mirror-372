# s3-lifecycle-delta

A small Python library to **compute and apply deltas** on AWS S3 lifecycle policies—especially focused on safe, declarative **storage class transitions**—with dry-run, validation, and minimal disruption.

## Problem

AWS S3 lifecycle policies are typically applied by overwriting the entire configuration. That makes automated changes brittle, error-prone, and risky when you only want to tweak transitions (e.g., change from `STANDARD` → `GLACIER` after 90 days) without accidentally deleting other rules.

This library:
- Introspects the current lifecycle policy
- Compares it to the desired policy (the "delta")
- Shows what would change (dry-run)
- Validates rules
- Applies only the intended change safely

## Features

- Declarative lifecycle policy definitions (via Python / JSON)
- Diff engine: detects rule adds / updates / deletes
- Safe apply with `dry-run`
- Validation of transition semantics (e.g., non-decreasing days)
- Idempotent behavior
- Pluggable for custom validation or rule logic

## Quickstart

### Install (editable for dev)

```bash
git clone https://github.com/your-org/s3-lifecycle-delta.git
cd s3-lifecycle-delta
pip install -e .
