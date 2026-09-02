import React, { useState } from 'react';
import { 
  Search, 
  Package, 
  RotateCcw, 
  ShieldCheck, 
  Wrench, 
  Ticket, 
  BookOpen, 
  ArrowRight, 
  ExternalLink,
  HelpCircle,
  Clock,
  Shield,
  MessageSquare,
  FileText,
  ChevronRight
} from 'lucide-react';

export default function WebsiteHomepage({ 
  onOpenChat, 
  onSelectPrompt, 
  onSwitchTab, 
  onOpenFaqExplorer, 
  onOpenSystemStats 
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;
    if (onSelectPrompt) {
      onSelectPrompt(query);
    } else {
      onOpenChat();
    }
  };

  const handleQuickPrompt = (prompt) => {
    if (onSelectPrompt) {
      onSelectPrompt(prompt);
    } else {
      onOpenChat();
    }
  };

  const quickCategories = [
    {
      title: 'Order & Shipping Tracking',
      description: 'Check real-time package delivery status, courier details, and estimated delivery dates.',
      prompt: 'Where is my order ORD-10021?',
      sample: 'Try ORD-10021 or ORD-10023',
      icon: Package,
      actionText: 'Track an Order'
    },
    {
      title: 'Returns & RMA Labels',
      description: 'Submit return requests, check 30-day window eligibility, and generate prepaid return labels.',
      prompt: 'I want to return an item from ORD-10021',
      sample: 'Instant prepaid RMA labels',
      icon: RotateCcw,
      actionText: 'Start a Return'
    },
    {
      title: 'Device Troubleshooting',
      description: 'Find solutions for device error codes (e.g. E-404), setup instructions, and firmware resets.',
      prompt: 'How do I fix error code E-404 on my smart hub?',
      sample: 'Troubleshoot error codes',
      icon: Wrench,
      actionText: 'Troubleshoot Device'
    },
    {
      title: 'Warranty & Replacement',
      description: 'Review 1-year limited warranty coverage and submit replacement claims for defective hardware.',
      prompt: 'Is my device covered under warranty for replacement?',
      sample: '1-Year hardware coverage',
      icon: ShieldCheck,
      actionText: 'File Warranty Claim'
    },
    {
      title: 'Vendor Support Desk',
      description: 'Escalate complex hardware queries to manufacturer specialists and inspect support tickets.',
      customAction: () => onSwitchTab('vendor'),
      sample: 'Lookup TCK-10021-VND',
      icon: Ticket,
      actionText: 'Open Vendor Desk'
    },
    {
      title: 'Policy & FAQ Knowledge Base',
      description: 'Search official store policies including 30-day returns, international shipping, and payments.',
      customAction: () => onOpenFaqExplorer && onOpenFaqExplorer(),
      sample: 'Search full store policy',
      icon: BookOpen,
      actionText: 'Browse Knowledge Base'
    }
  ];

  const popularArticles = [
    {
      question: 'What is the standard 30-day return policy?',
      category: 'Returns',
      prompt: 'What is your 30-day return policy and requirements?'
    },
    {
      question: 'How do I resolve Error Code E-404 on Smart Hub?',
      category: 'Troubleshooting',
      prompt: 'How do I fix error code E-404 on my smart hub?'
    },
    {
      question: 'What is covered under the 1-Year Limited Warranty?',
      category: 'Warranty',
      prompt: 'What is covered under the 1-Year Limited Warranty?'
    },
    {
      question: 'Where do you ship and what are standard delivery times?',
      category: 'Shipping',
      prompt: 'What are the shipping destinations and delivery estimates?'
    }
  ];

  return (
    <div className="min-h-full bg-zinc-950 text-zinc-100 font-sans">
      
      {/* Top Support Search Hero */}
      <section className="border-b border-zinc-800 bg-zinc-900/40 px-4 py-12 sm:px-6 md:py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-semibold tracking-tight text-zinc-100">
            Customer Support & Help Center
          </h1>
          <p className="mt-3 text-sm sm:text-base text-zinc-400 max-w-xl mx-auto">
            Search policies, track shipments, generate return labels, or troubleshoot device issues.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="mt-7 max-w-2xl mx-auto">
            <div className="relative flex items-center shadow-sm">
              <Search className="absolute left-4 h-4 w-4 text-zinc-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by order ID (e.g. ORD-10021), ticket ID, or issue..."
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950 py-3.5 pl-11 pr-28 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-700 focus:outline-none focus:ring-1 focus:ring-zinc-700"
              />
              <button
                type="submit"
                className="absolute right-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 px-3.5 py-1.5 text-xs font-medium text-zinc-200 transition-colors"
              >
                Search
              </button>
            </div>
          </form>

          {/* Quick Filter / Topic Chips */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs">
            <span className="text-zinc-500">Suggested:</span>
            <button
              onClick={() => handleQuickPrompt('Where is my order ORD-10021?')}
              className="rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              Track ORD-10021
            </button>
            <button
              onClick={() => handleQuickPrompt('I want to return an item from ORD-10021')}
              className="rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              Return Item
            </button>
            <button
              onClick={() => handleQuickPrompt('How do I fix error code E-404 on my smart hub?')}
              className="rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              Error Code E-404
            </button>
            <button
              onClick={() => handleQuickPrompt('What is the 30-day return policy?')}
              className="rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              30-Day Return Policy
            </button>
          </div>
        </div>
      </section>

      {/* Main Support Grid */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-zinc-200">Support Categories</h2>
            <p className="text-xs text-zinc-500 mt-0.5">Select a topic to start self-service support or look up information.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickCategories.map((cat, idx) => {
            const Icon = cat.icon;
            return (
              <div
                key={idx}
                onClick={() => {
                  if (cat.customAction) {
                    cat.customAction();
                  } else if (cat.prompt) {
                    handleQuickPrompt(cat.prompt);
                  }
                }}
                className="group flex flex-col justify-between cursor-pointer rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 hover:bg-zinc-900 hover:border-zinc-700 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 group-hover:text-white group-hover:bg-zinc-700 transition-colors">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="text-[11px] font-mono text-zinc-500">{cat.sample}</span>
                  </div>

                  <h3 className="text-sm font-semibold text-zinc-200 group-hover:text-white transition-colors">
                    {cat.title}
                  </h3>
                  <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                    {cat.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-zinc-800/60 flex items-center justify-between text-xs font-medium text-zinc-300 group-hover:text-blue-400 transition-colors">
                  <span>{cat.actionText}</span>
                  <ChevronRight className="h-3.5 w-3.5 text-zinc-500 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Two-Column Section: Frequently Asked Questions & Direct Access */}
      <section className="border-t border-zinc-800 bg-zinc-900/20 py-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left 2 Cols: Popular Questions List */}
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-zinc-200">Frequently Asked Questions</h3>
                <p className="text-xs text-zinc-500 mt-0.5">Commonly referenced store policies and troubleshooting answers.</p>
              </div>

              <div className="space-y-2.5">
                {popularArticles.map((art, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleQuickPrompt(art.prompt)}
                    className="flex items-center justify-between cursor-pointer rounded-lg border border-zinc-800 bg-zinc-900/40 px-4 py-3 hover:bg-zinc-900 hover:border-zinc-700 transition-all text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-4 w-4 text-zinc-500 shrink-0" />
                      <span className="font-medium text-zinc-200 hover:text-white">{art.question}</span>
                    </div>
                    <span className="rounded bg-zinc-800 px-2 py-0.5 text-[11px] text-zinc-400 shrink-0 ml-2">
                      {art.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right 1 Col: Direct Support Options */}
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-zinc-200">Support Resources</h3>
                <p className="text-xs text-zinc-500 mt-0.5">Access direct tools and internal portals.</p>
              </div>

              <div className="space-y-3">
                
                {/* Card 1: Full Workspace */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-zinc-200">Support Chat Assistant</span>
                    <MessageSquare className="h-4 w-4 text-zinc-400" />
                  </div>
                  <p className="text-zinc-400 leading-relaxed text-[11px]">
                    Open the dedicated full-screen chat workspace to view conversation history.
                  </p>
                  <button
                    onClick={() => onSwitchTab('chat')}
                    className="mt-2 w-full rounded-md border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 py-1.5 text-xs font-medium text-zinc-200 transition-colors"
                  >
                    Open Full Workspace
                  </button>
                </div>

                {/* Card 2: Vendor Desk */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-zinc-200">Vendor Support Desk</span>
                    <Ticket className="h-4 w-4 text-zinc-400" />
                  </div>
                  <p className="text-zinc-400 leading-relaxed text-[11px]">
                    Internal dashboard for viewing, replying to, and resolving vendor escalated tickets.
                  </p>
                  <button
                    onClick={() => onSwitchTab('vendor')}
                    className="mt-2 w-full rounded-md border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 py-1.5 text-xs font-medium text-zinc-200 transition-colors"
                  >
                    Open Vendor Portal
                  </button>
                </div>

              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Clean, Simple Footer */}
      <footer className="border-t border-zinc-800 py-6 text-xs text-zinc-500">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Shield className="h-4 w-4 text-zinc-500" />
            <span className="font-medium text-zinc-300">Customer Support Portal</span>
          </div>
          <p className="text-[11px]">Support Center & Self-Service Portal</p>
          <div className="flex items-center gap-4 text-zinc-400 text-xs">
            <button onClick={() => onSwitchTab('chat')} className="hover:text-zinc-200 transition-colors">
              Chat Workspace
            </button>
            <button onClick={() => onSwitchTab('vendor')} className="hover:text-zinc-200 transition-colors">
              Vendor Desk
            </button>
            <button onClick={() => onOpenFaqExplorer && onOpenFaqExplorer()} className="hover:text-zinc-200 transition-colors">
              FAQ Database
            </button>
          </div>
        </div>
      </footer>

    </div>
  );
}
