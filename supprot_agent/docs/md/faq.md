# Frequently Asked Questions (FAQ)

## 1. Where is my data hosted?
By default, all user data and compute workloads are hosted in US-East (Virginia) with automatic failover to US-West (Oregon). Enterprise plan customers can choose European (Frankfurt / Dublin) or Asia-Pacific (Tokyo / Sydney) data residency options.

## 2. Is CloudPlatform SOC2 and GDPR compliant?
Yes. CloudPlatform is SOC2 Type II certified annually and complies fully with GDPR and CCPA data privacy frameworks. You can request our latest SOC2 report and Data Processing Agreement (DPA) under **Settings > Compliance**.

## 3. How do I invite team members?
1. Open your organization dashboard.
2. Go to **Organization Settings > Members & Teams**.
3. Click **Invite Member**, enter their email address, and select their role (`Viewer`, `Developer`, or `Admin`).
4. The user will receive an email invitation valid for 7 days.

## 4. Can I export my project data and logs?
Yes, you can export all project configuration, audit logs, and metrics:
- Via Dashboard: **Settings > Organization > Export Data (CSV/JSON/Zip archive)**.
- Via CLI: `cloudplatform export --format json --output ./backup.json`.
- Via API: `GET /v1/projects/{id}/export`.

## 5. What languages and frameworks are supported?
CloudPlatform natively supports:
- Node.js (v18, v20, v22)
- Python (3.10, 3.11, 3.12, 3.13, 3.14)
- Go (1.21+)
- Rust (1.75+)
- Java / Kotlin (OpenJDK 17, 21)
- Custom Docker containers via `Dockerfile` support.
