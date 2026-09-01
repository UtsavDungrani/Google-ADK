"""
FastAPI Backend Server for Customer Care Chatbot & Vendor Portal
Connects React UI with Google ADK root_agent Runner, MongoDB ticket store, and MongoDB chat sessions.
"""

import os
import sys
import uuid
import datetime
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

# Setup parent path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

try:
    from .agent import root_agent
    from .db import (
        is_mongo_connected,
        MONGODB_DB_NAME,
        get_chat_sessions_collection,
        serialize_doc,
        serialize_docs
    )
    from .ticket_service import (
        list_tickets,
        get_ticket,
        update_vendor_response,
        close_ticket
    )
except (ImportError, ValueError):
    from agent import root_agent
    from db import (
        is_mongo_connected,
        MONGODB_DB_NAME,
        get_chat_sessions_collection,
        serialize_doc,
        serialize_docs
    )
    from ticket_service import (
        list_tickets,
        get_ticket,
        update_vendor_response,
        close_ticket
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("customer_care.server")

app = FastAPI(
    title="Customer Care & Support Portal API",
    description="Backend API powering Customer Care Chatbot & Vendor Desk",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK Session Service and Runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="customer_care",
    agent=root_agent,
    session_service=session_service
)

_SESSIONS_REGISTRY: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "cust_user_default"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    session_state: Dict[str, Any]
    status: str = "success"


class VendorReplyRequest(BaseModel):
    response: str
    responder_name: Optional[str] = "Authorized Support Specialist"
    status: Optional[str] = "Vendor Responded"


@app.get("/api/health")
def health_check():
    """Health status and database connectivity check."""
    return {
        "status": "healthy",
        "agent": root_agent.name,
        "database": MONGODB_DB_NAME,
        "mongodb_connected": is_mongo_connected()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Processes user chat input through Google ADK root_agent and persists chat turn to MongoDB."""
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    user_id = req.user_id or "cust_user_default"
    session_id = req.session_id

    if not session_id or session_id not in _SESSIONS_REGISTRY:
        session = await session_service.create_session(app_name="customer_care", user_id=user_id)
        session_id = session.id
        _SESSIONS_REGISTRY[session_id] = session

    session_obj = _SESSIONS_REGISTRY[session_id]

    try:
        msg_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_msg)]
        )

        response_chunks: List[str] = []

        async for event in runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=msg_content
        ):
            if hasattr(event, "message") and event.message and event.message.parts:
                for part in event.message.parts:
                    if part.text:
                        response_chunks.append(part.text)

        full_response = "".join(response_chunks).strip()
        if not full_response:
            full_response = "I have processed your request. Please let me know if you need any additional assistance!"

        current_state = {}
        if hasattr(session_obj, "state") and session_obj.state:
            current_state = dict(session_obj.state)

        # Persist conversation turn to MongoDB chat_sessions
        if is_mongo_connected():
            try:
                col = get_chat_sessions_collection()
                if col is not None:
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    existing = col.find_one({"session_id": session_id})
                    
                    user_turn = {
                        "id": f"user-{uuid.uuid4().hex[:6]}",
                        "role": "user",
                        "text": user_msg,
                        "timestamp": datetime.datetime.now().strftime("%H:%M")
                    }
                    bot_turn = {
                        "id": f"bot-{uuid.uuid4().hex[:6]}",
                        "role": "assistant",
                        "text": full_response,
                        "timestamp": datetime.datetime.now().strftime("%H:%M")
                    }

                    if existing:
                        messages = existing.get("messages", [])
                        messages.append(user_turn)
                        messages.append(bot_turn)
                        col.update_one(
                            {"session_id": session_id},
                            {"$set": {
                                "messages": messages,
                                "state": current_state,
                                "updated_at": now_ts,
                                "preview": user_msg[:60]
                            }}
                        )
                    else:
                        title = user_msg[:45] + ("..." if len(user_msg) > 45 else "")
                        col.insert_one({
                            "session_id": session_id,
                            "user_id": user_id,
                            "title": title,
                            "preview": user_msg[:60],
                            "messages": [user_turn, bot_turn],
                            "state": current_state,
                            "created_at": now_ts,
                            "updated_at": now_ts
                        })
            except Exception as e:
                logger.warning(f"Failed to persist chat history to MongoDB: {e}")

        return ChatResponse(
            response=full_response,
            session_id=session_id,
            user_id=user_id,
            session_state=current_state,
            status="success"
        )

    except Exception as e:
        logger.error(f"Error during ADK execution: {e}", exc_info=True)
        return ChatResponse(
            response="I apologize, but I encountered an error while processing your request. Please try again.",
            session_id=session_id,
            user_id=user_id,
            session_state={},
            status="error"
        )


# -------------------------------------------------------------
# CHAT SESSIONS & HISTORY ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/chats")
def get_chat_sessions(user_id: Optional[str] = "cust_user_default"):
    """Returns list of previous chat sessions for the user."""
    if not is_mongo_connected():
        return {"status": "success", "sessions": []}

    try:
        col = get_chat_sessions_collection()
        if col is None:
            return {"status": "success", "sessions": []}

        cursor = col.find({}, {"messages": 0}).sort("updated_at", -1).limit(50)
        sessions = serialize_docs(list(cursor))
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        return {"status": "error", "sessions": []}


@app.get("/api/chats/{session_id}")
def get_chat_session(session_id: str):
    """Retrieves full conversation history and state for a session."""
    if not is_mongo_connected():
        raise HTTPException(status_code=404, detail="Database offline")

    try:
        col = get_chat_sessions_collection()
        if col is None:
            raise HTTPException(status_code=404, detail="Database offline")

        doc = col.find_one({"session_id": session_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"status": "success", "session": serialize_doc(doc)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chats/{session_id}")
def delete_chat_session(session_id: str):
    """Deletes a chat session from MongoDB."""
    if not is_mongo_connected():
        return {"status": "success"}

    try:
        col = get_chat_sessions_collection()
        if col is not None:
            col.delete_one({"session_id": session_id})
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return {"status": "error"}


# -------------------------------------------------------------
# VENDOR TICKETING ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/tickets")
def get_all_tickets(
    customer_id: Optional[str] = None,
    order_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Lists all support tickets from MongoDB."""
    tickets = list_tickets(customer_id=customer_id, order_id=order_id, status=status)
    return {
        "status": "success",
        "total": len(tickets),
        "tickets": tickets
    }


@app.get("/api/tickets/{ticket_id}")
def get_single_ticket(ticket_id: str):
    """Retrieves a single ticket by ID."""
    t = get_ticket(ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "success", "ticket": t}


@app.post("/api/tickets/{ticket_id}/reply")
def reply_to_ticket(ticket_id: str, req: VendorReplyRequest):
    """Records an official vendor resolution to an open ticket in MongoDB."""
    if not req.response.strip():
        raise HTTPException(status_code=400, detail="Response text cannot be empty.")

    updated = update_vendor_response(
        ticket_id=ticket_id,
        vendor_response=req.response.strip(),
        vendor_responder_name=req.responder_name or "Authorized Support Specialist",
        status=req.status or "Vendor Responded"
    )

    if not updated:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

    return {
        "status": "success",
        "message": f"Response recorded for ticket {ticket_id}.",
        "ticket": updated
    }


@app.post("/api/tickets/{ticket_id}/close")
def close_single_ticket(ticket_id: str):
    """Marks a ticket as Closed."""
    updated = close_ticket(ticket_id=ticket_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
    return {"status": "success", "ticket": updated}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8080, reload=True)
