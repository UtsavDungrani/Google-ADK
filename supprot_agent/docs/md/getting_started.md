# Getting Started Guide

Welcome to the CloudPlatform Documentation!

## Overview
CloudPlatform is an intelligent cloud orchestration and API workflow management platform designed for engineering and product teams. It allows teams to deploy serverless workflows, manage microservices, and automate customer pipelines with zero DevOps overhead.

## Account Setup & Registration
1. Visit https://cloudplatform.example.com/signup
2. Enter your work email, username, and secure password (minimum 8 characters, at least 1 number and 1 special symbol).
3. Check your email inbox for a 6-digit verification code. Enter this code within 15 minutes.
4. Set up Multi-Factor Authentication (MFA) using any standard authenticator app (Google Authenticator, Authy, or 1Password).

## System Requirements
- **Operating Systems**: Windows 10/11 (64-bit), macOS 12.0+ (Apple Silicon or Intel), Ubuntu 20.04+ / Debian 11+.
- **CLI Requirements**: Node.js v18+ or Python 3.10+ (if using Python SDK).
- **Network**: Outbound HTTPS (Port 443) access to `api.cloudplatform.example.com`.

## Quickstart: Installing the CLI
Run the following command to install the CloudPlatform CLI globally:
```bash
npm install -g @cloudplatform/cli
```
Or with Python pip:
```bash
pip install cloudplatform-cli
```

## First Project Deployment
1. Authenticate your CLI:
   ```bash
   cloudplatform login
   ```
2. Initialize your workspace:
   ```bash
   cloudplatform init my-project
   ```
3. Deploy to production:
   ```bash
   cloudplatform deploy --env production
   ```
