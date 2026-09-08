import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  ShieldCheck, 
  Activity, 
  Database, 
  GitBranch, 
  Layers, 
  Check, 
  X,
  Sliders,
  Server
} from 'lucide-react';
import { fetchSystemStatsApi } from '../services/api';

export default function SystemArchitectureModal({ isOpen, onClose }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadStats();
    }
  }, [isOpen]);

  const loadStats = async () => {
    setLoading(true);
    const data = await fetchSystemStatsApi();
    setStats(data);
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-4xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden text-zinc-100 font-sans">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-zinc-800 flex items-center justify-between bg-zinc-950">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-zinc-100">
                System Architecture & Services
              </h2>
              <p className="text-xs text-zinc-400">
                Agent pipeline, data storage, security filters, and system metrics
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 max-h-[75vh]">
          {loading ? (
            <div className="py-12 text-center text-zinc-500 text-xs">
              Loading system metrics...
            </div>
          ) : (
            <>
              {/* Metric Overview Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
                  <div className="flex items-center justify-between text-xs text-zinc-400">
                    <span>Specialist Agents</span>
                    <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
                  </div>
                  <div className="text-xl font-bold text-zinc-100">
                    {stats?.sub_agents_count || 5}
                  </div>
                  <div className="text-[11px] text-zinc-500">
                    Active Agent Modules
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
                  <div className="flex items-center justify-between text-xs text-zinc-400">
                    <span>Tool Integrations</span>
                    <Layers className="w-3.5 h-3.5 text-zinc-400" />
                  </div>
                  <div className="text-xl font-bold text-zinc-100">
                    {stats?.registered_tools_count || 21}
                  </div>
                  <div className="text-[11px] text-zinc-500">
                    Backend Functions
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
                  <div className="flex items-center justify-between text-xs text-zinc-400">
                    <span>Knowledge Chunks</span>
                    <Database className="w-3.5 h-3.5 text-zinc-400" />
                  </div>
                  <div className="text-xl font-bold text-zinc-100">
                    {stats?.rag_vector_chunks || 31}
                  </div>
                  <div className="text-[11px] text-zinc-500">
                    Indexed Policies & FAQs
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
                  <div className="flex items-center justify-between text-xs text-zinc-400">
                    <span>Orders Dataset</span>
                    <Activity className="w-3.5 h-3.5 text-zinc-400" />
                  </div>
                  <div className="text-xl font-bold text-zinc-100">
                    99,441
                  </div>
                  <div className="text-[11px] text-zinc-500">
                    Historical Order Records
                  </div>
                </div>
              </div>

              {/* Section 1: Specialist Agents Hierarchy */}
              <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                    <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
                    Specialist Agent Hierarchy
                  </h3>
                  <span className="text-[11px] text-zinc-500 font-mono">ADK Multi-Agent Router</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">1. Order Logistics</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded">
                        4 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Handles shipment status lookup, courier tracking numbers, and delivery delay analysis.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">2. Product Support</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded">
                        7 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Executes knowledge base searches, FAQ lookups, error code resolution, and manual guides.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">3. Returns & Warranty</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded">
                        5 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Validates 30-day return eligibility, generates prepaid RMA shipping labels, and checks warranty.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">4. Escalation & Sentiment</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded">
                        4 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Monitors sentiment trajectory, provides courtesy credits, and handles priority escalation.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 space-y-1 md:col-span-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">5. Vendor Support & Ticketing</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded">
                        6 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Logs structured vendor tickets, tracks resolution statuses, and coordinates with manufacturer teams.
                    </p>
                  </div>
                </div>
              </div>

              {/* Section 2: Technical Specifications Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2.5">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                    <Database className="w-3.5 h-3.5 text-zinc-400" />
                    Knowledge Retrieval & Database
                  </h3>
                  <ul className="text-xs text-zinc-400 space-y-1.5 leading-relaxed">
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Dynamic Few-Shot RAG</strong>: Hybrid TF-IDF cosine similarity + BM25 overlap retrieves gold supervisor precedents for in-context prompt injection.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Sparse & Dense Retrieval</strong>: BM25 keyword matching combined with TF-IDF cosine similarity.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Ranking Fusion</strong>: Reciprocal Rank Fusion (RRF) for consistent search relevancy.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Database Storage</strong>: MongoDB collections for tickets, chat sessions, orders, customer profiles, episodes, and gold exemplars.</span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2.5">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-zinc-400" />
                    Security & Guardrails
                  </h3>
                  <ul className="text-xs text-zinc-400 space-y-1.5 leading-relaxed">
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Data Sanitization</strong>: Filters sensitive credit card and personal payment info.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Input Validation</strong>: Sanitizes inputs and protects system prompt boundaries.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-zinc-300 shrink-0 mt-0.5" />
                      <span><strong>Session State Management</strong>: Preserves order and ticket context across turns.</span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2.5 md:col-span-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                    <Sliders className="w-3.5 h-3.5 text-zinc-400" />
                    Context & Token Optimization
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 text-xs text-zinc-300">
                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80">
                      <span className="font-semibold text-zinc-200 block">Session Truncation</span>
                      <p className="text-[11px] text-zinc-500 mt-1">Sliding context window with historical conversation memory.</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80">
                      <span className="font-semibold text-zinc-200 block">Payload Pruning</span>
                      <p className="text-[11px] text-zinc-500 mt-1">Extracts only essential database fields to minimize payload overhead.</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80">
                      <span className="font-semibold text-zinc-200 block">Sentence Extraction</span>
                      <p className="text-[11px] text-zinc-500 mt-1">Filters out non-relevant documentation boilerplate before generation.</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80">
                      <span className="font-semibold text-zinc-200 block">Token Budgeting</span>
                      <p className="text-[11px] text-zinc-500 mt-1">Enforces per-turn token limits for fast response latency.</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-950 flex items-center justify-between text-xs text-zinc-500">
          <span>Customer Support Architecture Overview</span>
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs font-medium transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
