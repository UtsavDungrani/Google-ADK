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

// -------------------------------------------------------------
// FAQ KNOWLEDGE RAG & SYSTEM ARCHITECTURE APIs
// -------------------------------------------------------------

export async function searchFaqApi(query, category = 'All', topK = 4) {
  try {
    const url = `${API_BASE}/faq/search?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&top_k=${topK}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to search FAQ knowledge base');
    return await res.json();
  } catch (err) {
    console.error('Error searching FAQ:', err);
    return { status: 'error', faq_results: [] };
  }
}

export async function addFaqApi(question, answer, category = 'General Support') {
  const res = await fetch(`${API_BASE}/faq/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, answer, category }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to add FAQ to RAG vector store');
  }
  return await res.json();
}

export async function fetchFaqCategoriesApi() {
  try {
    const res = await fetch(`${API_BASE}/faq/categories`);
    if (!res.ok) throw new Error('Failed to fetch FAQ categories');
    return await res.json();
  } catch (err) {
    return { indexed_categories: [], total_chunks: 0 };
  }
}

export async function fetchSystemStatsApi() {
  try {
    const res = await fetch(`${API_BASE}/stats/system`);
    if (!res.ok) throw new Error('Failed to fetch system stats');
    return await res.json();
  } catch (err) {
    return { status: 'error' };
  }
}

export async function listFaqsApi(category = 'All') {
  try {
    const url = `${API_BASE}/faq/list?category=${encodeURIComponent(category)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch MongoDB FAQs');
    return await res.json();
  } catch (err) {
    return { status: 'error', faqs: [] };
  }
}

export async function deleteFaqApi(faqId) {
  const res = await fetch(`${API_BASE}/faq/${encodeURIComponent(faqId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete FAQ');
  return await res.json();
}

export async function fetchContextMetricsApi() {
  try {
    const res = await fetch(`${API_BASE}/stats/context-metrics`);
    if (!res.ok) throw new Error('Failed to fetch context metrics');
    return await res.json();
  } catch (err) {
    return { status: 'error' };
  }
}

// -------------------------------------------------------------
// CROSS-SESSION LONG-TERM MEMORY APIs
// -------------------------------------------------------------

export async function fetchCustomerProfilesApi() {
  try {
    const res = await fetch(`${API_BASE}/customer/profiles`);
    if (!res.ok) throw new Error('Failed to fetch customer profiles');
    return await res.json();
  } catch (err) {
    console.error('Error loading profiles:', err);
    return { status: 'error', profiles: [] };
  }
}

export async function fetchCustomerProfileApi(userId) {
  try {
    const res = await fetch(`${API_BASE}/customer/profile?user_id=${encodeURIComponent(userId)}`);
    if (!res.ok) throw new Error('Failed to fetch customer profile');
    return await res.json();
  } catch (err) {
    console.error('Error loading customer profile:', err);
    return { status: 'error', profile: null, episodes: [] };
  }
}

export async function addCustomerNoteApi(userId, note) {
  const res = await fetch(`${API_BASE}/customer/note`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, note }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to add note');
  }
  return await res.json();
}

export async function fetchCustomerEpisodesApi(userId, limit = 10) {
  try {
    const res = await fetch(`${API_BASE}/customer/episodes?user_id=${encodeURIComponent(userId)}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch customer episodes');
    return await res.json();
  } catch (err) {
    console.error('Error loading customer episodes:', err);
    return { status: 'error', episodes: [] };
  }
}

// -------------------------------------------------------------
// DYNAMIC FEW-SHOT RAG APIs
// -------------------------------------------------------------

export async function fetchFewShotExemplarsApi(category = 'All') {
  try {
    const url = category && category !== 'All' 
      ? `${API_BASE}/few-shot/exemplars?category=${encodeURIComponent(category)}`
      : `${API_BASE}/few-shot/exemplars`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch few-shot exemplars');
    return await res.json();
  } catch (err) {
    console.error('Error loading exemplars:', err);
    return { status: 'error', exemplars: [] };
  }
}

export async function searchFewShotExemplarsApi(query, category = 'All', topK = 3) {
  try {
    const url = `${API_BASE}/few-shot/search?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&top_k=${topK}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to search exemplars');
    return await res.json();
  } catch (err) {
    console.error('Error searching exemplars:', err);
    return { status: 'error', matches: [] };
  }
}

export async function addFewShotExemplarApi(exemplarData) {
  const res = await fetch(`${API_BASE}/few-shot/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(exemplarData),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to add gold exemplar');
  }
  return await res.json();
}

export async function deleteFewShotExemplarApi(exemplarId) {
  const res = await fetch(`${API_BASE}/few-shot/${encodeURIComponent(exemplarId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to delete exemplar');
  }
  return await res.json();
}

// -------------------------------------------------------------
// MULTILINGUAL NLP & CROSS-LINGUAL RAG APIs
// -------------------------------------------------------------

export async function detectLanguageApi(text) {
  try {
    const res = await fetch(`${API_BASE}/nlp/detect-language`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error('Failed to detect language');
    return await res.json();
  } catch (err) {
    console.error('Error detecting language:', err);
    return { status: 'error', analysis: { language: 'en', name: 'English', confidence: 1.0 } };
  }
}

export async function crossLingualSearchApi(query, category = 'All') {
  try {
    const res = await fetch(`${API_BASE}/nlp/cross-lingual-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, category }),
    });
    if (!res.ok) throw new Error('Failed to perform cross-lingual search');
    return await res.json();
  } catch (err) {
    console.error('Error in cross-lingual search:', err);
    return { status: 'error', matches_count: 0, exemplars: [] };
  }
}

export async function fetchSupportedLanguagesApi() {
  try {
    const res = await fetch(`${API_BASE}/nlp/supported-languages`);
    if (!res.ok) throw new Error('Failed to fetch supported languages');
    return await res.json();
  } catch (err) {
    console.error('Error loading languages:', err);
    return { status: 'error', languages: {} };
  }
}




