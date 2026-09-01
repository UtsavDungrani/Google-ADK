import React from 'react';

const SUGGESTIONS = [
  { label: 'Track ORD-10023', prompt: 'Where is my order ORD-10023 and when will it arrive?' },
  { label: 'TV Wi-Fi Error TV-NET-502', prompt: 'My TV from order ORD-10021 shows error code TV-NET-502. How do I fix it?' },
  { label: 'Check Ticket TCK-10021-VND', prompt: 'What is the status of vendor ticket TCK-10021-VND?' },
  { label: 'Open Vendor Ticket', prompt: 'My BaristaPro espresso machine (order ORD-10023) is vibrating erratically. Can you open a vendor support ticket for me?' },
  { label: 'Return ORD-10022', prompt: 'I want to return order ORD-10022. Is it eligible and can you generate an RMA return label?' },
  { label: 'Warranty Claim', prompt: 'The screen on my TV (order ORD-10021) has black lines. Can I file a warranty replacement claim?' },
  { label: 'Delayed Delivery Voucher', prompt: 'My delivery was delayed by 4 days and I need compensation.' }
];

export default function QuickPrompts({ onSelectPrompt, disabled }) {
  return (
    <div className="border-t border-zinc-800 bg-zinc-900/60 p-2.5">
      <div className="flex gap-1.5 overflow-x-auto scrollbar-none pb-0.5">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            disabled={disabled}
            onClick={() => onSelectPrompt(item.prompt)}
            className="shrink-0 rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-300 hover:border-zinc-700 hover:bg-zinc-800 hover:text-zinc-100 transition-colors disabled:opacity-50"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
