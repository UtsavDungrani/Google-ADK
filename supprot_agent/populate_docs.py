import os
import shutil
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak

DOCS_ROOT = Path(__file__).parent / "docs"
MD_DIR = DOCS_ROOT / "md"
HTML_DIR = DOCS_ROOT / "html"
PDF_DIR = DOCS_ROOT / "pdf"

MD_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Copy existing md files into docs/md/
for md_file in DOCS_ROOT.glob("*.md"):
    dest = MD_DIR / md_file.name
    shutil.copy2(md_file, dest)
    print(f"Copied {md_file.name} to docs/md/")

# Define rich content dictionaries for HTML and PDF generation
DOCS_DATA = [
    {
        "filename": "getting_started",
        "title": "CloudPlatform - Getting Started Guide",
        "sections": [
            {
                "heading": "Overview",
                "content": "CloudPlatform is an intelligent cloud orchestration and API workflow management platform designed for engineering and product teams. It allows teams to deploy serverless workflows, manage microservices, and automate customer pipelines with zero DevOps overhead."
            },
            {
                "heading": "Account Setup & Registration",
                "content": "1. Visit https://cloudplatform.example.com/signup\n2. Enter your work email, username, and secure password (minimum 8 characters, at least 1 number and 1 special symbol).\n3. Check your email inbox for a 6-digit verification code. Enter this code within 15 minutes.\n4. Set up Multi-Factor Authentication (MFA) using any standard authenticator app (Google Authenticator, Authy, or 1Password)."
            },
            {
                "heading": "System Requirements",
                "content": "• Operating Systems: Windows 10/11 (64-bit), macOS 12.0+ (Apple Silicon or Intel), Ubuntu 20.04+ / Debian 11+.\n• CLI Requirements: Node.js v18+ or Python 3.10+ (if using Python SDK).\n• Network: Outbound HTTPS (Port 443) access to api.cloudplatform.example.com."
            },
            {
                "heading": "Quickstart: Installing the CLI",
                "content": "Run the following command to install the CloudPlatform CLI globally via npm:\nnpm install -g @cloudplatform/cli\n\nOr with Python pip:\npip install cloudplatform-cli"
            },
            {
                "heading": "First Project Deployment",
                "content": "1. Authenticate your CLI: cloudplatform login\n2. Initialize your workspace: cloudplatform init my-project\n3. Deploy to production: cloudplatform deploy --env production"
            }
        ]
    },
    {
        "filename": "billing_and_subscriptions",
        "title": "CloudPlatform - Billing and Subscriptions",
        "sections": [
            {
                "heading": "Subscription Plans",
                "content": "1. Free Tier: $0/month. Up to 3 active projects, 50,000 monthly API calls, 1 GB storage. Community forum support with 48-hour response time.\n2. Pro Plan: $29/month per user (or $290/year paid annually). Unlimited projects, 1,000,000 monthly API calls, 50 GB storage, custom domain SSL. Priority email support with guaranteed 8-hour response SLA.\n3. Enterprise Plan: Custom pricing (contact sales@cloudplatform.example.com). Dedicated infrastructure, unlimited API calls, custom SLAs (99.99%), SSO / SAML integration, HIPAA & SOC2 compliance. Dedicated technical account manager & 24/7 phone/chat support with 15-minute response SLA."
            },
            {
                "heading": "Payment Methods & Invoicing",
                "content": "• We accept all major Credit/Debit cards (Visa, MasterCard, American Express), PayPal, and ACH wire transfers for Enterprise contracts.\n• Invoices are automatically generated on the 1st of each calendar month and emailed to the billing admin address.\n• Invoices can be downloaded anytime from Dashboard > Settings > Billing > Invoices (PDF)."
            },
            {
                "heading": "Cancellation and Refund Policy",
                "content": "• Cancellation: You can cancel your subscription at any time under Dashboard > Settings > Subscription > Cancel Plan. Your plan will remain active until the end of the current billing cycle.\n• Refund Policy: We offer a 14-day money-back guarantee for all first-time Pro plan purchases. If you are unsatisfied, request a refund within 14 days of purchase by submitting a support ticket.\n• Enterprise contracts are governed by individual Master Services Agreements (MSAs)."
            },
            {
                "heading": "Updating Payment Details",
                "content": "1. Log in to the CloudPlatform dashboard.\n2. Navigate to Organization Settings > Billing > Payment Methods.\n3. Click Add New Payment Method, enter new details, and select Set as Default.\n4. Old cards can be removed by clicking the trash icon next to the card."
            }
        ]
    },
    {
        "filename": "troubleshooting",
        "title": "CloudPlatform - Troubleshooting & Common Errors",
        "sections": [
            {
                "heading": "Error: 401 Unauthorized (AUTH_INVALID_TOKEN)",
                "content": "Symptoms: CLI commands or API requests fail with HTTP status code 401 Unauthorized and message 'Invalid or expired authorization token'.\n\nCause: Your session token has expired after 30 days of inactivity, or API Key was revoked or deleted in the admin dashboard.\n\nResolution Steps:\n1. Re-authenticate CLI: cloudplatform logout && cloudplatform login --force\n2. If using an API key in automated environments, generate a new secret key under Dashboard > Developer Settings > API Keys.\n3. Verify your environment variable CLOUDPLATFORM_API_KEY is loaded correctly."
            },
            {
                "heading": "Error: 429 Too Many Requests (RATE_LIMIT_EXCEEDED)",
                "content": "Symptoms: API returns 429 Too Many Requests.\n\nCause: You exceeded the rate limits of your plan (Free: 60 req/min, Pro: 600 req/min, Enterprise: Configurable/Unlimited).\n\nResolution Steps:\n1. Implement exponential backoff with jitter in your client application (e.g. retry after 1s, 2s, 4s).\n2. Check the Retry-After HTTP header returned by the API server.\n3. If higher throughput is needed, upgrade your plan under Billing > Change Plan."
            },
            {
                "heading": "Error: Deployment Timeout (DEPLOY_TIMEOUT_ERR)",
                "content": "Symptoms: Deployment hangs for more than 10 minutes and fails with 'Deployment timed out waiting for healthcheck'.\n\nCause: Application failed to bind to 0.0.0.0:$PORT, health check endpoint /healthz returned non-200 status, or heavy build step.\n\nResolution Steps:\n1. Ensure your server listens on 0.0.0.0 and uses $PORT (default 8080).\n2. Test healthcheck locally: curl -I http://localhost:8080/healthz\n3. Check deployment logs with: cloudplatform logs --deployment <DEPLOYMENT_ID> --tail 100"
            },
            {
                "heading": "Resetting Your Password / Locked Account",
                "content": "If your account is locked due to multiple failed login attempts:\n1. Go to https://cloudplatform.example.com/forgot-password\n2. Enter your account email address.\n3. Follow the reset link sent to your email within 30 minutes.\n4. If you do not receive the email, check spam or contact support."
            }
        ]
    },
    {
        "filename": "api_reference",
        "title": "CloudPlatform - API Reference and Integration Guide",
        "sections": [
            {
                "heading": "Base URL and Authentication",
                "content": "Base URL: https://api.cloudplatform.example.com/v1\n\nAuthentication: Authenticate all requests using Authorization Bearer token header:\nAuthorization: Bearer YOUR_API_SECRET_KEY"
            },
            {
                "heading": "Endpoint: List Projects (GET /projects)",
                "content": "Method: GET /projects\nQuery Parameters: limit (integer, default: 20, max: 100), status (active, archived)\n\nResponse Example:\n{\n  \"status\": \"success\",\n  \"data\": [\n    {\n      \"id\": \"proj_99812\",\n      \"name\": \"ecommerce-backend\",\n      \"status\": \"active\",\n      \"created_at\": \"2026-01-15T09:00:00Z\"\n    }\n  ]\n}"
            },
            {
                "heading": "Endpoint: Trigger Deployment (POST /projects/{project_id}/deploy)",
                "content": "Method: POST /projects/{project_id}/deploy\nRequest Body:\n{\n  \"branch\": \"main\",\n  \"commit_sha\": \"a1b2c3d4\",\n  \"environment\": \"production\"\n}\n\nResponse Example:\n{\n  \"status\": \"success\",\n  \"deployment_id\": \"dep_456789\",\n  \"build_url\": \"https://dashboard.cloudplatform.example.com/deployments/dep_456789\"\n}"
            },
            {
                "heading": "Webhooks & Event Subscriptions",
                "content": "Register webhooks to receive real-time notifications for deployment events:\n• Supported events: deployment.started, deployment.succeeded, deployment.failed\n• Webhook payloads include HMAC-SHA256 signature in X-CloudPlatform-Signature header for verification."
            }
        ]
    },
    {
        "filename": "faq",
        "title": "CloudPlatform - Frequently Asked Questions (FAQ)",
        "sections": [
            {
                "heading": "Where is my data hosted?",
                "content": "By default, all user data and compute workloads are hosted in US-East (Virginia) with automatic failover to US-West (Oregon). Enterprise plan customers can choose European (Frankfurt / Dublin) or Asia-Pacific (Tokyo / Sydney) data residency options."
            },
            {
                "heading": "Is CloudPlatform SOC2 and GDPR compliant?",
                "content": "Yes. CloudPlatform is SOC2 Type II certified annually and complies fully with GDPR and CCPA data privacy frameworks. You can request our latest SOC2 report and Data Processing Agreement (DPA) under Settings > Compliance."
            },
            {
                "heading": "How do I invite team members?",
                "content": "1. Open your organization dashboard.\n2. Go to Organization Settings > Members & Teams.\n3. Click Invite Member, enter their email address, and select their role (Viewer, Developer, or Admin).\n4. The user will receive an email invitation valid for 7 days."
            },
            {
                "heading": "Can I export my project data and logs?",
                "content": "Yes, you can export all project configuration, audit logs, and metrics:\n• Via Dashboard: Settings > Organization > Export Data (CSV/JSON/Zip archive).\n• Via CLI: cloudplatform export --format json --output ./backup.json\n• Via API: GET /v1/projects/{id}/export"
            },
            {
                "heading": "What languages and frameworks are supported?",
                "content": "CloudPlatform natively supports:\n• Node.js (v18, v20, v22)\n• Python (3.10, 3.11, 3.12, 3.13, 3.14)\n• Go (1.21+)\n• Rust (1.75+)\n• Java / Kotlin (OpenJDK 17, 21)\n• Custom Docker containers via Dockerfile support."
            }
        ]
    }
]

