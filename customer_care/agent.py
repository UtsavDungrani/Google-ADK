"""
Post-Purchase Customer Care Master Agent (customer_care)
Unifies Multi-Agent Orchestration, LSTM Neural Sequence Sentiment Analysis,
Fine-Tuned LoRA/SFT Domain Adaptation, Hybrid RAG Diagnostics, and Large-Scale (99k+) Kaggle Orders.
"""

import os
import re
import warnings
import logging
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)


from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

# Import Care Tools
try:
    from .care_tools import (
        lookup_order,
        track_shipment,
        predict_delivery_delay_risk,
        get_ecommerce_dataset_kpis,
        check_warranty_status,
        file_warranty_claim,
        check_return_eligibility,
        create_rma_return,
        issue_courtesy_credit,
        escalate_to_human_supervisor,
        get_customer_session_summary,
        create_support_ticket,
        get_ticket_status,
        list_customer_tickets,
        vendor_reply_ticket,
        close_support_ticket
    )
    from .rag_tools import (
        search_product_guides,
        troubleshoot_product_issue,
        index_customer_care_docs
    )
    from .lstm_sentiment import run_lstm_sentiment_analysis
    from .finetune_adapter import apply_finetuned_care_adapter
except (ImportError, ValueError):
    from care_tools import (
        lookup_order,
        track_shipment,
        predict_delivery_delay_risk,
        get_ecommerce_dataset_kpis,
        check_warranty_status,
        file_warranty_claim,
        check_return_eligibility,
        create_rma_return,
        issue_courtesy_credit,
        escalate_to_human_supervisor,
        get_customer_session_summary,
        create_support_ticket,
        get_ticket_status,
        list_customer_tickets,
        vendor_reply_ticket,
        close_support_ticket
    )
    from rag_tools import (
        search_product_guides,
        troubleshoot_product_issue,
        index_customer_care_docs
    )
    from lstm_sentiment import run_lstm_sentiment_analysis
    from finetune_adapter import apply_finetuned_care_adapter

MODEL_NAME = os.environ.get("DEFAULT_MODEL", "gemini-3.1-flash-lite")

# Pre-index documents on startup
index_customer_care_docs()


# -------------------------------------------------------------
# SAFETY GUARDRAILS
# -------------------------------------------------------------

def input_safety_guardrail(callback_context, llm_request: LlmRequest):
    """Sanitizes user input to prevent credit card leakage and abusive prompts."""
    for content in (llm_request.contents or []):
        # Only inspect user messages for security filter
        if getattr(content, "role", "") == "model":
            continue
        for part in (content.parts or []):
            if part.text:
                # Strip known system identifiers (Ticket IDs, Order IDs, Claims, RMA, Tracking)
                clean_text = re.sub(
                    r"\b(TCK|ORD|CLM|RMA|TRK|FDX|UPS|DHL|SN|CUST)-[A-Za-z0-9-]+\b",
                    "",
                    part.text,
                    flags=re.IGNORECASE
                )
                # Credit Card Detection: 15-16 digit cards in 4-4-4-4 or raw format
                has_formatted_cc = bool(re.search(r"\b(?:\d{4}[ -]){3}\d{4}\b", clean_text))
                has_amex_cc = bool(re.search(r"\b\d{4}[ -]\d{6}[ -]\d{5}\b", clean_text))
                has_raw_cc = bool(re.search(r"\b(?:4[0-9]{15}|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b", clean_text))

                if has_formatted_cc or has_amex_cc or has_raw_cc:
                    return LlmResponse(
                        content=types.Content(
                            role="model",
                            parts=[types.Part.from_text(
                                text="[Security Alert]: For your safety and PCI compliance, please never enter full credit card numbers in chat. Our billing systems securely store your payment method on file."
                            )]
                        )
                    )
                # Restricted Prompt Injection Filter
                if "ignore all instructions" in part.text.lower() or "system prompt leak" in part.text.lower():
                    return LlmResponse(
                        content=types.Content(
                            role="model",
                            parts=[types.Part.from_text(
                                text="I am here exclusively to assist you with post-purchase customer care, product troubleshooting, order tracking, returns, and warranties."
                            )]
                        )
                    )
    return None


