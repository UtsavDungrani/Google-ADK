import React, { useState, useEffect } from 'react';
import { 
  Ticket, 
  Search, 
  Clock, 
  CheckCircle2, 
  Send, 
  RefreshCw, 
  User, 
  Mail, 
  Phone, 
  Package, 
  AlertCircle 
} from 'lucide-react';
import { fetchTickets, replyToTicket, closeTicket } from '../services/api';

export default function VendorPortal() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [statusFilter, setStatusFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Reply form state
  const [replyText, setReplyText] = useState('');
  const [responderName, setResponderName] = useState('Authorized Support Lead');
  const [replyStatus, setReplyStatus] = useState('Vendor Responded');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const loadTickets = async () => {
    setLoading(true);
    const data = await fetchTickets();
    if (data && data.tickets) {
      setTickets(data.tickets);
      if (selectedTicket) {
        const updated = data.tickets.find((t) => t.ticket_id === selectedTicket.ticket_id);
        if (updated) setSelectedTicket(updated);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleSelectTicket = (t) => {
    setSelectedTicket(t);
    setReplyText(t.vendor_response || '');
    setSuccessMsg('');
  };

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!selectedTicket || !replyText.trim() || submitting) return;

    setSubmitting(true);
    try {
      await replyToTicket(
        selectedTicket.ticket_id,
        replyText.trim(),
        responderName.trim(),
        replyStatus
      );
      setSuccessMsg('Resolution saved to MongoDB!');
      await loadTickets();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      alert(`Error submitting reply: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCloseTicket = async () => {
    if (!selectedTicket || submitting) return;
    setSubmitting(true);
    try {
      await closeTicket(selectedTicket.ticket_id);
      setSuccessMsg('Ticket closed in MongoDB.');
      await loadTickets();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      alert(`Error closing ticket: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  // Filtered tickets list
  const filteredTickets = tickets.filter((t) => {
    const matchesStatus = 
      statusFilter === 'All' 
        ? true 
        : statusFilter === 'Pending' 
        ? t.status?.toLowerCase().includes('pending')
        : statusFilter === 'Responded'
        ? t.status?.toLowerCase().includes('responded')
        : t.status?.toLowerCase().includes('closed');

    const matchesSearch = 
      !searchQuery.trim() ||
      t.ticket_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.order_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.subject?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesSearch;
  });

  return (
    <div className="flex h-full w-full overflow-hidden bg-zinc-950 text-zinc-100">
      
      {/* Left Column: Tickets List */}
      <div className="flex w-full md:w-96 flex-col border-r border-zinc-800 bg-zinc-900/50">
        
        {/* Search & Filter Header */}
        <div className="border-b border-zinc-800 p-3 space-y-2.5">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Support Desk Tickets ({filteredTickets.length})
            </h2>
            <button
              onClick={loadTickets}
              disabled={loading}
              className="text-zinc-400 hover:text-zinc-200 text-xs flex items-center gap-1 p-1 rounded hover:bg-zinc-800 transition-colors"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Search by ticket, order, or customer..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-md border border-zinc-800 bg-zinc-950 py-1.5 pl-8 pr-3 text-xs text-zinc-200 placeholder-zinc-500 focus:border-zinc-700 focus:outline-none"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex gap-1.5 text-[11px]">
            {['All', 'Pending', 'Responded', 'Closed'].map((f) => (
              <button
                key={f}
                onClick={() => setStatusFilter(f)}
                className={`rounded-md px-2.5 py-1 transition-colors ${
                  statusFilter === f
                    ? 'bg-zinc-800 font-medium text-zinc-100 border border-zinc-700'
                    : 'text-zinc-400 hover:bg-zinc-800/50'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Tickets Scrollable Feed */}
        <div className="flex-1 overflow-y-auto divide-y divide-zinc-800/60">
          {loading && tickets.length === 0 ? (
            <div className="p-6 text-center text-xs text-zinc-500">Loading tickets from MongoDB...</div>
          ) : filteredTickets.length === 0 ? (
            <div className="p-6 text-center text-xs text-zinc-500">No matching tickets found.</div>
          ) : (
            filteredTickets.map((t) => {
              const isSelected = selectedTicket?.ticket_id === t.ticket_id;
              const isPending = t.status?.toLowerCase().includes('pending');
              const isResponded = t.status?.toLowerCase().includes('responded');

              return (
                <div
                  key={t.ticket_id}
                  onClick={() => handleSelectTicket(t)}
                  className={`cursor-pointer p-3.5 transition-colors ${
                    isSelected ? 'bg-zinc-800/90' : 'hover:bg-zinc-900/80'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs font-semibold text-zinc-200">{t.ticket_id}</span>
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                      isPending 
                        ? 'bg-amber-950/80 text-amber-300 border border-amber-800/50' 
                        : isResponded 
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/50'
                        : 'bg-zinc-800 text-zinc-400'
                    }`}>
                      {t.status}
                    </span>
                  </div>

                  <div className="mt-1 font-medium text-xs text-zinc-300 truncate">
                    {t.subject || t.description}
                  </div>

                  <div className="mt-1.5 flex items-center justify-between text-[11px] text-zinc-500">
                    <span>{t.customer_name || 'Customer'}</span>
                    <span className="font-mono">{t.order_id || 'N/A'}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Column: Ticket Inspection & Reply Form */}
      <div className="hidden md:flex flex-1 flex-col overflow-y-auto bg-zinc-950 p-6">
        {selectedTicket ? (
          <div className="max-w-2xl space-y-5">
            
            {/* Ticket Header */}
            <div className="flex items-start justify-between border-b border-zinc-800 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="font-mono text-base font-bold text-zinc-100">{selectedTicket.ticket_id}</h1>
                  <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300 border border-zinc-700">
                    {selectedTicket.category || 'General Support'}
                  </span>
                </div>
                <h2 className="mt-1 text-sm font-semibold text-zinc-200">
                  {selectedTicket.subject || 'Support Request'}
                </h2>
              </div>

              <div className="text-right">
                <span className="text-xs text-zinc-400">Status</span>
                <div className="font-semibold text-xs text-zinc-200">{selectedTicket.status}</div>
              </div>
            </div>

            {/* Customer Details Box */}
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3.5 text-xs grid grid-cols-2 gap-3">
              <div>
                <span className="text-zinc-500">Customer:</span>
                <div className="font-medium text-zinc-200 mt-0.5">{selectedTicket.customer_name} ({selectedTicket.customer_id})</div>
              </div>
              <div>
                <span className="text-zinc-500">Linked Order:</span>
                <div className="font-mono font-medium text-zinc-200 mt-0.5">{selectedTicket.order_id}</div>
              </div>
              <div>
                <span className="text-zinc-500">Product:</span>
                <div className="text-zinc-200 mt-0.5">{selectedTicket.product_name || 'N/A'}</div>
              </div>
              <div>
                <span className="text-zinc-500">Created:</span>
                <div className="text-zinc-200 mt-0.5">{selectedTicket.created_at}</div>
              </div>
            </div>

            {/* Customer Issue Description */}
            <div>
              <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Customer Inquiry</label>
              <div className="mt-1.5 rounded-lg border border-zinc-800 bg-zinc-900/80 p-3.5 text-xs text-zinc-200 leading-relaxed whitespace-pre-wrap">
                {selectedTicket.description}
              </div>
            </div>

            {/* Existing Vendor Response Display */}
            {selectedTicket.vendor_response && (
              <div className="rounded-lg border border-emerald-800/40 bg-emerald-950/20 p-3.5 text-xs">
                <div className="font-semibold text-emerald-400 flex items-center justify-between">
                  <span>Current Resolution</span>
                  <span className="text-emerald-300/70 font-normal">by {selectedTicket.vendor_responder_name || 'Specialist'}</span>
                </div>
                <p className="mt-1.5 text-zinc-200 leading-relaxed whitespace-pre-wrap">
                  {selectedTicket.vendor_response}
                </p>
              </div>
            )}

            {/* Reply / Resolve Form */}
            <form onSubmit={handleSendReply} className="space-y-3.5 border-t border-zinc-800 pt-4">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">Submit Official Resolution</label>
                {successMsg && <span className="text-xs font-medium text-emerald-400">{successMsg}</span>}
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-zinc-400 block mb-1">Your Name & Role</label>
                  <input
                    type="text"
                    value={responderName}
                    onChange={(e) => setResponderName(e.target.value)}
                    placeholder="e.g. Sarah Chen - Senior Hardware Lead"
                    className="w-full rounded-md border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 focus:border-zinc-700 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">Update Status To</label>
                  <select
                    value={replyStatus}
                    onChange={(e) => setReplyStatus(e.target.value)}
                    className="w-full rounded-md border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 focus:border-zinc-700 focus:outline-none"
                  >
                    <option value="Vendor Responded">Vendor Responded</option>
                    <option value="Closed">Closed / Resolved</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-zinc-400 block mb-1 text-xs">Technical Explanation / Solution for Customer</label>
                <textarea
                  rows={4}
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Provide technical diagnosis, firmware instructions, replacement terms, or resolution..."
                  className="w-full rounded-md border border-zinc-800 bg-zinc-900 p-3 text-xs text-zinc-200 placeholder-zinc-500 focus:border-zinc-700 focus:outline-none leading-relaxed"
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <button
                  type="button"
                  onClick={handleCloseTicket}
                  disabled={submitting}
                  className="rounded-md border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 text-xs text-zinc-300 transition-colors"
                >
                  Close Ticket
                </button>

                <button
                  type="submit"
                  disabled={!replyText.trim() || submitting}
                  className="flex items-center gap-1.5 rounded-md bg-blue-600 hover:bg-blue-500 px-4 py-1.5 text-xs font-semibold text-white transition-colors disabled:opacity-40"
                >
                  <Send className="h-3.5 w-3.5" />
                  <span>{submitting ? 'Saving...' : 'Save & Publish Resolution'}</span>
                </button>
              </div>
            </form>

          </div>
        ) : (
          <div className="flex h-full flex-col items-center justify-center text-center text-zinc-500 text-xs">
            <Ticket className="h-8 w-8 text-zinc-700 mb-2" />
            <p>Select a ticket from the left panel to inspect and submit resolutions.</p>
          </div>
        )}
      </div>

    </div>
  );
}
