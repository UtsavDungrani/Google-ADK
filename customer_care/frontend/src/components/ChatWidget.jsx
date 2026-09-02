import React, { useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  X, 
  Send, 
  Loader2, 
  RotateCcw, 
  Maximize2, 
  HelpCircle
} from 'lucide-react';
import MessageBubble from './MessageBubble';
import QuickPrompts from './QuickPrompts';

export default function ChatWidget({
  isOpen,
  onToggleOpen,
  messages,
  input,
  setInput,
  loading,
  handleSendMessage,
  handleResetChat,
  onOpenTicket,
  onExpandToFullScreen,
  isMongoOnline
}) {
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, loading]);

  const onFormSubmit = (e) => {
    e.preventDefault();
    handleSendMessage();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Floating Trigger Button (Bottom Right) */}
      <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5">
        
        {/* Helper Pill when widget is closed */}
        {!isOpen && (
          <div 
            onClick={onToggleOpen}
            className="hidden sm:flex items-center gap-1.5 cursor-pointer rounded-full border border-zinc-800 bg-zinc-900/95 px-3.5 py-1.5 text-xs text-zinc-300 shadow-lg backdrop-blur hover:bg-zinc-800 hover:text-white transition-all"
          >
            <HelpCircle className="h-3.5 w-3.5 text-zinc-400" />
            <span>Need Help?</span>
          </div>
        )}

        {/* Main Floating Circle Button */}
        <button
          onClick={onToggleOpen}
          aria-label="Toggle customer support chat"
          className={`relative flex h-13 w-13 items-center justify-center rounded-full shadow-lg transition-all duration-200 transform active:scale-95 ${
            isOpen 
              ? 'bg-zinc-800 text-zinc-100 hover:bg-zinc-700 border border-zinc-700' 
              : 'bg-blue-600 text-white hover:bg-blue-500'
          }`}
        >
          {isOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <>
              <MessageSquare className="h-5 w-5" />
              {/* Connected Indicator Dot */}
              <span className={`absolute top-1 right-1 h-2.5 w-2.5 rounded-full border-2 border-zinc-900 ${
                isMongoOnline ? 'bg-emerald-500' : 'bg-amber-500'
              }`} />
            </>
          )}
        </button>
      </div>

      {/* Floating Popup Box Container */}
      {isOpen && (
        <div className="fixed bottom-22 right-4 sm:right-6 z-50 flex flex-col w-[92vw] sm:w-[400px] h-[560px] max-h-[80vh] rounded-xl border border-zinc-800 bg-zinc-950 shadow-2xl overflow-hidden font-sans">
          
          {/* Header */}
          <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900 px-4 py-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700">
                <MessageSquare className="h-3.5 w-3.5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="text-xs font-semibold text-zinc-100">Customer Support</h3>
                  <span className={`h-1.5 w-1.5 rounded-full ${isMongoOnline ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                </div>
                <p className="text-[10px] text-zinc-400">Orders, Returns, Warranty & Tech Desk</p>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-1">
              <button
                onClick={handleResetChat}
                title="New Chat"
                className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </button>

              <button
                onClick={onExpandToFullScreen}
                title="Expand to Workspace"
                className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
              >
                <Maximize2 className="h-3.5 w-3.5" />
              </button>

              <button
                onClick={onToggleOpen}
                title="Close widget"
                className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-zinc-950">
            {messages.map((msg) => (
              <MessageBubble 
                key={msg.id} 
                message={msg} 
                onOpenTicket={onOpenTicket}
              />
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-xs text-zinc-500 py-1 px-2">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-zinc-400" />
                <span>Searching assistance...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Suggestions */}
          <div className="px-3 py-1 bg-zinc-950 border-t border-zinc-900">
            <QuickPrompts 
              onSelectPrompt={(prompt) => handleSendMessage(prompt)} 
              disabled={loading} 
            />
          </div>

          {/* Input Bar */}
          <div className="border-t border-zinc-800 bg-zinc-900/90 p-2.5">
            <form onSubmit={onFormSubmit} className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about orders, returns, errors..."
                disabled={loading}
                className="flex-1 rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:border-zinc-700 focus:outline-none"
              />

              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-40"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          </div>

        </div>
      )}
    </>
  );
}