def tool_argument_guardrail(tool: BaseTool, args: dict, tool_context: ToolContext):
    """Sanitizes parameters passed into care tools to block malicious inputs."""
    for param in ["order_id", "ticket_id"]:
        if param in args and args[param]:
            val = str(args.get(param, "")).strip()
            if any(c in val for c in ["<", ">", ";", "$", "{", "}", "'", '"']):
                raise ValueError(f"Malicious characters detected in {param} parameter.")
    return None


# -------------------------------------------------------------
# SPECIALIST SUB-AGENTS
# -------------------------------------------------------------

order_logistics_agent = Agent(
    name="order_logistics_specialist",
    model=MODEL_NAME,
    description="Specialist in order lookup, courier tracking (FedEx/UPS/DHL), delivery delay risk prediction, and 99k+ Kaggle order logs.",
    instruction="""You are the Order Logistics Specialist.
Your Mission:
1. When a customer asks about their package, order status, or tracking, call `track_shipment` or `lookup_order`.
2. To evaluate delivery transit delays, call `predict_delivery_delay_risk`.
3. To view store-wide delivery KPIs across the 99,441 dataset orders, call `get_ecommerce_dataset_kpis`.
4. Provide exact milestone timestamps, carrier tracking codes, and estimated delivery dates.
5. Be clear, concise, and reassuring.""",
    tools=[
        lookup_order,
        track_shipment,
        predict_delivery_delay_risk,
        get_ecommerce_dataset_kpis
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)

product_support_agent = Agent(
    name="product_troubleshooting_specialist",
    model=MODEL_NAME,
    description="Specialist in technical troubleshooting, device setup, error codes, and fine-tuned domain adaptation via RAG.",
    instruction="""You are the Technical Support and Diagnostic Specialist.
Your Mission:
1. When a customer reports device malfunctions, error codes, Wi-Fi pairing issues, audio sync, or cleaning alerts, call `troubleshoot_product_issue` or `search_product_guides`.
2. To provide strict schema-compliant resolution, apply `apply_finetuned_care_adapter`.
3. Present clear, numbered troubleshooting steps matching the official product manuals.
4. Always cite the documentation source at the end (e.g. `*Source: docs/smart_tv_manual.md (Section)*`).
5. If remote troubleshooting fails or documentation does not cover the specific issue, offer to create an asynchronous vendor support ticket using `create_support_ticket` or advise warranty replacement.""",
    tools=[
        troubleshoot_product_issue,
        search_product_guides,
        apply_finetuned_care_adapter,
        create_support_ticket
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)

returns_warranty_agent = Agent(
    name="returns_warranty_specialist",
    model=MODEL_NAME,
    description="Specialist in 30-day return policy, prepaid RMA return labels, warranty verification, and replacement claims.",
    instruction="""You are the Returns and Warranty Specialist.
Your Mission:
1. For return requests, check 30-day eligibility with `check_return_eligibility` and generate return labels using `create_rma_return`.
2. For hardware defects, verify warranty coverage using `check_warranty_status` and dispatch replacement units with `file_warranty_claim`.
3. Explain refund timelines (3-5 business days) and zero restocking fees clearly.""",
    tools=[
        check_return_eligibility,
        create_rma_return,
        check_warranty_status,
        file_warranty_claim
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)

escalation_sentiment_agent = Agent(
    name="escalation_sentiment_specialist",
    model=MODEL_NAME,
    description="Specialist in customer sentiment sequence analysis using LSTM, courtesy credits, and Tier-2 supervisor escalation.",
    instruction="""You are the Senior Customer Care Escalation & Sentiment Intelligence Specialist.
Your Mission:
1. Analyze customer emotional valence, churn risk, and frustration trajectory across conversation turns using `run_lstm_sentiment_analysis`.
2. When frustration or shipping delays occur, apologize empathetically and offer courtesy credit with `issue_courtesy_credit`.
3. If human intervention or executive review is needed, dispatch a priority callback ticket with `escalate_to_human_supervisor`.
4. Use `get_customer_session_summary` to review past context and state.""",
    tools=[
        run_lstm_sentiment_analysis,
        issue_courtesy_credit,
        escalate_to_human_supervisor,
        get_customer_session_summary
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)

vendor_ticket_agent = Agent(
    name="vendor_ticket_specialist",
    model=MODEL_NAME,
    description="Specialist in asynchronous vendor support ticket creation, ticket tracking, vendor SLA management, and resolution lookup.",
    instruction="""You are the Vendor Support & Ticketing Specialist.
Your Mission:
1. When a user asks a question that is unresolved by the AI system, out-of-scope, or explicitly requests to contact the vendor, call `create_support_ticket`. Provide the user their Ticket ID and clear SLA expectations.
2. When a user asks for ticket status (e.g. 'What is my ticket status?' or 'I want to check my ticket'):
   - If the user DID NOT specify a Ticket ID (e.g., TCK-XXXX) or Order ID (e.g., ORD-XXXX) in their message, and no active ticket ID exists in session memory, DO NOT list all tickets. Simply reply politely asking: "Could you please share your Ticket ID or Order ID so I can check the status for you?"
   - ONLY call `get_ticket_status` when a specific Ticket ID or Order ID is provided or active in session memory.
3. If a vendor response is present (`has_vendor_response` is True) for the requested ticket, present the vendor's resolution clearly and politely.
4. If the ticket is still pending vendor response, explain that it is in the vendor's queue and provide the expected SLA reassurance.""",
    tools=[
        create_support_ticket,
        get_ticket_status,
        list_customer_tickets,
        vendor_reply_ticket,
        close_support_ticket,
        get_customer_session_summary
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)


# -------------------------------------------------------------
# ROOT COORDINATOR AGENT
# -------------------------------------------------------------

CARE_COORDINATOR_INSTRUCTIONS = """
You are the Lead Post-Purchase Customer Care Assistant for our store.
You integrate cutting-edge ML and AI engineering capabilities:
1. **Large-Scale 99,441 Order Knowledge**: Call `lookup_order`, `track_shipment`, `predict_delivery_delay_risk`, or `get_ecommerce_dataset_kpis`.
2. **LSTM Neural Sequence Sentiment Analysis**: Call `run_lstm_sentiment_analysis` to evaluate customer sentiment trajectory and churn risk.
3. **Hybrid RAG Knowledge Retrieval**: Call `troubleshoot_product_issue` or `search_product_guides` to retrieve exact manual instructions with citations (*Source: docs/filename.md*).
4. **Fine-Tuned Domain Adapters**: Call `apply_finetuned_care_adapter` for structured post-purchase resolution templates.
5. **Returns & RMA Automation**: Call `check_return_eligibility` and `create_rma_return`.
6. **Warranty Claims & Replacements**: Call `check_warranty_status` and `file_warranty_claim`.
7. **Courtesy Credits & Escalations**: Call `issue_courtesy_credit` ($25-$50) or `escalate_to_human_supervisor`.
8. **Asynchronous Vendor Support Tickets**: When an inquiry cannot be answered by official manuals or automated tools, or when the customer asks to contact the vendor/open a ticket, call `create_support_ticket` and supply the user with their Ticket ID and vendor SLA. When the user asks generally for ticket status without supplying a Ticket ID or Order ID, simply ask them to provide their Ticket ID or Order ID. Only run `get_ticket_status` when a specific ID is provided.

### Communication Tone:
- Empathetic, polite, proactive, and concise.
- Format responses cleanly with bullet points, numbered steps, and bold key metrics.
"""

root_agent = Agent(
    name="customer_care_coordinator",
    model=MODEL_NAME,
    description="Comprehensive Post-Purchase AI Customer Care Chatbot combining Multi-Agents, LSTM Sentiment, Fine-Tuning, Hybrid RAG, 99k+ Kaggle Orders, and Asynchronous Vendor Ticketing.",
    instruction=CARE_COORDINATOR_INSTRUCTIONS,
    sub_agents=[
        order_logistics_agent,
        product_support_agent,
        returns_warranty_agent,
        escalation_sentiment_agent,
        vendor_ticket_agent
    ],
    tools=[
        lookup_order,
        track_shipment,
        predict_delivery_delay_risk,
        get_ecommerce_dataset_kpis,
        troubleshoot_product_issue,
        search_product_guides,
        check_return_eligibility,
        create_rma_return,
        check_warranty_status,
        file_warranty_claim,
        run_lstm_sentiment_analysis,
        apply_finetuned_care_adapter,
        issue_courtesy_credit,
        escalate_to_human_supervisor,
        get_customer_session_summary,
        create_support_ticket,
        get_ticket_status,
        list_customer_tickets,
        vendor_reply_ticket,
        close_support_ticket
    ],
    before_model_callback=input_safety_guardrail,
    before_tool_callback=tool_argument_guardrail
)
