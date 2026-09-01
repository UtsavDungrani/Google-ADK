/**
 * Centralized API Service for Customer Care Chatbot, History, & Vendor Desk
 */

const API_BASE = '/api';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    return { status: 'offline', mongodb_connected: false };
  }
}

export async function sendChatMessage(message, sessionId = null, userId = 'cust_web_user') {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: userId,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function fetchChatSessions() {
  try {
    const res = await fetch(`${API_BASE}/chats`);
    if (!res.ok) throw new Error('Failed to fetch chat sessions');
    return await res.json();
  } catch (err) {
    console.error('Error loading chat history:', err);
    return { status: 'error', sessions: [] };
  }
}

export async function fetchChatSession(sessionId) {
  const res = await fetch(`${API_BASE}/chats/${encodeURIComponent(sessionId)}`);
  if (!res.ok) throw new Error('Failed to load conversation');
  return await res.json();
}

export async function deleteChatSession(sessionId) {
  const res = await fetch(`${API_BASE}/chats/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete session');
  return await res.json();
}

export async function fetchTicket(ticketId) {
  const res = await fetch(`${API_BASE}/tickets/${encodeURIComponent(ticketId)}`);
  if (!res.ok) throw new Error('Failed to fetch ticket details');
  return await res.json();
}

export async function fetchTickets(status = null) {
  try {
    const url = status ? `${API_BASE}/tickets?status=${encodeURIComponent(status)}` : `${API_BASE}/tickets`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return await res.json();
  } catch (err) {
    console.error('Error loading tickets:', err);
    return { status: 'error', tickets: [] };
  }
}

export async function replyToTicket(ticketId, responseText, responderName = 'Support Lead', status = 'Vendor Responded') {
  const res = await fetch(`${API_BASE}/tickets/${encodeURIComponent(ticketId)}/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      response: responseText,
      responder_name: responderName,
      status: status,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to submit response');
  }

  return await res.json();
}

export async function closeTicket(ticketId) {
  const res = await fetch(`${API_BASE}/tickets/${encodeURIComponent(ticketId)}/close`, {
    method: 'POST',
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to close ticket');
  }

  return await res.json();
}