# 1. Generate HTML Files
for doc in DOCS_DATA:
    html_path = HTML_DIR / f"{doc['filename']}.html"
    sections_html = ""
    for sec in doc["sections"]:
        content_p = "".join(f"<p>{line}</p>" for line in sec["content"].split("\n") if line.strip())
        sections_html += f"""
        <section class="doc-section">
            <h2>{sec['heading']}</h2>
            <div class="section-content">
                {content_p}
            </div>
        </section>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc['title']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #2d3748; max-width: 800px; margin: 0 auto; padding: 2rem; }}
        h1 {{ color: #1a202c; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }}
        h2 {{ color: #2b6cb0; margin-top: 1.5rem; }}
        p {{ margin-bottom: 0.75rem; }}
        .doc-section {{ margin-bottom: 2rem; padding: 1rem; background: #f7fafc; border-left: 4px solid #3182ce; border-radius: 4px; }}
        code {{ background: #edf2f7; padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
    </style>
</head>
<body>
    <header>
        <h1>{doc['title']}</h1>
    </header>
    <main>
        {sections_html}
    </main>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML: {html_path.name}")


# 2. Generate PDF Files using ReportLab
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#1a365d'),
    spaceAfter=12
)
heading_style = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontSize=13,
    leading=16,
    textColor=colors.HexColor('#2b6cb0'),
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True
)
body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#2d3748'),
    spaceAfter=8
)

for doc in DOCS_DATA:
    pdf_path = PDF_DIR / f"{doc['filename']}.pdf"
    doc_template = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = [
        Paragraph(doc['title'], title_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e0'), spaceAfter=14)
    ]
    
    for i, sec in enumerate(doc["sections"]):
        story.append(Paragraph(sec['heading'], heading_style))
        for line in sec['content'].split('\n'):
            if line.strip():
                # Escape XML entities for ReportLab Paragraph
                escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(escaped, body_style))
        story.append(Spacer(1, 8))
        
        # Add a page break for multi-page demonstration if there are many sections
        if i == 2 and len(doc["sections"]) > 3:
            story.append(PageBreak())
            
    doc_template.build(story)
    print(f"Generated PDF: {pdf_path.name}")

print("All documents generated successfully!")
