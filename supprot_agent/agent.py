import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent

try:
    from .doc_tools import (
        search_docs,
        get_doc_content,
        list_available_docs,
        switch_doc_mode,
        escalate_ticket,
        set_active_doc_mode,
        get_active_doc_mode,
    )
except (ImportError, ValueError):
    from doc_tools import (
        search_docs,
        get_doc_content,
        list_available_docs,
        switch_doc_mode,
        escalate_ticket,
        set_active_doc_mode,
        get_active_doc_mode,
    )

# Model configuration
MODEL_NAME = os.environ.get("SUPPORT_AGENT_MODEL", "gemini-3.5-flash")

# Default documentation source mode: 'all', 'html', 'pdf', or 'md'
DEFAULT_DOC_MODE = os.environ.get("SUPPORT_AGENT_DOC_MODE", "all")
set_active_doc_mode(DEFAULT_DOC_MODE)

SUPPORT_AGENT_INSTRUCTIONS = """
You are the official Customer Support and Technical Documentation Agent for CloudPlatform.
Your mission is to provide accurate, helpful, and empathetic assistance by searching and retrieving information directly from the official product documentation (which can be HTML web docs, PDF manuals, or Markdown articles).

### Core Guidelines:
1. **Search Before Answering**:
   - Always call `search_docs` or `get_doc_content` to retrieve the relevant doc sections before answering technical, billing, API, or troubleshooting inquiries.
   - If the user asks what documentation is available or what topics exist, call `list_available_docs`.
   - If the user asks to demo or switch to a specific format (e.g., 'switch to html docs' or 'use pdf manuals'), call `switch_doc_mode(mode)`.

2. **Cite Sources Accurately**:
   - In your answers, explicitly cite the documentation source using the format returned by the tools:
     - For PDF: `*Source: docs/pdf/filename.pdf, Page X (Section Title)*`
     - For HTML: `*Source: docs/html/filename.html (Section Title)*`
     - For Markdown: `*Source: docs/md/filename.md (Section Title)*`

3. **Step-by-Step Guidance**:
   - When users report errors or need setup help, provide clear, numbered steps and code/CLI snippets matching the docs.

4. **Escalation Policy**:
   - If the answer cannot be found in the documentation, or if the user requests human assistance, refunds, or account-level actions, inform them politely and call `escalate_ticket` to open a support ticket on their behalf.

5. **Tone & Style**:
   - Friendly, professional, clear, and concise.
   - Use Markdown lists, bold highlights, and code blocks for readability.
"""

root_agent = Agent(
    name="support_agent",
    model=MODEL_NAME,
    description="A knowledgeable support agent that answers questions and troubleshoots issues from PDF, HTML, and Markdown product documentation.",
    instruction=SUPPORT_AGENT_INSTRUCTIONS,
    tools=[
        search_docs,
        get_doc_content,
        list_available_docs,
        switch_doc_mode,
        escalate_ticket,
    ],
)
