import React from 'react';
import { 
  TicketCard, 
  OrderTrackingCard, 
  RmaCard, 
  WarrantyClaimCard, 
  CreditVoucherCard 
} from './RichCards';
import { Ticket } from 'lucide-react';

export default function MessageBubble({ message, onOpenTicket }) {
  const isUser = message.role === 'user';
  const text = message.text || '';

  // Extract entities from message text
  const ticketMatch = text.match(/\b(TCK-[A-Za-z0-9]+-[A-Za-z0-9]+)\b/);
  const orderMatch = text.match(/\b(ORD-\d{5}|[a-f0-9]{32})\b/);
  const rmaMatch = text.match(/\b(RMA-\d+-[A-Za-z0-9-]+)\b/);
  const claimMatch = text.match(/\b(CLM-\d+-[A-Za-z0-9-]+)\b/);
  const creditMatch = text.match(/\b(CARE-CREDIT-\d+)\b/);

  const isPendingTicket = text.toLowerCase().includes('pending vendor response') || text.toLowerCase().includes('opened a vendor support ticket');
  const isVendorResponded = text.toLowerCase().includes('vendor resolution') || text.toLowerCase().includes('vendor responded');
  const isDelivered = text.toLowerCase().includes('delivered');
  const isOutForDelivery = text.toLowerCase().includes('out for delivery');

  // Format simple markdown into clean HTML
  const formatMarkdown = (content) => {
    const lines = content.split('\n');
    const formatted = [];

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      if (trimmed.startsWith('*Source:') || trimmed.startsWith('Source:')) {
        formatted.push(
          <div key={idx} className="mt-2 text-[11px] text-zinc-500 font-mono">
            {trimmed.replace(/^\*+|\*+$/g, '')}
          </div>
        );
        return;
      }

      if (trimmed.startsWith('### ') || trimmed.startsWith('## ')) {
        const title = trimmed.replace(/^###?\s+/, '');
        formatted.push(
          <h4 key={idx} className="mt-2.5 mb-1 font-semibold text-zinc-100">
            {parseInlineStyles(title)}
          </h4>
        );
        return;
      }

      if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        const itemText = trimmed.replace(/^[\*\-]\s+/, '');
        formatted.push(
          <li key={idx} className="ml-4 list-disc text-zinc-300 my-0.5 leading-relaxed">
            {parseInlineStyles(itemText)}
          </li>
        );
        return;
      }

      if (/^\d+\.\s/.test(trimmed)) {
        const itemText = trimmed.replace(/^\d+\.\s+/, '');
        const num = trimmed.match(/^\d+/)[0];
        formatted.push(
          <div key={idx} className="my-1 flex items-start gap-2 text-zinc-300 leading-relaxed">
            <span className="font-mono text-zinc-500 text-xs">{num}.</span>
            <span className="flex-1">{parseInlineStyles(itemText)}</span>
          </div>
        );
        return;
      }

      if (!trimmed) {
        formatted.push(<div key={idx} className="h-1.5" />);
        return;
      }

      formatted.push(
        <p key={idx} className="my-0.5 leading-relaxed text-zinc-200">
          {parseInlineStyles(line)}
        </p>
      );
    });

    return formatted;
  };

  const parseInlineStyles = (str) => {
    const parts = [];
    const regex = /(\*\*[^*]+\*\*|`[^`]+`|\bTCK-[A-Za-z0-9]+-[A-Za-z0-9]+\b)/g;
    let lastIdx = 0;
    let match;

    while ((match = regex.exec(str)) !== null) {
      if (match.index > lastIdx) {
        parts.push(str.substring(lastIdx, match.index));
      }
      const token = match[0];

      // Clickable Ticket Code
      if (/^TCK-[A-Za-z0-9]+-[A-Za-z0-9]+$/.test(token)) {
        parts.push(
          <button
            key={match.index}
            type="button"
            onClick={() => onOpenTicket && onOpenTicket(token)}
            className="inline-flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-1.5 py-0.5 font-mono text-[11px] font-medium text-blue-300 border border-zinc-700 cursor-pointer transition-colors"
          >
            <Ticket className="h-2.5 w-2.5 text-blue-400" />
            <span>{token}</span>
          </button>
        );
      } else if (token.startsWith('**') && token.endsWith('**')) {
        const inner = token.slice(2, -2);
        // Check if bold text is a ticket
        if (/^TCK-[A-Za-z0-9]+-[A-Za-z0-9]+$/.test(inner)) {
          parts.push(
            <button
              key={match.index}
              type="button"
              onClick={() => onOpenTicket && onOpenTicket(inner)}
              className="inline-flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-1.5 py-0.5 font-mono text-[11px] font-medium text-blue-300 border border-zinc-700 cursor-pointer transition-colors"
            >
              <Ticket className="h-2.5 w-2.5 text-blue-400" />
              <span>{inner}</span>
            </button>
          );
        } else {
          parts.push(<strong key={match.index} className="font-semibold text-zinc-100">{inner}</strong>);
        }
      } else if (token.startsWith('`') && token.endsWith('`')) {
        const inner = token.slice(1, -1);
        if (/^TCK-[A-Za-z0-9]+-[A-Za-z0-9]+$/.test(inner)) {
          parts.push(
            <button
              key={match.index}
              type="button"
              onClick={() => onOpenTicket && onOpenTicket(inner)}
              className="inline-flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-1.5 py-0.5 font-mono text-[11px] font-medium text-blue-300 border border-zinc-700 cursor-pointer transition-colors"
            >
              <Ticket className="h-2.5 w-2.5 text-blue-400" />
              <span>{inner}</span>
            </button>
          );
        } else {
          parts.push(
            <code key={match.index} className="rounded bg-zinc-800 px-1 py-0.5 font-mono text-[11px] text-zinc-200">
              {inner}
            </code>
          );
        }
      }
      lastIdx = regex.lastIndex;
    }
    if (lastIdx < str.length) {
      parts.push(str.substring(lastIdx));
    }
    return parts.length > 0 ? parts : str;
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
        isUser 
          ? 'bg-blue-600 text-white rounded-br-xs' 
          : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-bl-xs'
      }`}>
        <div className="space-y-0.5">
          {formatMarkdown(text)}
        </div>

        {/* Dynamic Rich Cards */}
        {!isUser && (
          <div className="mt-2 space-y-2">
            {ticketMatch && (
              <TicketCard 
                ticketId={ticketMatch[1]}
                status={isVendorResponded ? 'Vendor Responded' : isPendingTicket ? 'Pending Vendor Response' : 'Active Ticket'}
                orderId={orderMatch ? orderMatch[1] : null}
                onOpenTicket={onOpenTicket}
              />
            )}

            {orderMatch && !ticketMatch && (text.toLowerCase().includes('tracking') || text.toLowerCase().includes('shipment') || text.toLowerCase().includes('delivery')) && (
              <OrderTrackingCard 
                orderId={orderMatch[1]}
                status={isDelivered ? 'Delivered' : isOutForDelivery ? 'Out for Delivery' : 'In Transit'}
                carrier={text.includes('FedEx') ? 'FedEx Freight' : text.includes('UPS') ? 'UPS Express' : text.includes('DHL') ? 'DHL Express' : 'Standard Express'}
              />
            )}

            {rmaMatch && (
              <RmaCard 
                rmaCode={rmaMatch[1]}
                labelUrl={`https://returns.store.com/labels/${rmaMatch[1]}.pdf`}
              />
            )}

            {claimMatch && (
              <WarrantyClaimCard 
                claimId={claimMatch[1]}
              />
            )}

            {creditMatch && (
              <CreditVoucherCard 
                voucherCode={creditMatch[1]}
                amount={text.includes('$50') ? '$50.00' : '$25.00'}
              />
            )}
          </div>
        )}

        <div className={`mt-2 text-[10px] flex items-center justify-between gap-2 border-t border-zinc-800/80 pt-1.5 ${isUser ? 'text-blue-200' : 'text-zinc-400'}`}>
          {message.token_metrics ? (
            <span className={`font-mono text-[10px] flex items-center gap-1.5 px-2 py-0.5 rounded border ${
              isUser 
                ? 'bg-blue-700/50 border-blue-500/40 text-blue-100' 
                : 'bg-zinc-950/80 border-zinc-800 text-amber-300'
            }`}>
              <span>⚡ {message.token_metrics.total_tokens} tokens</span>
              {message.token_metrics.completion_tokens && (
                <span className="text-zinc-400 font-normal hidden sm:inline">
                  (Prompt: {message.token_metrics.prompt_tokens} | Res: {message.token_metrics.completion_tokens} | Saved: {message.token_metrics.tokens_saved})
                </span>
              )}
            </span>
          ) : (
            <span />
          )}
          <span className="font-mono text-[10px] text-zinc-500">{message.timestamp}</span>
        </div>
      </div>
    </div>
  );
}
