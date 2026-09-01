import os
import re
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# Base directory for docs relative to this file
DOCS_ROOT = Path(__file__).parent / "docs"

# Active Document Mode: 'all', 'html', 'pdf', 'md' (or subfolder name)
# Can be changed via environment variable SUPPORT_AGENT_DOC_MODE or set_active_doc_mode()
ACTIVE_DOC_MODE: str = os.environ.get("SUPPORT_AGENT_DOC_MODE", "all").lower()


def set_active_doc_mode(mode: str) -> dict:
    """Sets the active document folder/format mode for retrieval.

    Args:
        mode: The format or folder to use: 'all', 'html', 'pdf', 'md' (or 'markdown').

    Returns:
        Confirmation dictionary with current active mode and available document count.
    """
    global ACTIVE_DOC_MODE
    normalized = mode.strip().lower()
    if normalized in ["markdown", "md"]:
        ACTIVE_DOC_MODE = "md"
    elif normalized in ["html", "htm"]:
        ACTIVE_DOC_MODE = "html"
    elif normalized == "pdf":
        ACTIVE_DOC_MODE = "pdf"
    elif normalized == "all":
        ACTIVE_DOC_MODE = "all"
    else:
        # Check if custom subfolder exists
        custom_dir = DOCS_ROOT / normalized
        if custom_dir.is_dir():
            ACTIVE_DOC_MODE = normalized
        else:
            return {
                "status": "error",
                "message": f"Invalid mode '{mode}'. Supported modes: 'all', 'html', 'pdf', 'md' or existing subfolder.",
                "current_mode": ACTIVE_DOC_MODE
            }

    files = _get_active_files()
    return {
        "status": "success",
        "active_mode": ACTIVE_DOC_MODE,
        "active_directory": str(_get_mode_directory()),
        "total_documents": len(files),
        "available_files": [f.name for f in files]
    }


def get_active_doc_mode() -> dict:
    """Returns the currently active document source mode and target directory."""
    files = _get_active_files()
    return {
        "status": "success",
        "active_mode": ACTIVE_DOC_MODE,
        "active_directory": str(_get_mode_directory()),
        "total_documents": len(files),
        "available_files": [f.name for f in files]
    }


def switch_doc_mode(mode: str) -> dict:
    """Switches the knowledge base documentation source mode (html, pdf, md, or all).

    Use this tool when you need to switch document format modes for demonstrations or specific queries.

    Args:
        mode: The target mode: 'html' (HTML web docs), 'pdf' (PDF manual docs), 'md' (Markdown docs), or 'all' (all formats).

    Returns:
        Status of the switch and list of documents loaded in the new mode.
    """
    return set_active_doc_mode(mode)


def _get_mode_directory() -> Path:
    """Resolves directory path based on active mode."""
    if ACTIVE_DOC_MODE in ["md", "markdown"]:
        md_dir = DOCS_ROOT / "md"
        return md_dir if md_dir.exists() else DOCS_ROOT
    elif ACTIVE_DOC_MODE in ["html", "htm"]:
        html_dir = DOCS_ROOT / "html"
        return html_dir if html_dir.exists() else DOCS_ROOT
    elif ACTIVE_DOC_MODE == "pdf":
        pdf_dir = DOCS_ROOT / "pdf"
        return pdf_dir if pdf_dir.exists() else DOCS_ROOT
    elif ACTIVE_DOC_MODE != "all":
        custom_dir = DOCS_ROOT / ACTIVE_DOC_MODE
        if custom_dir.exists():
            return custom_dir
    return DOCS_ROOT


def _get_active_files(category: str = "") -> List[Path]:
    """Finds all relevant documentation files according to active mode and optional category filter."""
    if not DOCS_ROOT.exists():
        return []

    target_dir = _get_mode_directory()
    extensions = {".md", ".html", ".htm", ".pdf"}

    if ACTIVE_DOC_MODE in ["md", "markdown"]:
        extensions = {".md"}
    elif ACTIVE_DOC_MODE in ["html", "htm"]:
        extensions = {".html", ".htm"}
    elif ACTIVE_DOC_MODE == "pdf":
        extensions = {".pdf"}

    matched_files = []
    # Search within target directory recursively
    for path in target_dir.glob("**/*"):
        if path.is_file() and path.suffix.lower() in extensions:
            if category and category.lower() not in path.stem.lower():
                continue
            matched_files.append(path)

    return sorted(matched_files)


