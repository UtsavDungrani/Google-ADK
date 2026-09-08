"""
Cross-Session Long-Term Memory Service for Post-Purchase Customer Care
Implements a cognitive memory architecture combining:
1. Semantic Memory (Persistent customer traits, preferences, owned devices, churn risk)
2. Episodic Memory (Chronological interaction timeline across past conversation sessions)
3. Recall Synthesizer (Contextual prompt injection for personalized return visits)
4. Memory Consolidation (Distillation of active session turns into permanent memory)
"""

import os
import re
import json
import uuid
import datetime
import logging
from typing import Dict, List, Any, Optional

try:
    from .db import (
        is_mongo_connected,
        get_profiles_collection,
        get_episodes_collection,
        serialize_doc,
        serialize_docs,
        SEED_PROFILES,
        SEED_EPISODES
    )
except (ImportError, ValueError):
    from db import (
        is_mongo_connected,
        get_profiles_collection,
        get_episodes_collection,
        serialize_doc,
        serialize_docs,
        SEED_PROFILES,
        SEED_EPISODES
    )

logger = logging.getLogger("customer_care.memory_service")

PROFILES_FILE_PATH = os.path.join(os.path.dirname(__file__), ".adk", "customer_profiles.json")
EPISODES_FILE_PATH = os.path.join(os.path.dirname(__file__), ".adk", "customer_episodes.json")

_FALLBACK_SEED_PROFILES: Dict[str, Dict[str, Any]] = {
    p["customer_id"]: p for p in SEED_PROFILES
}

_FALLBACK_SEED_EPISODES: List[Dict[str, Any]] = list(SEED_EPISODES)


