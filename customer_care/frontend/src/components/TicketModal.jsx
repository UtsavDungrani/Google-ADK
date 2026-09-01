import React, { useState, useEffect } from 'react';
import { 
  X, 
  Ticket, 
  Clock, 
  User, 
  Package, 
  Check, 
  Copy, 
  AlertCircle, 
  Loader2,
  Building,
  CheckCircle2
} from 'lucide-react';
import { fetchTicket } from '../services/api';

export default function TicketModal({ ticketId, onClose }) {
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!ticketId) return;

    let isMounted = true;
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchTicket(ticketId);
        if (isMounted) {
          if (res && res.ticket) {
            setTicket(res.ticket);
          } else {
            setError('Ticket details not found.');
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch ticket.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadData();
    return () => { isMounted = false; };
  }, [ticketId]);

  // Handle ESC key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!ticketId) return null;

  const handleCopyId = () => {
    navigator.clipboard.writeText(ticketId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isResponded = ticket?.status?.toLowerCase().includes('responded');
  const isClosed = ticket?.status?.toLowerCase().includes('closed');

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="relative w-full max-w-xl rounded-xl border border-zinc-800 bg-zinc-900 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 text-zinc-100"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Modal Top Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4 bg-zinc-900/90">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700">
              <Ticket className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-bold text-zinc-100">{ticketId}</span>
                <button
                  onClick={handleCopyId}
                  title="Copy Ticket ID"
                  className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              </div>
              <span className="text-[11px] text-zinc-400">Support Ticket Record (MongoDB)</span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="max-h-[75vh] overflow-y-auto p-5 space-y-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 text-zinc-500 gap-2">
              <Loader2 className="h-6 w-6 animate-spin text-zinc-400" />
              <span className="text-xs">Fetching verified ticket from database...</span>
            </div>
          ) : error ? (
            <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-4 text-center text-xs text-red-300">
              <AlertCircle className="h-5 w-5 mx-auto mb-1 text-red-400" />
              <span>{error}</span>
            </div>
          ) : ticket ? (
            <>
              {/* Status & Subject */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-sm font-semibold text-zinc-100">{ticket.subject || ticket.description}</h3>
                <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium ${
                  isResponded 
                    ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60' 
                    : isClosed 
                    ? 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                    : 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                }`}>
                  {ticket.status || 'Pending Review'}
                </span>
              </div>

              {/* Key Details Grid */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-3.5 text-xs grid grid-cols-2 gap-3">
                <div>
                  <span className="text-zinc-500">Customer:</span>
                  <div className="font-medium text-zinc-200 mt-0.5">{ticket.customer_name || 'Customer'}</div>
                  <div className="text-[11px] text-zinc-400">{ticket.customer_email}</div>
                </div>

                <div>
                  <span className="text-zinc-500">Linked Order:</span>
                  <div className="font-mono font-medium text-zinc-200 mt-0.5">{ticket.order_id || 'N/A'}</div>
                  <div className="text-[11px] text-zinc-400">{ticket.product_name}</div>
                </div>

                <div>
                  <span className="text-zinc-500">Category:</span>
                  <div className="font-medium text-zinc-200 mt-0.5">{ticket.category || 'General Support'}</div>
                </div>

                <div>
                  <span className="text-zinc-500">Expected SLA:</span>
                  <div className="flex items-center gap-1 font-medium text-zinc-200 mt-0.5">
                    <Clock className="h-3 w-3 text-amber-400" />
                    {ticket.estimated_sla || '24-48 Business Hours'}
                  </div>
                </div>
              </div>

              {/* Customer Inquiry Details */}
              <div>
                <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Customer Inquiry</label>
                <div className="mt-1.5 rounded-lg border border-zinc-800 bg-zinc-950 p-3.5 text-xs text-zinc-200 leading-relaxed whitespace-pre-wrap">
                  {ticket.description}
                </div>
              </div>

              {/* Vendor Resolution (if available) */}
              {ticket.vendor_response ? (
                <div className="rounded-lg border border-emerald-800/40 bg-emerald-950/20 p-4 text-xs space-y-1.5">
                  <div className="font-semibold text-emerald-400 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      Official Vendor Technical Resolution
                    </span>
                    {ticket.vendor_responder_name && (
                      <span className="text-emerald-300/80 font-normal">by {ticket.vendor_responder_name}</span>
                    )}
                  </div>
                  <p className="mt-1.5 text-zinc-200 leading-relaxed whitespace-pre-wrap pt-1">
                    {ticket.vendor_response}
                  </p>
                  {ticket.vendor_responded_at && (
                    <div className="text-[10px] text-emerald-400/60 pt-1 text-right">
                      Responded on {ticket.vendor_responded_at}
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/40 p-3 text-xs text-zinc-400 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-amber-400 shrink-0" />
                  <span>This ticket is currently queued with the assigned vendor ({ticket.assigned_vendor || 'Technical Support'}).</span>
                </div>
              )}

              {/* Assigned Team */}
              <div className="flex items-center gap-2 text-[11px] text-zinc-500 border-t border-zinc-800/60 pt-3">
                <Building className="h-3.5 w-3.5 text-zinc-400" />
                <span>Assigned Vendor: <strong className="text-zinc-300 font-medium">{ticket.assigned_vendor || 'Authorized Support Team'}</strong></span>
              </div>
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end border-t border-zinc-800 bg-zinc-900/90 px-5 py-3">
          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-800 hover:bg-zinc-700 px-4 py-1.5 text-xs font-medium text-zinc-200 transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