def _extract_md_sections(file_path: Path) -> List[Dict[str, Any]]:
    """Parses a Markdown file into distinct sections by headers."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return []

    lines = content.split("\n")
    sections = []
    
    h1 = file_path.stem.replace("_", " ").title()
    h2 = ""
    current_heading = h1
    current_lines = []

    for line in lines:
        if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
            if current_lines:
                sections.append({
                    "document": file_path.name,
                    "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
                    "format": "markdown",
                    "title": current_heading,
                    "content": "\n".join(current_lines).strip(),
                    "page": None
                })
                current_lines = []
            
            if line.startswith("# "):
                h1 = line.lstrip("# ").strip()
                h2 = ""
                current_heading = h1
            elif line.startswith("## "):
                h2 = line.lstrip("# ").strip()
                current_heading = f"{h1} -> {h2}" if h1 else h2
            else:
                h3 = line.lstrip("# ").strip()
                current_heading = f"{h2} -> {h3}" if h2 else h3
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "document": file_path.name,
            "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
            "format": "markdown",
            "title": current_heading,
            "content": "\n".join(current_lines).strip(),
            "page": None
        })

    return sections


def _extract_html_sections(file_path: Path) -> List[Dict[str, Any]]:
    """Parses an HTML file into sections using BeautifulSoup."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_html = f.read()
    except Exception:
        return []

    if BeautifulSoup is None:
        # Fallback simple text extraction
        clean_text = re.sub(r"<[^>]+>", " ", raw_html)
        return [{
            "document": file_path.name,
            "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
            "format": "html",
            "title": file_path.stem.replace("_", " ").title(),
            "content": clean_text.strip(),
            "page": None
        }]

    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    doc_title = file_path.stem.replace("_", " ").title()
    if soup.title and soup.title.string:
        doc_title = soup.title.string.strip()
    elif soup.find("h1"):
        doc_title = soup.find("h1").get_text().strip()

    sections = []

    # Check for <section> or <article> tags
    container_tags = soup.find_all(["section", "article"])
    if container_tags:
        for container in container_tags:
            heading = container.find(["h1", "h2", "h3", "h4"])
            heading_text = heading.get_text().strip() if heading else doc_title
            content_text = container.get_text(separator="\n", strip=True)
            if content_text:
                sections.append({
                    "document": file_path.name,
                    "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
                    "format": "html",
                    "title": f"{doc_title} -> {heading_text}" if heading_text != doc_title else doc_title,
                    "content": content_text,
                    "page": None
                })

    # If no section tags found, chunk by H1/H2/H3 headings
    if not sections:
        headings = soup.find_all(["h1", "h2", "h3"])
        if headings:
            for h in headings:
                h_text = h.get_text().strip()
                body_parts = []
                for sibling in h.find_next_siblings():
                    if sibling.name in ["h1", "h2", "h3"]:
                        break
                    text = sibling.get_text(separator="\n", strip=True)
                    if text:
                        body_parts.append(text)
                
                content = "\n".join(body_parts).strip() if body_parts else h_text
                sections.append({
                    "document": file_path.name,
                    "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
                    "format": "html",
                    "title": f"{doc_title} -> {h_text}" if h_text != doc_title else doc_title,
                    "content": content,
                    "page": None
                })
        else:
            # Fallback to whole body
            body_text = soup.get_text(separator="\n", strip=True)
            sections.append({
                "document": file_path.name,
                "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
                "format": "html",
                "title": doc_title,
                "content": body_text,
                "page": None
            })

    return sections


