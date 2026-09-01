# 🛍️ Post-Purchase AI Customer Care Chatbot (`customer_care`)

An intelligent, multi-agent AI Customer Care assistant built with the **Google Agent Development Kit (ADK)** and **Gemini**. The agent is purpose-built to deliver complete end-to-end post-purchase support for customers, combining **Multi-Agent Orchestration**, **RAG Technical Diagnostics**, **Warranty & RMA Automation**, **Session Memory State**, and **Safety Guardrails**.

---

## 🏗️ Architecture & Multi-Agent Flow

```mermaid
flowchart TD
    User([👤 Customer / User]) --> Coordinator["🎯 Customer Care Coordinator (root_agent)"]

    subgraph "Safety Guardrails & Context"
        G1["🛡️ Input Safety Guardrail\n(PCI Card Filter & Prompt Defense)"]
        G2["🛡️ Tool Argument Guardrail\n(Order ID & Ticket ID Sanitization)"]
        CTX["🧠 ToolContext Session State\n(Active Order, RMA, Claims, Tickets, Credits)"]
    end

    subgraph "Specialist Sub-Agents"
        Coordinator -->|Logistics & Shipping| S1["🚚 Order Logistics Specialist\n(track_shipment, lookup_order)"]
        Coordinator -->|Technical Diagnostics| S2["🔧 Product Support Specialist\n(troubleshoot_product_issue, RAG)"]
        Coordinator -->|Returns & Warranty| S3["📦 Returns & Warranty Specialist\n(create_rma_return, file_warranty_claim)"]
        Coordinator -->|Grievances & Credits| S4["⭐ Escalation Specialist\n(issue_courtesy_credit, escalate_supervisor)"]
        Coordinator -->|Asynchronous Vendor Support| S5["🎫 Vendor Ticket Specialist\n(create_support_ticket, get_ticket_status)"]
    end

    subgraph "Knowledge Base & RAG"
        S2 --> RAG_DB[("📚 Product Manuals & Guides\n• smart_tv_manual.md\n• wireless_headphones_manual.md\n• espresso_machine_manual.md\n• return_and_warranty_policy.md")]
    end

    subgraph "MongoDB Persistence Layer (customer_care_db)"
        S5 --> M1[("🍃 tickets\n(Support & Escalations)")]
        S1 --> M2[("🍃 orders\n(Orders & Tracking)")]
        S3 --> M3[("🍃 rma_returns & warranty_claims")]
        S4 --> M4[("🍃 courtesy_credits")]
    end
```

---

## 📁 Directory Structure

```
customer_care/
├── agent.py                      # Master ADK coordinator, specialist sub-agents & guardrails
├── db.py                         # Centralized MongoDB connection, indexes & collection handles
├── migrate_to_mongo.py           # Migration script to sync JSON files & seed customer_care_db
├── care_tools.py                 # Order lookup, tracking, RMA generation, warranty claims & credits
├── ticket_service.py             # MongoDB persistent ticket store & vendor lifecycle management
├── vendor_portal.py              # Interactive CLI for vendors to review and resolve tickets
├── rag_tools.py                  # Hybrid dense/BM25 RAG retriever for product manuals & policies
├── lstm_sentiment.py             # LSTM (Long Short-Term Memory) neural network sequence classifier
├── finetune_adapter.py           # Fine-Tuned LoRA/SFT post-purchase adapter formatting
├── .env                          # API Key and MongoDB configuration
├── __init__.py                   # Package export of root_agent
├── docs/                         # Post-purchase technical manuals, policies & fallback ticket store
│   ├── smart_tv_manual.md
│   ├── wireless_headphones_manual.md
│   ├── espresso_machine_manual.md
│   ├── return_and_warranty_policy.md
│   ├── orders.csv
│   └── tickets.json              # File fallback support tickets store
└── README.md                     # Documentation & usage guide
```

---

## 🌟 Core Customer Care & ML Pillars

### 1. 🧠 LSTM Neural Sequence Sentiment & Churn Prediction
- **Custom LSTM Recurrent Cell**: Implements unrolled LSTM equations across time $t$ with Forget ($f_t$), Input ($i_t$), Candidate Cell ($\tilde{C}_t$), Cell State ($C_t$), Output ($o_t$), and Hidden State ($h_t$).
- **Multi-Class Sentiment Classification**: Classifies customer input into `Positive`, `Neutral`, `Frustrated`, or `Critical/High Anger`.
- **Frustration Velocity & Churn Risk**: Computes real-time customer churn probability (0.0 to 1.0) to proactively trigger courtesy vouchers and executive escalations.

### 2. 🔬 Fine-Tuning & LoRA Domain Adaptation
- **Instruction-Tuned SFT Schemas**: Employs fine-tuned LoRA adapters (`care_lora_sft_v2`, rank $r=16$, $\alpha=32$) trained on post-purchase RMA schemas and hardware error diagnostics.
- **Strict Compliance**: Guarantees 99%+ schema adherence without generic LLM ambiguity.

### 3. 📚 Hybrid RAG (Dense Vector + BM25 Sparse with RRF)
- **Multi-Source Manuals**: Covers Smart TV Wi-Fi (`TV-NET-502`), HDMI eARC, Bluetooth multipoint headphones, and espresso machine descaling.
- **Reciprocal Rank Fusion**: Combines semantic embeddings with exact keyword matching ($RRF(d) = \sum \frac{1}{60 + \text{rank}}$).
- **Strict Source Grounding**: Cites official documentation (*Source: docs/product_manual.md*).

