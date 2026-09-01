import React from 'react';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  X, 
  Clock 
} from 'lucide-react';

export default function ChatHistorySidebar({ 
  isOpen, 
  onClose, 
  sessions, 
  currentSessionId, 
  onSelectSession, 
  onNewChat, 
  onDeleteSession 
}) {
  if (!isOpen) return null;

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-zinc-800 bg-zinc-900 shadow-xl md:static md:z-auto">
      
      {/* Top Header & New Chat */}
      <div className="border-b border-zinc-800 p-3 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Chat History
        </span>
        <button
          onClick={onClose}
          className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 md:hidden"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-2.5">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 p-2 text-xs font-medium text-zinc-200 border border-zinc-700 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>New Chat</span>
        </button>
      </div>

      {/* History Items Scrollable List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sessions.length === 0 ? (
          <div className="p-4 text-center text-xs text-zinc-500">
            No previous chat sessions yet.
          </div>
        ) : (
          sessions.map((s) => {
            const isSelected = s.session_id === currentSessionId;
            return (
              <div
                key={s.session_id}
                className={`group flex items-center justify-between rounded-lg px-2.5 py-2 text-xs cursor-pointer transition-colors ${
                  isSelected 
                    ? 'bg-zinc-800 text-zinc-100 font-medium' 
                    : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
                }`}
                onClick={() => onSelectSession(s.session_id)}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <MessageSquare className="h-3.5 w-3.5 shrink-0 text-zinc-500" />
                  <div className="truncate text-left">
                    <div className="truncate text-xs">{s.title || 'Support Conversation'}</div>
                    <div className="text-[10px] text-zinc-500 flex items-center gap-1 mt-0.5">
                      <Clock className="h-2.5 w-2.5" />
                      <span>{s.updated_at ? s.updated_at.split(' ')[0] : 'Recent'}</span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.session_id);
                  }}
                  className="opacity-0 group-hover:opacity-100 rounded p-1 text-zinc-500 hover:bg-zinc-700 hover:text-rose-400 transition-all"
                  title="Delete chat"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

    </aside>
  );
}