def _extract_pdf_sections(file_path: Path) -> List[Dict[str, Any]]:
    """Parses a PDF file page-by-page into searchable sections with page metadata."""
    if PdfReader is None:
        return []

    try:
        reader = PdfReader(str(file_path))
    except Exception:
        return []

    sections = []
    doc_title = file_path.stem.replace("_", " ").title()

    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""

        page_text = page_text.strip()
        if not page_text:
            continue

        # Detect top heading or first non-empty line
        first_line = ""
        for line in page_text.split("\n"):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 2:
                first_line = cleaned
                break

        section_title = f"{doc_title} (Page {idx})"
        if first_line and len(first_line) < 60:
            section_title = f"{doc_title} (Page {idx} - {first_line})"

        sections.append({
            "document": file_path.name,
            "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
            "format": "pdf",
            "title": section_title,
            "content": page_text,
            "page": idx
        })

    return sections


def _extract_sections(file_path: Path) -> List[Dict[str, Any]]:
    """Universal section extractor dispatcher based on file extension."""
    if not file_path.exists():
        return []

    suffix = file_path.suffix.lower()
    if suffix == ".md":
        return _extract_md_sections(file_path)
    elif suffix in [".html", ".htm"]:
        return _extract_html_sections(file_path)
    elif suffix == ".pdf":
        return _extract_pdf_sections(file_path)
    return []


def search_docs(query: str, category: str = "") -> dict:
    """Searches the official documentation (Markdown, HTML, or PDF) for answers to user questions.

    Args:
        query: The search keywords, topic, or question (e.g., 'refund policy', 'reset password', 'API error 401', 'pro plan pricing').
        category: Optional category or filename filter (e.g., 'billing', 'troubleshooting', 'api', 'faq', 'getting_started').

    Returns:
        A dictionary with matching documentation snippets, source filenames, section titles, and citations.
    """
    if not DOCS_ROOT.exists():
        return {
            "status": "error",
            "message": f"Documentation root directory not found at {DOCS_ROOT}"
        }

    files = _get_active_files(category=category)
    if not files:
        return {
            "status": "no_results",
            "query": query,
            "active_mode": ACTIVE_DOC_MODE,
            "message": f"No documentation files found for mode '{ACTIVE_DOC_MODE}'" + (f" with category '{category}'" if category else ".")
        }

    query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    if not query_terms:
        query_terms = [t.lower() for t in re.findall(r"\w+", query)]

    results = []

    for file_path in files:
        doc_sections = _extract_sections(file_path)
        for sec in doc_sections:
            title = sec["title"]
            body = sec["content"]
            full_text = f"{title}\n{body}".lower()

            score = 0
            # Full phrase match bonus
            if query.lower() in full_text:
                score += 30
            
            # Match in title bonus
            for term in query_terms:
                if term in title.lower():
                    score += 15
                if term in body.lower():
                    score += min(body.lower().count(term) * 3, 20)

            if score > 0:
                # Prepare a preview snippet around the match
                snippet = body[:500] + "..." if len(body) > 500 else body
                
                # Format standard citation string
                rel_path = sec["relative_path"]
                page_info = f", Page {sec['page']}" if sec.get("page") else ""
                citation = f"docs/{rel_path}{page_info} ({title})"

                results.append({
                    "document": sec["document"],
                    "relative_path": rel_path,
                    "format": sec["format"],
                    "section_title": title,
                    "page": sec.get("page"),
                    "citation": citation,
                    "score": score,
                    "snippet": snippet,
                    "content": body
                })

    # Sort by relevance score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:4]

    if not top_results:
        return {
            "status": "no_results",
            "query": query,
            "active_mode": ACTIVE_DOC_MODE,
            "message": f"No matching documentation found for '{query}' in {ACTIVE_DOC_MODE} mode."
        }

    return {
        "status": "success",
        "query": query,
        "active_mode": ACTIVE_DOC_MODE,
        "results_count": len(top_results),
        "matches": top_results
    }