def _ensure_memory_fallback_files():
    """Ensures fallback JSON files exist in .adk directory for offline resilience."""
    os.makedirs(os.path.dirname(PROFILES_FILE_PATH), exist_ok=True)
    if not os.path.exists(PROFILES_FILE_PATH):
        try:
            with open(PROFILES_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(_FALLBACK_SEED_PROFILES, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to initialize profiles fallback file: {e}")

    if not os.path.exists(EPISODES_FILE_PATH):
        try:
            with open(EPISODES_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(_FALLBACK_SEED_EPISODES, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to initialize episodes fallback file: {e}")


def _load_fallback_profiles() -> Dict[str, Dict[str, Any]]:
    """Loads profiles from fallback JSON file."""
    _ensure_memory_fallback_files()
    try:
        with open(PROFILES_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(_FALLBACK_SEED_PROFILES)


def _save_fallback_profiles(profiles: Dict[str, Dict[str, Any]]):
    """Saves profiles to fallback JSON file."""
    _ensure_memory_fallback_files()
    try:
        with open(PROFILES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write to profiles fallback file: {e}")


def _load_fallback_episodes() -> List[Dict[str, Any]]:
    """Loads episodes from fallback JSON file."""
    _ensure_memory_fallback_files()
    try:
        with open(EPISODES_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return list(_FALLBACK_SEED_EPISODES)


def _save_fallback_episodes(episodes: List[Dict[str, Any]]):
    """Saves episodes to fallback JSON file."""
    _ensure_memory_fallback_files()
    try:
        with open(EPISODES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(episodes, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write to episodes fallback file: {e}")


# -------------------------------------------------------------
# Core Profile (Semantic Memory) Operations
# -------------------------------------------------------------

def get_customer_profile(identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieves customer semantic memory profile by ID, Email, Name, or Order ID.

    Args:
        identifier: Search key (e.g. 'CUST-9921', 'alex.mercer@example.com', 'Alex Mercer', or 'ORD-10021').

    Returns:
        Dict representing persistent customer profile or None if not found.
    """
    if not identifier or not str(identifier).strip():
        return None

    clean_id = str(identifier).strip()

    # 1. Query MongoDB if connected
    if is_mongo_connected():
        try:
            col = get_profiles_collection()
            if col is not None:
                # Query by customer_id or email
                doc = col.find_one({
                    "$or": [
                        {"customer_id": {"$regex": f"^{re.escape(clean_id)}$", "$options": "i"}},
                        {"customer_email": {"$regex": f"^{re.escape(clean_id)}$", "$options": "i"}},
                        {"customer_name": {"$regex": f"^{re.escape(clean_id)}$", "$options": "i"}},
                        {"owned_devices.order_id": {"$regex": f"^{re.escape(clean_id)}$", "$options": "i"}}
                    ]
                })
                if doc:
                    return serialize_doc(doc)
        except Exception as e:
            logger.warning(f"MongoDB query failed for customer profile '{identifier}': {e}")

    # 2. Query fallback store
    profiles = _load_fallback_profiles()
    clean_lower = clean_id.lower()

    for pid, p in profiles.items():
        if pid.lower() == clean_lower:
            return p
        if p.get("customer_email", "").lower() == clean_lower:
            return p
        if clean_lower in p.get("customer_name", "").lower():
            return p
        for dev in p.get("owned_devices", []):
            if dev.get("order_id", "").lower() == clean_lower:
                return p

    return None


def list_all_profiles() -> List[Dict[str, Any]]:
    """Lists all available customer profiles for persona selection and testing."""
    if is_mongo_connected():
        try:
            col = get_profiles_collection()
            if col is not None:
                docs = list(col.find({}).sort("customer_id", 1))
                if docs:
                    return serialize_docs(docs)
        except Exception as e:
            logger.warning(f"Failed to list profiles from MongoDB: {e}")

    profiles = _load_fallback_profiles()
    return list(profiles.values())


def save_customer_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Persists or updates customer semantic profile in MongoDB and fallback store."""
    cid = profile_data.get("customer_id")
    if not cid:
        cid = f"CUST-{uuid.uuid4().hex[:4].upper()}"
        profile_data["customer_id"] = cid

    # Ensure required fields
    profile_data.setdefault("persistent_notes", [])
    profile_data.setdefault("owned_devices", [])
    profile_data.setdefault("active_tickets", [])
    profile_data.setdefault("preferred_tone", "Friendly & Professional")
    profile_data.setdefault("preferred_language", "English")
    profile_data.setdefault("churn_risk", 0.2)
    profile_data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Save to MongoDB
    if is_mongo_connected():
        try:
            col = get_profiles_collection()
            if col is not None:
                col.update_one({"customer_id": cid}, {"$set": profile_data}, upsert=True)
        except Exception as e:
            logger.warning(f"Error saving profile '{cid}' to MongoDB: {e}")

    # 2. Save to Fallback file
    profiles = _load_fallback_profiles()
    profiles[cid] = profile_data
    _save_fallback_profiles(profiles)

    return profile_data


def add_customer_note(customer_id: str, note: str) -> bool:
    """Appends a new persistent note or learned fact to customer profile."""
    if not note or not note.strip():
        return False

    note_clean = note.strip()
    profile = get_customer_profile(customer_id)
    if not profile:
        return False

    notes = profile.get("persistent_notes", [])
    if note_clean not in notes:
        notes.append(note_clean)
        profile["persistent_notes"] = notes
        save_customer_profile(profile)
        return True

    return False


# -------------------------------------------------------------
# Episodic Memory Operations
# -------------------------------------------------------------

def record_customer_episode(
    customer_id: str,
    session_id: str,
    summary: str,
    topics: Optional[List[str]] = None,
    sentiment: str = "Neutral",
    resolved: bool = False
) -> Dict[str, Any]:
    """Records an episodic memory entry representing a consolidated interaction session."""
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ep_id = f"EPS-{customer_id.replace('CUST-', '')}-{uuid.uuid4().hex[:4].upper()}"

    episode = {
        "episode_id": ep_id,
        "customer_id": customer_id,
        "session_id": session_id,
        "timestamp": now_ts,
        "summary": summary.strip(),
        "topics": topics or [],
        "sentiment_at_conclusion": sentiment,
        "resolved": resolved
    }

    # 1. Save to MongoDB
    if is_mongo_connected():
        try:
            col = get_episodes_collection()
            if col is not None:
                col.insert_one(episode)
        except Exception as e:
            logger.warning(f"Error saving episode to MongoDB: {e}")

    # 2. Save to Fallback file
    episodes = _load_fallback_episodes()
    episodes.append(episode)
    _save_fallback_episodes(episodes)

    return episode


def get_customer_episodes(customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves recent chronological interaction episodes for a customer."""
    if not customer_id:
        return []

    # 1. MongoDB query
    if is_mongo_connected():
        try:
            col = get_episodes_collection()
            if col is not None:
                docs = list(col.find({"customer_id": customer_id}).sort("timestamp", -1).limit(limit))
                if docs:
                    return serialize_docs(docs)
        except Exception as e:
            logger.warning(f"Failed to query episodes from MongoDB: {e}")

    # 2. Fallback query
    all_episodes = _load_fallback_episodes()
    matched = [e for e in all_episodes if e.get("customer_id") == customer_id]
    matched.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return matched[:limit]


# -------------------------------------------------------------
# Cross-Session Context Synthesizer (For Prompt Injection)
# -------------------------------------------------------------

def format_cross_session_context(identifier: str) -> str:
    """Synthesizes customer profile, devices, open tickets, and recent episodes into a prompt-ready memory block.

    Args:
        identifier: Customer ID, email, name, or order ID.

    Returns:
        Formatted markdown block with long-term memory context.
    """
    profile = get_customer_profile(identifier)
    if not profile:
        return ""

    cid = profile.get("customer_id", "Unknown")
    cname = profile.get("customer_name", "Valued Customer")
    cemail = profile.get("customer_email", "N/A")
    tone = profile.get("preferred_tone", "Professional & Empathetic")
    lang = profile.get("preferred_language", "English")
    churn = profile.get("churn_risk_level", "Low")
    notes = profile.get("persistent_notes", [])
    devices = profile.get("owned_devices", [])
    tickets = profile.get("active_tickets", [])

    episodes = get_customer_episodes(cid, limit=3)

    lines = [
        "=== [CROSS-SESSION LONG-TERM CUSTOMER MEMORY RECALL] ===",
        f"• Identified Customer: {cname} (Customer ID: {cid})",
        f"• Contact Email: {cemail}",
        f"• Preferred Communication Tone: {tone} | Preferred Language: {lang}",
        f"• Churn Risk Trajectory: {churn}",
    ]

    if devices:
        lines.append("• Registered Customer Devices & Purchases:")
        for dev in devices:
            d_name = dev.get("item_name", "Item")
            d_order = dev.get("order_id", "N/A")
            d_sn = dev.get("serial_number", "N/A")
            lines.append(f"  - {d_name} (Order: {d_order}, S/N: {d_sn})")

    if tickets:
        lines.append(f"• Active / Associated Support Tickets: {', '.join(tickets)}")

    if notes:
        lines.append("• Persistent Customer Traits & Learned Facts:")
        for n in notes:
            lines.append(f"  - {n}")

    if episodes:
        lines.append("• Chronological Cross-Session Interaction History (Past Sessions):")
        for ep in episodes:
            ts = ep.get("timestamp", "Past Date")
            summary = ep.get("summary", "")
            sentiment = ep.get("sentiment_at_conclusion", "Neutral")
            resolved_str = "Resolved" if ep.get("resolved") else "Open / In Progress"
            lines.append(f"  - [{ts}] ({resolved_str}): {summary} (Valence: {sentiment})")

    lines.append("=== [END MEMORY RECALL: Personalize response using this history] ===")
    return "\n".join(lines)


# -------------------------------------------------------------
# Memory Consolidation Pipeline (Post-Turn / Session Conclusion)
# -------------------------------------------------------------

def consolidate_session_memory(
    session_id: str,
    user_id: str,
    messages: List[Dict[str, Any]],
    session_state: Dict[str, Any]
) -> Dict[str, Any]:
    """Distills the current conversation turn/session into long-term semantic and episodic memory.

    Args:
        session_id: The chat session ID.
        user_id: User/Customer ID.
        messages: List of message turns in the session.
        session_state: Current ADK ToolContext.state dictionary.

    Returns:
        Dict summarizing consolidation outcomes.
    """
    if not messages:
        return {"status": "skipped", "reason": "No messages in session."}

    # 1. Resolve customer identity
    profile = get_customer_profile(user_id)
    if not profile and session_state.get("customer_id"):
        profile = get_customer_profile(session_state["customer_id"])

    # If still not found, search messages for known order IDs or customer IDs
    if not profile:
        full_convo_text = " ".join([m.get("text", "") for m in messages])
        found_order = re.search(r"\b(ORD-\d{4,6})\b", full_convo_text, re.IGNORECASE)
        if found_order:
            profile = get_customer_profile(found_order.group(1).upper())

    if not profile:
        # Cannot associate with a permanent profile yet
        return {"status": "unassociated", "reason": f"No customer profile matches user_id '{user_id}'."}

    cid = profile["customer_id"]

    # 2. Extract conversation insights
    user_turns = [m.get("text", "") for m in messages if m.get("role") == "user"]
    bot_turns = [m.get("text", "") for m in messages if m.get("role") == "assistant"]

    last_user_msg = user_turns[-1] if user_turns else ""
    last_bot_msg = bot_turns[-1] if bot_turns else ""

    topics: List[str] = []
    convo_blob = " ".join(user_turns).lower()

    if "return" in convo_blob or "rma" in convo_blob:
        topics.append("Return / RMA")
    if "warranty" in convo_blob or "claim" in convo_blob or "defect" in convo_blob:
        topics.append("Warranty Claim")
    if "track" in convo_blob or "shipment" in convo_blob or "delivery" in convo_blob or "where" in convo_blob:
        topics.append("Order Logistics")
    if "wifi" in convo_blob or "wi-fi" in convo_blob or "error" in convo_blob or "tv-net" in convo_blob:
        topics.append("Technical Diagnostics")
    if "ticket" in convo_blob:
        topics.append("Vendor Support Ticket")
    if "credit" in convo_blob or "voucher" in convo_blob:
        topics.append("Courtesy Credit")

    if not topics:
        topics.append("General Customer Care")

    # Determine resolution status
    is_resolved = bool(
        "thank" in last_user_msg.lower() or
        "helped" in last_user_msg.lower() or
        "fixed" in last_user_msg.lower() or
        "label has been generated" in last_bot_msg.lower() or
        "claim has been filed" in last_bot_msg.lower() or
        "credit has been applied" in last_bot_msg.lower()
    )

    # 3. Create concise episode summary
    first_inquiry = user_turns[0] if user_turns else "General support inquiry"
    if len(first_inquiry) > 90:
        first_inquiry = first_inquiry[:90] + "..."

    summary_text = f"Inquired: '{first_inquiry}'."
    if session_state.get("active_ticket_id"):
        summary_text += f" Associated with Ticket {session_state['active_ticket_id']}."
    if session_state.get("rma_code"):
        summary_text += f" Return RMA {session_state['rma_code']} generated."
    if session_state.get("claim_id"):
        summary_text += f" Warranty Claim {session_state['claim_id']} dispatched."
    if session_state.get("issued_credits"):
        summary_text += f" Courtesy credit voucher issued."

    # Record the episode
    record_customer_episode(
        customer_id=cid,
        session_id=session_id,
        summary=summary_text,
        topics=topics,
        sentiment="Satisfied" if is_resolved else "Pending Resolution",
        resolved=is_resolved
    )

    # 4. Update Profile attributes & devices if newly mentioned
    updated_profile = dict(profile)
    updated_profile["last_interaction_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update active tickets if state has new ones
    if session_state.get("active_ticket_id"):
        tid = session_state["active_ticket_id"]
        if tid not in updated_profile.get("active_tickets", []):
            updated_profile.setdefault("active_tickets", []).append(tid)

    save_customer_profile(updated_profile)

    return {
        "status": "consolidated",
        "customer_id": cid,
        "topics": topics,
        "resolved": is_resolved,
        "summary": summary_text
    }
