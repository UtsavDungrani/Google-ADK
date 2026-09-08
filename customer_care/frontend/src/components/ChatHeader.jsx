import React from 'react';
import { 
  RotateCcw, 
  MessageSquare, 
  Ticket, 
  Home, 
  PanelLeftClose, 
  PanelLeft, 
  BookOpen, 
  Server,
  Brain,
  Sparkles,
  Globe
} from 'lucide-react';

export default function ChatHeader({ 
  activeTab, 
  setActiveTab, 
  onResetChat, 
  sessionState, 
  isMongoOnline, 
  messageCount, 
  sidebarOpen, 
  onToggleSidebar, 
  onOpenFaqExplorer, 
  onOpenSystemStats,
  onOpenMemoryModal,
  onOpenFewShotExplorer,
  onOpenMultilingualExplorer,
  detectedLanguage = 'en',
  languageName,
  activeCustomerName,
  activeUserId
}) {
  const activeOrder = sessionState?.current_order_id;
  const activeTicket = sessionState?.active_ticket_id;
  const activeCustomer = sessionState?.customer_name || activeCustomerName;

  return (
    <header className="border-b border-zinc-800 bg-zinc-900 px-4 py-2.5 text-zinc-100">
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
            <h1 className="text-sm font-semibold text-zinc-100">Customer Support</h1>
            <span className="flex items-center gap-1 text-[11px] text-zinc-400">
              <span className={`h-1.5 w-1.5 rounded-full ${isMongoOnline ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              {isMongoOnline ? 'Connected' : 'Offline'}
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
            <span>Home</span>
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
            <span>Chat Workspace</span>
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
          <button
            onClick={onOpenMemoryModal}
            className="flex items-center gap-1.5 rounded-md border border-purple-500/40 bg-purple-500/10 px-2.5 py-1 text-xs text-purple-300 hover:bg-purple-500/20 hover:text-white transition-colors shadow-sm"
            title="Cross-Session Long-Term Memory & Persona Switcher"
          >
            <Brain className="h-3.5 w-3.5 text-purple-400" />
            <span className="hidden sm:inline font-medium">{activeCustomer ? activeCustomer.split(' ')[0] : 'Memory'}</span>
          </button>

          <button
            onClick={onOpenFewShotExplorer}
            className="flex items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-xs text-amber-300 hover:bg-amber-500/20 hover:text-white transition-colors shadow-sm"
            title="Dynamic Few-Shot RAG Precedents & In-Context Exemplars"
          >
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span className="hidden sm:inline font-medium">Few-Shot RAG</span>
          </button>

          <button
            onClick={onOpenMultilingualExplorer}
            className="flex items-center gap-1.5 rounded-md border border-teal-500/40 bg-teal-500/10 px-2.5 py-1 text-xs text-teal-300 hover:bg-teal-500/20 hover:text-white transition-colors shadow-sm"
            title="Multilingual NLP, Sub-ms LID & Cross-Lingual RAG Bridge"
          >
            <Globe className="h-3.5 w-3.5 text-teal-400" />
            <span className="hidden sm:inline font-medium">
              {detectedLanguage && detectedLanguage !== 'en' ? `${detectedLanguage.toUpperCase()} NLP` : 'Multilingual'}
            </span>
          </button>

          <button
            onClick={onOpenFaqExplorer}
            className="flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-800/80 px-2.5 py-1 text-xs text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors"
            title="Search Knowledge Base & Policies"
          >
            <BookOpen className="h-3.5 w-3.5 text-zinc-400" />
            <span className="hidden sm:inline font-medium">Knowledge Base</span>
          </button>

          <button
            onClick={onOpenSystemStats}
            className="flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-800/80 px-2.5 py-1 text-xs text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors"
            title="View System Architecture & Services"
          >
            <Server className="h-3.5 w-3.5 text-zinc-400" />
            <span className="hidden sm:inline font-medium">Architecture</span>
          </button>

          {activeTab === 'chat' && (
            <button
              onClick={onResetChat}
              className="flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-800/80 px-2.5 py-1 text-xs text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors"
            >
              <RotateCcw className="h-3 w-3 text-zinc-400" />
              <span>New Chat</span>
            </button>
          )}
        </div>
      </div>

      {/* Active Session Context (Customer / Order / Ticket) */}
      {activeTab === 'chat' && (activeCustomer || activeOrder || activeTicket) && (
        <div className="mt-2 flex items-center gap-2 border-t border-zinc-800/60 pt-2 text-[11px] text-zinc-400">
          <span>Active Context:</span>
          {activeCustomer && (
            <span 
              onClick={onOpenMemoryModal}
              className="cursor-pointer flex items-center gap-1 font-mono text-purple-300 bg-purple-950/40 hover:bg-purple-900/40 px-1.5 py-0.5 rounded border border-purple-800/60 transition-colors"
              title="View Customer Long-Term Memory"
            >
              <Brain className="w-3 h-3 text-purple-400" /> {activeCustomer}
            </span>
          )}
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