def get_doc_content(
    document_name: str,
    section_title: str = "",
    page: Optional[int] = None
) -> dict:
    """Retrieves full text, specific section, or PDF page from a documentation file.

    Args:
        document_name: The filename of the document (e.g. 'billing_and_subscriptions.pdf', 'troubleshooting.html', 'getting_started.md').
        section_title: Optional title or keyword of the specific section to retrieve.
        page: Optional page number for PDF files (1-indexed).

    Returns:
        The content of the requested document, section, or page.
    """
    files = _get_active_files()
    
    # Try exact match or match without extension
    target_file = None
    clean_doc_name = document_name.lower().strip()
    
    for f in files:
        if f.name.lower() == clean_doc_name or f.stem.lower() == clean_doc_name.split(".")[0]:
            target_file = f
            break

    # If not found in active files, search entire docs folder
    if not target_file:
        for f in DOCS_ROOT.glob("**/*"):
            if f.is_file() and (f.name.lower() == clean_doc_name or f.stem.lower() == clean_doc_name.split(".")[0]):
                target_file = f
                break

    if not target_file:
        available = [f.name for f in files]
        return {
            "status": "error",
            "message": f"Document '{document_name}' not found.",
            "active_mode": ACTIVE_DOC_MODE,
            "available_documents": available
        }

    sections = _extract_sections(target_file)
    
    # If specific page requested for PDF
    if page is not None:
        page_sections = [s for s in sections if s.get("page") == page]
        if page_sections:
            return {
                "status": "success",
                "document": target_file.name,
                "format": page_sections[0]["format"],
                "page": page,
                "title": page_sections[0]["title"],
                "content": page_sections[0]["content"]
            }
        return {
            "status": "error",
            "message": f"Page {page} not found in {target_file.name}. Total pages: {len(sections)}",
            "total_pages": len(sections)
        }

    # If specific section requested
    if section_title:
        for sec in sections:
            if section_title.lower() in sec["title"].lower():
                return {
                    "status": "success",
                    "document": target_file.name,
                    "format": sec["format"],
                    "section_title": sec["title"],
                    "page": sec.get("page"),
                    "content": sec["content"]
                }
        return {
            "status": "error",
            "message": f"Section '{section_title}' not found in {target_file.name}.",
            "available_sections": [s["title"] for s in sections]
        }

    # Return full content
    full_content = "\n\n---\n\n".join([f"### {s['title']}\n{s['content']}" for s in sections])
    return {
        "status": "success",
        "document": target_file.name,
        "format": sections[0]["format"] if sections else target_file.suffix,
        "relative_path": str(target_file.relative_to(DOCS_ROOT)).replace("\\", "/"),
        "total_sections": len(sections),
        "content": full_content
    }


def list_available_docs() -> dict:
    """Lists all available documentation files, their formats, and sections in the active mode."""
    if not DOCS_ROOT.exists():
        return {"status": "error", "message": "Docs directory does not exist."}

    files = _get_active_files()
    catalog = []

    for file_path in files:
        sections = _extract_sections(file_path)
        catalog.append({
            "filename": file_path.name,
            "relative_path": str(file_path.relative_to(DOCS_ROOT)).replace("\\", "/"),
            "format": file_path.suffix.lstrip(".").lower(),
            "title": file_path.stem.replace("_", " ").title(),
            "total_sections_or_pages": len(sections),
            "sections": [s["title"] for s in sections]
        })

    return {
        "status": "success",
        "active_mode": ACTIVE_DOC_MODE,
        "total_documents": len(catalog),
        "catalog": catalog
    }


def escalate_ticket(
    user_email: str,
    issue_title: str,
    issue_description: str,
    priority: str = "medium"
) -> dict:
    """Escalates an unresolved issue or user request to a human support specialist.

    Args:
        user_email: The customer's contact email.
        issue_title: Brief summary of the problem.
        issue_description: Full details of the issue and steps already tried.
        priority: Urgency level ('low', 'medium', 'high', 'critical').

    Returns:
        Ticket creation confirmation with a reference number and SLA estimate.
    """
    ticket_id = f"TICKET-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sla_map = {
        "critical": "1 hour",
        "high": "4 hours",
        "medium": "24 hours",
        "low": "48 hours"
    }

    return {
        "status": "created",
        "ticket_id": ticket_id,
        "user_email": user_email,
        "issue_title": issue_title,
        "priority": priority.lower(),
        "created_at": created_at,
        "estimated_sla": sla_map.get(priority.lower(), "24 hours"),
        "message": f"Support ticket {ticket_id} has been created and assigned to a support specialist."
    }
