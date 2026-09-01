import React from 'react';
import { 
  MessageSquare, 
  Package, 
  RotateCcw, 
  ShieldCheck, 
  Headphones, 
  ArrowRight, 
  Search, 
  Sparkles, 
  CheckCircle2, 
  Truck, 
  Ticket, 
  Clock, 
  LifeBuoy,
  ChevronRight,
  Shield,
  Bot
} from 'lucide-react';

export default function WebsiteHomepage({ onOpenChat, onSelectPrompt, onSwitchTab }) {
  const handleQuickAction = (promptText) => {
    onOpenChat();
    if (onSelectPrompt) {
      onSelectPrompt(promptText);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-blue-600 selection:text-white">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-zinc-800/80 bg-gradient-to-b from-zinc-900 via-zinc-950 to-zinc-950 pt-12 pb-16 md:pt-20 md:pb-24">
        
        {/* Ambient Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/15 blur-3xl rounded-full pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-indigo-600/10 blur-3xl rounded-full pointer-events-none" />

        <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
          <div className="flex flex-col items-center text-center max-w-3xl mx-auto">
            
            {/* Top Pill Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3.5 py-1 text-xs font-medium text-blue-400 mb-6 backdrop-blur-sm">
              <Sparkles className="h-3.5 w-3.5 animate-pulse text-blue-400" />
              <span>Next-Gen AI Customer Care Suite</span>
            </div>

            {/* Headline */}
            <h1 className="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
              Instant Support, Orders & Returns{' '}
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-sky-400 bg-clip-text text-transparent">
                Powered by AI
              </span>
            </h1>

            {/* Subtitle */}
            <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl leading-relaxed">
              Track shipments, request prepaid return labels, troubleshoot device errors, and inspect vendor tickets in real-time — 24/7 without waiting.
            </p>

            {/* CTA Buttons */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={() => onOpenChat()}
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 hover:bg-blue-500 active:scale-95 transition-all"
              >
                <MessageSquare className="h-4 w-4" />
                <span>Launch Support Chat</span>
                <ArrowRight className="h-4 w-4 opacity-70" />
              </button>

              <button
                onClick={() => handleQuickAction('Track order ORD-10021')}
                className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900/90 px-5 py-3 text-sm font-medium text-zinc-200 hover:bg-zinc-800 hover:text-white transition-all"
              >
                <Package className="h-4 w-4 text-zinc-400" />
                <span>Track Demo Order (ORD-10021)</span>
              </button>
            </div>

            {/* Micro Stats */}
            <div className="mt-12 grid grid-cols-3 gap-6 sm:gap-12 border-t border-zinc-800/80 pt-8 text-center max-w-xl w-full">
              <div>
                <p className="text-xl sm:text-2xl font-bold text-zinc-100">99.8%</p>
                <p className="text-xs text-zinc-500 mt-0.5">Instant Resolution</p>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-zinc-100">&lt; 2s</p>
                <p className="text-xs text-zinc-500 mt-0.5">Response Time</p>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-zinc-100">24 / 7</p>
                <p className="text-xs text-zinc-500 mt-0.5">Automated Support</p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Quick Services Grid */}
      <section className="py-14 bg-zinc-950 border-b border-zinc-800/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-xl mx-auto mb-10">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400">Self-Service Portal</h2>
            <p className="text-2xl font-bold text-zinc-100 mt-1">What can we help you with today?</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Card 1: Order Tracking */}
            <div 
              onClick={() => handleQuickAction('Where is my order ORD-10023?')}
              className="group relative cursor-pointer rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 hover:border-blue-500/50 hover:bg-zinc-900 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  <Truck className="h-5 w-5" />
                </div>
                <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 group-hover:text-blue-400 transition-colors">Order & Shipment Tracking</h3>
              <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                Check real-time shipping status, courier details, and estimated delivery dates for your purchases.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-[11px] font-medium text-blue-400">
                <span>Try ORD-10021 or ORD-10023</span>
              </div>
            </div>

            {/* Card 2: Easy Returns & RMA */}
            <div 
              onClick={() => handleQuickAction('I want to return item from ORD-10021')}
              className="group relative cursor-pointer rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 hover:border-emerald-500/50 hover:bg-zinc-900 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                  <RotateCcw className="h-5 w-5" />
                </div>
                <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 group-hover:text-emerald-400 transition-colors">Returns & RMA Labels</h3>
              <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                Instantly request returns, check return window eligibility, and download prepaid RMA shipping labels.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-[11px] font-medium text-emerald-400">
                <span>Instant RMA Label Generation</span>
              </div>
            </div>

            {/* Card 3: Troubleshooting */}
            <div 
              onClick={() => handleQuickAction('How do I fix error code E-404 on my smart hub?')}
              className="group relative cursor-pointer rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 hover:border-purple-500/50 hover:bg-zinc-900 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-purple-400 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 group-hover:text-purple-400 transition-colors">Device & Error Codes</h3>
              <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                Troubleshoot device setup, diagnostic error codes (e.g. E-404), firmware updates, and resetting devices.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-[11px] font-medium text-purple-400">
                <span>Knowledgebase RAG Search</span>
              </div>
            </div>

            {/* Card 4: Vendor Portal */}
            <div 
              onClick={() => onSwitchTab('vendor')}
              className="group relative cursor-pointer rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 hover:border-amber-500/50 hover:bg-zinc-900 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-400 group-hover:bg-amber-600 group-hover:text-white transition-colors">
                  <Ticket className="h-5 w-5" />
                </div>
                <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 group-hover:text-amber-400 transition-colors">Vendor Support Desk</h3>
              <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                Escalate complex technical queries directly to product vendors and track support tickets (`TCK-...`).
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-[11px] font-medium text-amber-400">
                <span>Open Vendor Portal</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Interactive Demo Showcase / How it Works */}
      <section className="py-16 bg-zinc-900/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">
                <Bot className="h-4 w-4" />
                <span>Smart Conversational AI</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-white leading-tight">
                Everything you need to manage your purchases in one floating widget.
              </h2>
              <p className="mt-4 text-sm text-zinc-400 leading-relaxed">
                Our customer care assistant directly integrates with MongoDB databases and vendor ticket management. Click the floating widget in the bottom right corner anytime to interact.
              </p>

              <div className="mt-6 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-zinc-200">Real-Time Database Queries</p>
                    <p className="text-xs text-zinc-500">Live order lookup for packages, courier tracking URLs, and return windows.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-blue-400 text-xs">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-zinc-200">RMA Prepaid Label Generator</p>
                    <p className="text-xs text-zinc-500">Automated approval and return shipping label creation for eligible orders.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-500/20 text-indigo-400 text-xs">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-zinc-200">Vendor Ticket Escalation</p>
                    <p className="text-xs text-zinc-500">Seamlessly logs structured tickets to vendor systems for complex hardware issues.</p>
                  </div>
                </div>
              </div>

              <div className="mt-8">
                <button
                  onClick={() => onOpenChat()}
                  className="inline-flex items-center gap-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 px-5 py-2.5 text-xs font-medium text-zinc-100 transition-colors"
                >
                  <MessageSquare className="h-4 w-4 text-blue-400" />
                  <span>Try Floating Chatbot Widget Now</span>
                </button>
              </div>
            </div>

            {/* Graphic / Preview Box */}
            <div className="relative rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 shadow-2xl overflow-hidden">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-4">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-red-500/80" />
                  <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                  <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                </div>
                <span className="text-xs font-mono text-zinc-500">Live Support Preview</span>
              </div>

              <div className="space-y-3 text-xs">
                {/* Mock user message */}
                <div className="flex justify-end">
                  <div className="rounded-xl bg-blue-600 px-3.5 py-2 text-white max-w-[80%] shadow">
                    Where is my package for order ORD-10021?
                  </div>
                </div>

                {/* Mock bot message */}
                <div className="flex justify-start">
                  <div className="rounded-xl bg-zinc-900 border border-zinc-800 px-3.5 py-2.5 text-zinc-200 max-w-[90%] space-y-2">
                    <p>📦 Order **ORD-10021** is currently **In Transit** via FedEx.</p>
                    <div className="rounded-lg bg-zinc-950 p-2 border border-zinc-800 text-[11px]">
                      <div className="flex justify-between text-zinc-400">
                        <span>Courier: FedEx Ground</span>
                        <span className="text-emerald-400">On Schedule</span>
                      </div>
                      <div className="font-mono text-zinc-300 mt-1">Tracking: FX-992104-US</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Floating Trigger Prompt */}
              <div className="mt-6 pt-4 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400">
                <span>Click the button in the bottom right corner to test live</span>
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800/80 bg-zinc-950 py-8 text-xs text-zinc-500">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-zinc-400 font-semibold">
            <Bot className="h-4 w-4 text-blue-500" />
            <span>Customer Care AI Portal</span>
          </div>
          <p>© 2026 Customer Care Support System. All rights reserved.</p>
          <div className="flex items-center gap-4 text-zinc-400">
            <button onClick={() => onSwitchTab('chat')} className="hover:text-white transition-colors">Full Workspace</button>
            <button onClick={() => onSwitchTab('vendor')} className="hover:text-white transition-colors">Vendor Desk</button>
          </div>
        </div>
      </footer>

    </div>
  );
}
