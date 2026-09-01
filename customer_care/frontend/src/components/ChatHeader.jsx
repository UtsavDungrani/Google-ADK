import React from 'react';
import { 
  RotateCcw, 
  MessageSquare, 
  Ticket, 
  Home,
  PanelLeftClose,
  PanelLeft
} from 'lucide-react';

export default function ChatHeader({ 
  activeTab, 
  setActiveTab, 
  onResetChat, 
  sessionState, 
  isMongoOnline,
  messageCount,
  sidebarOpen,
  onToggleSidebar
}) {
  const activeOrder = sessionState?.current_order_id;
  const activeTicket = sessionState?.active_ticket_id;

  return (
    <header className="border-b border-zinc-800 bg-zinc-900 px-4 py-3 text-zinc-100">
      <div className="flex items-center justify-between">
        
        {/* Left: History toggle & Title */}
        <div className="flex items-center gap-3">
          {activeTab === 'chat' && (
            <button
              onClick={onToggleSidebar}
              className={`rounded-lg p-1.5 transition-colors border ${
                sidebarOpen 
                  ? 'bg-zinc-800 text-zinc-100 border-zinc-700' 
                  : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:bg-zinc-800 hover:text-zinc-200'
              }`}
              title={sidebarOpen ? "Hide chat history" : "Show chat history"}
            >
              {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeft className="h-4 w-4" />}
            </button>
          )}

          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold text-zinc-100">Customer Care</h1>
            <span className="flex items-center gap-1 text-[11px] text-zinc-400">
              <span className={`h-1.5 w-1.5 rounded-full ${isMongoOnline ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              {isMongoOnline ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Center: View Switcher */}
        <div className="flex rounded-lg bg-zinc-950 p-0.5 border border-zinc-800 text-xs">
          <button
            onClick={() => setActiveTab('website')}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 font-medium transition-colors ${
              activeTab === 'website'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Home className="h-3.5 w-3.5" />
            <span>Website Home</span>
          </button>

          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 font-medium transition-colors ${
              activeTab === 'chat'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <MessageSquare className="h-3.5 w-3.5" />
            <span>Full Workspace</span>
          </button>
          
          <button
            onClick={() => setActiveTab('vendor')}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 font-medium transition-colors ${
              activeTab === 'vendor'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Ticket className="h-3.5 w-3.5" />
            <span>Vendor Desk</span>
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {activeTab === 'chat' && (
            <button
              onClick={onResetChat}
              className="flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-800/80 px-2.5 py-1 text-xs text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors"
            >
              <RotateCcw className="h-3 w-3" />
              <span>New Chat</span>
            </button>
          )}
        </div>
      </div>

      {/* Active Session Context (Order / Ticket) */}
      {activeTab === 'chat' && (activeOrder || activeTicket) && (
        <div className="mt-2.5 flex items-center gap-2 border-t border-zinc-800/60 pt-2 text-[11px] text-zinc-400">
          <span>Active Context:</span>
          {activeOrder && (
            <span className="font-mono text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded border border-zinc-700">
              {activeOrder}
            </span>
          )}
          {activeTicket && (
            <span className="font-mono text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded border border-zinc-700">
              {activeTicket}
            </span>
          )}
        </div>
      )}
    </header>
  );
}
