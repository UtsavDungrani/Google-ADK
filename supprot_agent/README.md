# Multi-Format Documentation Support Agent (`supprot_agent`)

An intelligent AI Customer & Technical Support Agent built with the **Google Agent Development Kit (ADK)** and **Gemini 3.5 Flash**. The agent dynamically searches, retrieves, and cites official product documentation across **PDF (`.pdf`)**, **HTML (`.html`)**, and **Markdown (`.md`)** formats.

---

## 📁 Project Structure

```
supprot_agent/
├── docs/                               # Knowledge base organized by format
│   ├── html/                           # HTML documentation (Web format)
│   │   ├── getting_started.html
│   │   ├── billing_and_subscriptions.html
│   │   ├── troubleshooting.html
│   │   ├── api_reference.html
│   │   └── faq.html
│   ├── pdf/                            # PDF documentation (Manual format with pages)
│   │   ├── getting_started.pdf
│   │   ├── billing_and_subscriptions.pdf
│   │   ├── troubleshooting.pdf
│   │   ├── api_reference.pdf
│   │   └── faq.pdf
│   └── md/                             # Markdown documentation
│       ├── getting_started.md
│       ├── billing_and_subscriptions.md
│       ├── troubleshooting.md
│       ├── api_reference.md
│       └── faq.md
├── doc_tools.py                        # Universal extractor, retriever, and mode manager
├── agent.py                            # ADK root_agent definition and instructions
├── populate_docs.py                    # Generator script for docs (HTML & PDF)
├── __init__.py                         # Module export
├── .env                                # Environment variables (API keys)
└── .gitignore                          # Git ignore rules
```

---

## 🎯 Switching Document Formats for Demos

You can control which folder/format the agent uses using three simple methods:

### Option 1: In Python Code (Direct API)
```python
from supprot_agent.doc_tools import set_active_doc_mode

# Switch to HTML only
set_active_doc_mode("html")

# Switch to PDF only
set_active_doc_mode("pdf")

# Switch to Markdown only
set_active_doc_mode("md")

# Search across ALL formats
set_active_doc_mode("all")
```

### Option 2: Environment Variable
Set the `SUPPORT_AGENT_DOC_MODE` environment variable before running:
```bash
# Windows PowerShell
$env:SUPPORT_AGENT_DOC_MODE="html"; adk run supprot_agent

# Windows CMD
set SUPPORT_AGENT_DOC_MODE=pdf && adk run supprot_agent

# Linux / macOS
SUPPORT_AGENT_DOC_MODE=pdf adk run supprot_agent
```

### Option 3: Conversationally in Chat
During an interactive session, you can ask the agent:
> *"Switch doc mode to HTML and tell me the refund policy."*  
> *"Switch doc mode to PDF and show me how to fix Error 401."*

---

## 🛠️ Key Capabilities & Tools

1. **`search_docs(query, category)`**:
   - Searches across documents in the active format mode (`html`, `pdf`, `md`, or `all`).
   - Extracts headings, sections, and PDF page numbers.
   - Generates exact citations (e.g., `*Source: docs/pdf/billing_and_subscriptions.pdf, Page 1*`).

2. **`get_doc_content(document_name, section_title, page)`**:
   - Retrieves full text, a specific HTML/MD section, or a specific PDF page.

3. **`list_available_docs()`**:
   - Lists all documents, formats, page counts, and sections in the active mode.

4. **`switch_doc_mode(mode)`**:
   - ADK tool allowing the agent/user to switch doc source at runtime.

5. **`escalate_ticket(user_email, issue_title, issue_description, priority)`**:
   - Generates a tracked support ticket with SLA estimate when an issue requires human specialist intervention.

---

## 🚀 How to Run

### 1. Interactive CLI Mode
```bash
adk run supprot_agent
```

### 2. Single-Step Query
```bash
adk run supprot_agent "How much is the Pro plan and what is the refund policy?"
```

### 3. Launch Web UI Server
```bash
adk web supprot_agent
```

### 4. Run via Python Script
```python
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from supprot_agent.agent import root_agent
from supprot_agent.doc_tools import set_active_doc_mode

async def main():
    # Set to demo HTML docs
    set_active_doc_mode("html")
    
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service)
    session = await session_service.create_session()
    
    response = await runner.run_single_turn(
        session_id=session.id,
        user_message="What are the rate limits for the Pro plan and how do I handle error 429?"
    )
    print(response.message)

if __name__ == "__main__":
    asyncio.run(main())
```
