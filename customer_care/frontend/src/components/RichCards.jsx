import React, { useState } from 'react';
import { 
  Package, 
  Truck, 
  Ticket, 
  Clock, 
  ShieldCheck, 
  RotateCcw, 
  Tag, 
  Copy, 
  Check, 
  ExternalLink 
} from 'lucide-react';

/**
 * Clean Support Ticket Card
 */
export function TicketCard({ ticketId, status, responder, response, sla, orderId, onOpenTicket }) {
  const isResponded = status?.toLowerCase().includes('responded');
  const isClosed = status?.toLowerCase().includes('closed');

  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3.5 text-xs text-zinc-300 transition-all hover:border-zinc-700">
      <div className="flex items-center justify-between gap-2 border-b border-zinc-800 pb-2.5">
        <div 
          onClick={() => onOpenTicket && onOpenTicket(ticketId)}
          className="flex items-center gap-2 cursor-pointer hover:text-white transition-colors group"
        >
          <Ticket className="h-4 w-4 text-zinc-400 group-hover:text-blue-400 transition-colors" />
          <span className="font-mono font-medium text-zinc-100 underline decoration-zinc-700 underline-offset-2 group-hover:decoration-blue-400">
            {ticketId}
          </span>
          <ExternalLink className="h-3 w-3 text-zinc-500 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        
        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium ${
          isResponded 
            ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-800/50' 
            : isClosed 
            ? 'bg-zinc-800 text-zinc-400 border border-zinc-700'
            : 'bg-amber-950/70 text-amber-300 border border-amber-800/50'
        }`}>
          {status || 'Pending Review'}
        </span>
      </div>

      <div className="mt-2.5 flex items-center justify-between text-zinc-400">
        {orderId && <span>Order: <span className="font-mono text-zinc-200">{orderId}</span></span>}
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" /> SLA: {sla || '24-48 Hours'}
        </span>
      </div>

      {response && (
        <div className="mt-2.5 rounded-md border border-zinc-800 bg-zinc-950/80 p-2.5 text-zinc-200">
          <div className="font-medium text-emerald-400 text-[11px] mb-1">
            Resolution {responder ? `by ${responder}` : ''}
          </div>
          <p className="leading-relaxed text-zinc-300 whitespace-pre-wrap">{response}</p>
        </div>
      )}

      {onOpenTicket && (
        <div className="mt-3 pt-2.5 border-t border-zinc-800/60 flex justify-end">
          <button
            type="button"
            onClick={() => onOpenTicket(ticketId)}
            className="flex items-center gap-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 text-[11px] font-medium text-zinc-200 transition-colors border border-zinc-700 cursor-pointer"
          >
            <span>View Full Ticket Details</span>
            <ExternalLink className="h-3 w-3 text-zinc-400" />
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * Clean Order Tracking Card
 */
export function OrderTrackingCard({ orderId, status, carrier, trackingNumber, eta }) {
  const isDelivered = status?.toLowerCase().includes('delivered');

  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3.5 text-xs text-zinc-300">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <Truck className="h-4 w-4 text-zinc-400" />
          <span className="font-mono font-medium text-zinc-100">{orderId}</span>
        </div>
        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium ${
          isDelivered 
            ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-800/50' 
            : 'bg-blue-950/70 text-blue-300 border border-blue-800/50'
        }`}>
          {status || 'In Transit'}
        </span>
      </div>

      <div className="mt-2.5 grid grid-cols-2 gap-2 text-zinc-400">
        <div>Carrier: <span className="text-zinc-200">{carrier || 'Standard'}</span></div>
        <div>ETA: <span className="text-zinc-200">{eta || 'On Schedule'}</span></div>
      </div>

      {trackingNumber && (
        <div className="mt-2 flex items-center justify-between border-t border-zinc-800/60 pt-2 text-[11px] text-zinc-400">
          <span className="font-mono">Tracking: {trackingNumber}</span>
        </div>
      )}
    </div>
  );
}

/**
 * Clean RMA Return Card
 */
export function RmaCard({ rmaCode, refundAmount, labelUrl }) {
  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3.5 text-xs text-zinc-300">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <RotateCcw className="h-4 w-4 text-zinc-400" />
          <span className="font-mono font-medium text-zinc-100">{rmaCode}</span>
        </div>
        <span className="rounded-md bg-emerald-950/70 text-emerald-300 border border-emerald-800/50 px-2 py-0.5 text-[11px]">
          Authorized Return
        </span>
      </div>

      <div className="mt-2.5 flex items-center justify-between">
        <span className="text-zinc-400">Refund: <strong className="text-zinc-200">{refundAmount || '100%'}</strong></span>
        {labelUrl && (
          <a
            href={labelUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 text-xs text-zinc-200 transition-colors border border-zinc-700"
          >
            Download Label <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </div>
  );
}

/**
 * Clean Warranty Claim Card
 */
export function WarrantyClaimCard({ claimId }) {
  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3.5 text-xs text-zinc-300">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-zinc-400" />
          <span className="font-mono font-medium text-zinc-100">{claimId}</span>
        </div>
        <span className="rounded-md bg-emerald-950/70 text-emerald-300 border border-emerald-800/50 px-2 py-0.5 text-[11px]">
          Replacement Approved
        </span>
      </div>
      <div className="mt-2 text-zinc-400">
        Dispatched via 2-Day Air Express. Prepaid return box included.
      </div>
    </div>
  );
}

/**
 * Clean Courtesy Credit Card
 */
export function CreditVoucherCard({ voucherCode, amount }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(voucherCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3 text-xs text-zinc-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-zinc-400" />
          <span className="font-medium text-zinc-200">Courtesy Credit ({amount || '$25.00'})</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-2 py-1 text-[11px] text-zinc-200 border border-zinc-700 transition-colors"
        >
          {copied ? <><Check className="h-3 w-3 text-emerald-400" /> Copied</> : <><Copy className="h-3 w-3" /> {voucherCode}</>}
        </button>
      </div>
    </div>
  );
}