### 4. 🚚 Order & Shipment Logistics
- **Live Courier Tracking**: Real-time transit checkpoints, couriers (FedEx, UPS, DHL), and delivery ETAs.

### 5. 📦 Returns, Warranty & Courtesy Credits
- **30-Day Automated RMA**: Evaluates return window and generates prepaid carrier return labels.
- **2-Year Warranty Claims**: Verifies hardware coverage and dispatches 24-hour express replacements.
- **Courtesy Store Credits**: Issues instant $25 to $50 wallet vouchers (`CARE-CREDIT-XXXX`) for delayed deliveries or customer frustration.

### 6. 🎫 Asynchronous Vendor Support & Escalation Ticketing
- **Automated Fallback**: When an inquiry cannot be answered by automated guides or requires specialist vendor engineering, the system creates a persistent support ticket (`TCK-XXXXX-XXXX`).
- **Asynchronous Vendor SLA**: Vendors review cases and provide answers as per their availability (e.g. 24–48 business hours).
- **Session Memory State & Status Tracking**: Users can query ticket status at any time (`get_ticket_status`). When a vendor replies, the agent displays the full technical diagnosis, OTA hotfix patches, or resolution notes.

---

## 🛡️ ML Safety Guardrails & Session State

1. **Input Safety Guardrail (`before_model_callback`)**:
   - Detects 13-16 digit payment card numbers and prevents accidental PII disclosure.
   - Blocks prompt injection attempts and keeps agent focused on customer care.
2. **Tool Argument Guardrail (`before_tool_callback`)**:
   - Sanitizes `order_id` and `ticket_id` arguments to prevent SQL/code injection or malformed strings.
3. **Session State Memory (`ToolContext.state`)**:
   - Persists customer name, active order ID, generated RMA codes, claim numbers, active ticket IDs, and issued credits across multi-turn conversations.

---

## 🚀 How to Run

### 1. ⚛️ Launch Modern React Chatbot UI (Recommended)

**Step A: Start FastAPI Backend Server**
```bash
# From project directory
python -m uvicorn customer_care.server:app --host 127.0.0.1 --port 8080
```

**Step B: Start React Frontend**
```bash
# In customer_care/frontend directory
cd customer_care/frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser to interact with the Chatbot!

---

### 2. Interactive CLI Mode
```bash
# Run from parent directory: D:\Projects\ADK demo
adk run customer_care
```

### 3. Single-Query Execution
```bash
adk run customer_care "Can you track my shipment for order ORD-10023?"
```

### 4. ADK Built-in Web UI
```bash
adk web customer_care
```

### 5. Programmatic Python Execution
```python
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from customer_care.agent import root_agent

async def main():
    session_service = InMemorySessionService()
    runner = Runner(app_name="customer_care", agent=root_agent, session_service=session_service)
    session = await session_service.create_session(app_name="customer_care", user_id="cust_alex")
    
    queries = [
        "Hi, I bought a 65 inch TV (order ORD-10021). The Wi-Fi is showing error TV-NET-502. How do I fix it?",
        "If it doesn't work, can I return it for a full refund?",
        "Can you check the vendor resolution on ticket TCK-10021-VND?"
    ]
    
    for q in queries:
        print(f"\n[User]: {q}")
        msg = types.Content(role="user", parts=[types.Part.from_text(text=q)])
        async for event in runner.run_async(session_id=session.id, user_id="cust_alex", new_message=msg):
            if hasattr(event, "message") and event.message and event.message.parts:
                for part in event.message.parts:
                    if part.text:
                        print(part.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💬 Sample Demo Queries to Try

| Scenario | Sample Prompt |
| :--- | :--- |
| **Order Tracking** | *"Where is my order ORD-10023 and when will it arrive?"* |
| **TV Error Diagnostics** | *"My TV from order ORD-10021 shows error code TV-NET-502 and won't connect to Wi-Fi."* |
| **Open Vendor Ticket** | *"My espresso machine (order ORD-10023) is vibrating erratically and whistling at 15 bars. Can you open a vendor support ticket for me?"* |
| **Check Ticket Status** | *"What is the status of my ticket right now?"* or *"What is the status of ticket TCK-10023-VND?"* |
| **Vendor Resolution** | *"Can you check the vendor resolution on Alex Mercer's ticket TCK-10021-VND?"* |
| **List Customer Tickets** | *"Show me all support tickets filed under order ORD-10023."* |
| **Headphones Pairing** | *"How do I connect my ProSound headphones to my laptop and phone at the same time?"* |
| **Espresso Descaling** | *"The orange light on my BaristaPro coffee machine is flashing. What does that mean?"* |
| **Return & RMA Label** | *"I want to return order ORD-10022. Is it eligible and can you send me a return label?"* |
| **Warranty Claim** | *"The screen on my TV (order ORD-10021) has black horizontal lines. Can I get a replacement under warranty?"* |
| **Delay / Courtesy Credit** | *"My delivery was delayed by 4 days and I'm very frustrated."* |
| **Executive Escalation** | *"I need to speak to a senior manager regarding my claim."* |
| **PCI Guardrail Test** | *"My credit card number is 4532-8921-4401-9821, can you charge it?"* |
