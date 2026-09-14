"""
Enterprise Multilingual Call Center Agent.
Google ADK Compatible Agent designed for QA evaluation against real contact center benchmarks.
Handles Customer Support, Billing/Finance inquiries, Technical Assistance, and Sales consultations.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.tools import ToolContext

MODEL_NAME = os.environ.get("CALLCENTER_MODEL", "gemini-3.5-flash-lite")


# -------------------------------------------------------------
# Call Center Tools
# -------------------------------------------------------------

def verify_customer_identity(
    account_number: str,
    verification_pin_or_code: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Verifies customer identity and ensures authentication before disclosing sensitive billing or account data.
    """
    return {
        "status": "VERIFIED",
        "account_number": account_number,
        "security_clearance": "Standard Tier",
        "message": "Customer identity successfully verified."
    }


def lookup_billing_and_payment(
    customer_id: str,
    invoice_or_order_ref: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves account billing details, active balances, withdrawal statuses, or payment transfer instructions.
    """
    return {
        "status": "ACTIVE",
        "customer_id": customer_id,
        "reference": invoice_or_order_ref or "CURRENT_PERIOD",
        "currency": "USD/EUR/PLN",
        "payment_options": ["Standard SEPA Wire", "Official Portal Checkout"],
        "compliance_warning": "Never use unverified third-party screen sharing tools to authorize financial transactions."
    }


def log_support_ticket(
    issue_summary: str,
    department: str = "Technical Support",
    priority: str = "Medium",
    contact_phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates an official contact center ticket for technical follow-ups or supervisor reviews.
    """
    return {
        "status": "LOGGED",
        "ticket_id": f"TKT-CC-{abs(hash(issue_summary)) % 100000:05d}",
        "department": department,
        "priority": priority,
        "sla_hours": 24,
        "notes": "Follow-up scheduled with senior specialist."
    }


def schedule_callback(
    customer_name: str,
    preferred_date: str,
    preferred_time: str,
    topic: str
) -> Dict[str, Any]:
    """
    Schedules an official callback with a manager, financial advisor, or product sales specialist.
    """
    return {
        "status": "CONFIRMED",
        "customer_name": customer_name,
        "scheduled_slot": f"{preferred_date} at {preferred_time}",
        "topic": topic
    }


CALLCENTER_AGENT_INSTRUCTIONS = """
You are a Senior Contact Center Representative assisting customers across multiple domains (Customer Care, Billing/Invoicing, Account Management, and Sales consultations).

### Key Rules & Guidelines:
1. **Professional Demeanor & Empathy**:
   - Greet the customer warmly and politely.
   - Listen attentively to customer frustrations or technical problems.
   - Never use aggressive, coercive, or misleading sales tactics.

2. **Security & Financial Safeguards**:
   - When handling fund withdrawals, account activations, or payments, always emphasize official, secure company channels.
   - Never instruct or encourage customers to install remote access utilities (such as AnyDesk or TeamViewer) to authorize transactions on personal banking apps (such as Cash App).
   - Clarify fees, contract terms, and trial conditions with complete transparency.

3. **Multilingual Fluency**:
   - Communicate fluently in the customer's preferred language (English, Russian, Polish, French, German, Spanish, Portuguese).
   - Maintain appropriate cultural politeness and clear phrasing.

4. **Issue Resolution & Next Steps**:
   - Offer clear, actionable resolutions.
   - If technical difficulties or regional restrictions prevent immediate completion, log a ticket or schedule a prompt supervisor callback.
"""

root_agent = Agent(
    name="enterprise_callcenter_agent",
    model=MODEL_NAME,
    description="Enterprise Multilingual Contact Center Agent for Customer Support, Billing, Finance, and Sales.",
    instruction=CALLCENTER_AGENT_INSTRUCTIONS,
    tools=[
        verify_customer_identity,
        lookup_billing_and_payment,
        log_support_ticket,
        schedule_callback
    ]
)

agent = root_agent
