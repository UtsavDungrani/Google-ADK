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
        close_support_ticket,
        adapt_response_tone_and_language,
        detect_and_adapt_language,
        recall_customer_memory,
        save_customer_fact,
        get_cross_session_timeline,
        retrieve_gold_exemplars
    )
    from .rag_tools import (
        search_product_guides,
        troubleshoot_product_issue,
        index_customer_care_docs,
        search_faq_knowledge_base,
        add_dynamic_faq
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
        close_support_ticket,
        adapt_response_tone_and_language,
        detect_and_adapt_language,
        recall_customer_memory,
        save_customer_fact,
        get_cross_session_timeline,
        retrieve_gold_exemplars
    )
    from rag_tools import (
        search_product_guides,
        troubleshoot_product_issue,
        index_customer_care_docs,
        search_faq_knowledge_base,
        add_dynamic_faq
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
    description="Specialist in technical troubleshooting, FAQ knowledge retrieval, device setup, error codes, and fine-tuned domain adaptation via RAG.",
    instruction="""You are the Technical Support and Diagnostic Specialist.
Your Mission:
1. When a customer reports device malfunctions, error codes, Wi-Fi pairing issues, audio sync, or cleaning alerts, call `troubleshoot_product_issue` or `search_product_guides`.
2. When a customer asks general policy, shipping, return, warranty, billing, or store FAQ questions, call `search_faq_knowledge_base`.
3. To adapt target language or persona tone, call `adapt_response_tone_and_language`.
4. To provide strict schema-compliant resolution, apply `apply_finetuned_care_adapter`.
5. Present clear, numbered troubleshooting steps matching official documentation.
6. Always cite the documentation source at the end (e.g. `*Source: MongoDB Database (Category)*`).
7. If troubleshooting steps have already been attempted by the customer and failed (e.g. descaling run twice but light is still flashing or pressure is stuck at 0 bar), DO NOT repeat troubleshooting lookups. Call `create_support_ticket` immediately to create a vendor support ticket and set clear SLA expectations.""",
    tools=[
        troubleshoot_product_issue,
        search_product_guides,
        search_faq_knowledge_base,
        add_dynamic_faq,
        adapt_response_tone_and_language,
        apply_finetuned_care_adapter,
        retrieve_gold_exemplars,
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
3. For general return/warranty FAQ inquiries, search the store knowledge base with `search_faq_knowledge_base`.
4. Explain refund timelines (3-5 business days) and zero restocking fees clearly.""",
    tools=[
        check_return_eligibility,
        create_rma_return,
        check_warranty_status,
        file_warranty_claim,
        retrieve_gold_exemplars,
        search_faq_knowledge_base
    ],
    before_tool_callback=tool_argument_guardrail,
    before_model_callback=input_safety_guardrail
)

escalation_sentiment_agent = Agent(
    name="escalation_sentiment_specialist",
    model=MODEL_NAME,
    description="Specialist in customer sentiment sequence analysis using LSTM, cross-session long-term memory recall, courtesy credits, and Tier-2 supervisor escalation.",
    instruction="""You are the Senior Customer Care Escalation & Sentiment Intelligence Specialist.
Your Mission:
1. Analyze customer emotional valence, churn risk, and frustration trajectory across conversation turns using `run_lstm_sentiment_analysis`.
2. Access and synthesize customer long-term episodic and profile history using `recall_customer_memory` and `get_cross_session_timeline`.
3. When customer expresses persistent personal preferences, communication constraints, or device setups, save them using `save_customer_fact`.
4. When frustration or shipping delays occur, apologize empathetically and offer courtesy credit with `issue_courtesy_credit`.
5. If human intervention or executive review is needed, dispatch a priority callback ticket with `escalate_to_human_supervisor`.
6. Use `get_customer_session_summary` to review past context and state.""",
    tools=[
        run_lstm_sentiment_analysis,
        recall_customer_memory,
        save_customer_fact,
        get_cross_session_timeline,
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
   - If the user DID NOT specify a Ticket ID (e.g., TCK-XXXX) or Order ID (e.g., ORD-XXXX) in their message, and no active ticket ID exists in session memory, DO NOT call `list_customer_tickets` or `get_ticket_status`. DO NOT invoke any tools. Directly respond asking: "Could you please share your Ticket ID (e.g., TCK-XXXX) or Order ID so I can check the status for you?"
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
You are the Lead Post-Purchase Customer Care Coordinator and Orchestrator for our store.
You coordinate and route customer inquiries across specialized sub-agents:

1. **Order Logistics & Tracking**: When a customer asks about order status, tracking, courier details, transit delay risk, or delivery KPIs, route to `order_logistics_specialist` using `transfer_to_agent`.
2. **Returns & Warranty Verification**: When a customer asks to return an item, check return or refund eligibility, request prepaid RMA return labels, verify warranty coverage, or file warranty claims, route to `returns_warranty_specialist` using `transfer_to_agent`.
3. **Escalations, Frustration & Courtesy Credits**: When a customer expresses frustration, reports repeated order delays, demands a supervisor, or requests compensation/credits, route to `escalation_sentiment_specialist` using `transfer_to_agent`.
4. **Hardware Diagnostics & Technical Troubleshooting RAG**: When a customer reports initial device malfunctions, hardware error codes (such as TV-NET-502), Wi-Fi pairing issues, or manual lookups, call `troubleshoot_product_issue` or `search_product_guides`. Present clear numbered steps matching official documentation and cite the source (*Source: MongoDB Database (Category)*).
5. **Asynchronous Vendor Support Tickets**: When troubleshooting steps have already been attempted by the customer and failed (e.g. running descaling cycle twice with persisting hardware errors or 0 bar pressure), or when an inquiry cannot be answered by official manuals, call `create_support_ticket` immediately to open a vendor support ticket and provide SLA expectations. When the user asks generally for ticket status without supplying a Ticket ID or Order ID (e.g., "What is the status of my support ticket?"), DO NOT call `list_customer_tickets` or `get_ticket_status`. DO NOT invoke any tools. Directly respond asking: "Could you please share your Ticket ID (e.g., TCK-XXXX) or Order ID so I can check the status for you?"
6. **Multilingual NLP & Cultural Pragmatics**: When the customer communicates in non-English (Spanish, French, German, Hindi, Japanese) or code-mixed language (Hinglish/Spanglish), call `detect_and_adapt_language` or `adapt_response_tone_and_language`. Respond fluently in the customer's language using respectful cultural honorifics (Spanish: Usted, German: Sie, Hindi: Aap, Japanese: Keigo). Keep Order IDs (ORD-XXXX), serial numbers, and error codes (TV-NET-502) in exact alphanumeric format.
7. **Cross-Session Long-Term Memory Continuity**: Access customer profile and episodic history via `recall_customer_memory` or pre-loaded memory in session context. When interacting with returning customers (e.g. Alex Mercer, Sarah Connor, David Kim):
    - Warmly acknowledge their return by name.
    - Proactively reference their registered devices or past tickets (e.g. asking Alex if the Wi-Fi OTA firmware update resolved error TV-NET-502, or checking on David's espresso customs hold).
    - Align with their preferred communication tone (e.g. technical, concise, empathetic).
    - If the customer reveals a new persistent personal fact, hardware setup, or communication preference, call `save_customer_fact` to persist it across future sessions.
8. **Dynamic Few-Shot RAG & Gold-Standard Precedents**: When resolving complex diagnostic symptoms, policy exceptions, return grace periods, or high-friction escalations, consult gold-standard human resolution precedents via dynamic few-shot retrieval or by calling `retrieve_gold_exemplars`. Model the agent's tone, empathy, exact step numbers, and official policy citations after these verified supervisor cases.
9. **Fine-Tuned Domain Adapters & Store FAQ**: Call `apply_finetuned_care_adapter` or `search_faq_knowledge_base` to retrieve exact store policies, shipping/return FAQs, and manual instructions with citations.

### Communication Tone:
- Empathetic, polite, proactive, and concise.
- Format responses cleanly with bullet points, numbered steps, and bold key metrics.
"""

root_agent = Agent(
    name="customer_care_coordinator",
    model=MODEL_NAME,
    description="Comprehensive Post-Purchase AI Customer Care Chatbot combining Multi-Agents, Multilingual NLP, Cross-Session Long-Term Memory, Dynamic Few-Shot RAG, LSTM Sentiment, Fine-Tuning, Hybrid FAQ RAG, 99k+ Kaggle Orders, and Asynchronous Vendor Ticketing.",
    instruction=CARE_COORDINATOR_INSTRUCTIONS,
    sub_agents=[
        order_logistics_agent,
        product_support_agent,
        returns_warranty_agent,
        escalation_sentiment_agent,
        vendor_ticket_agent
    ],
    tools=[
        troubleshoot_product_issue,
        search_product_guides,
        search_faq_knowledge_base,
        add_dynamic_faq,
        adapt_response_tone_and_language,
        detect_and_adapt_language,
        recall_customer_memory,
        save_customer_fact,
        get_cross_session_timeline,
        retrieve_gold_exemplars,
        apply_finetuned_care_adapter,
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

# Alias for ADK evaluation module introspection
agent = root_agent
