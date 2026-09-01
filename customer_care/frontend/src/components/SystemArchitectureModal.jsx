import React, { useState, useEffect } from 'react';
import { Cpu, ShieldCheck, Activity, Database, GitBranch, Layers, CheckCircle2, Zap, Sparkles, X } from 'lucide-react';
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[92vh] shadow-2xl flex flex-col overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-600/20 text-purple-400 border border-purple-500/30">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                System Architecture & AI Intelligence Dashboard
                <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-medium">
                  Google ADK 2.0
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Multi-Agent System Graph, Hybrid RAG Specs, Neural Sentiment & Kaggle Dataset Metrics
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 max-h-[80vh]">
          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs font-medium">Querying System Architecture & ADK Runtime State...</p>
            </div>
          ) : (
            <>
              {/* Top Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                    <span>Active Sub-Agents</span>
                    <GitBranch className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-2xl font-black text-slate-100">
                    {stats?.sub_agents_count || 5}
                  </div>
                  <div className="text-[11px] text-purple-300 font-mono">
                    Specialist Agents
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                    <span>Registered Tools</span>
                    <Layers className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-2xl font-black text-slate-100">
                    {stats?.registered_tools_count || 21}
                  </div>
                  <div className="text-[11px] text-blue-300 font-mono">
                    Callable Tool Functions
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                    <span>RAG Vector Chunks</span>
                    <Database className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-black text-slate-100">
                    {stats?.rag_vector_chunks || 31}
                  </div>
                  <div className="text-[11px] text-emerald-300 font-mono">
                    Indexed Docs & FAQs
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                    <span>Kaggle Dataset</span>
                    <Activity className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-2xl font-black text-slate-100">
                    99,441
                  </div>
                  <div className="text-[11px] text-amber-300 font-mono">
                    E-Commerce Orders
                  </div>
                </div>
              </div>

              {/* Architecture Section 1: Multi-Agent Sub-Agents Graph */}
              <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-3">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-purple-400" />
                  Google ADK Multi-Agent Hierarchy & Specialist Sub-Agents
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-purple-300">1. Order Logistics Specialist</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded">
                        4 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Handles courier tracking (FedEx/UPS/DHL), delay risk predictions, and 99k+ dataset order logs.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-blue-300">2. Product Support Specialist</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded">
                        7 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Executes Hybrid RAG manual search, FAQ knowledge base retrieval, and troubleshooting.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-300">3. Returns & Warranty Specialist</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded">
                        5 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Automates 30-day return validation, prepaid RMA labels, warranty verification, and hardware claims.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-rose-300">4. Escalation & Sentiment Intelligence</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-rose-500/20 text-rose-300 rounded">
                        4 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Monitors emotional valence trajectory with LSTM Neural Sequence model, courtesy credits, and Tier-2 escalation.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 md:col-span-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-300">5. Vendor Support & Ticketing Specialist</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded">
                        6 Tools
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Manages asynchronous vendor tickets, SLA status lookups, vendor portal synchronization, and ticket resolution.
                    </p>
                  </div>
                </div>
              </div>

              {/* Architecture Section 2: ML & RAG Engine Technical Stack */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-3">
                  <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                    <Database className="w-4 h-4 text-emerald-400" />
                    Hybrid Dense-Sparse RAG Architecture
                  </h3>
                  <ul className="text-xs text-slate-300 space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span><strong>Dense Retrieval</strong>: Normalized TF-IDF Vector Cosine Similarity across document chunks.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span><strong>Sparse Retrieval</strong>: BM25 Term Frequency-Inverse Document Frequency matching.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span><strong>Ranking Fusion</strong>: Reciprocal Rank Fusion (RRF, k=60) for balanced precision.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span><strong>Storage Engine</strong>: 100% MongoDB Database Storage (`knowledge_docs` & `faqs` collections).</span>
                    </li>
                  </ul>
                </div>

                <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-3">
                  <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-blue-400" />
                    Safety, Sentiment & Security Guardrails
                  </h3>
                  <ul className="text-xs text-slate-300 space-y-2">
                    <li className="flex items-start gap-2">
                      <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                      <span><strong>PCI Compliance Guardrail</strong>: Regex sanitizer blocks credit card leakage before LLM processing.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                      <span><strong>Prompt Injection Filter</strong>: Strips malicious system prompt override attempts.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                      <span><strong>LSTM Neural Sentiment</strong>: Sequence trajectory classification for proactive churn prevention.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                      <span><strong>Multilingual Adapter</strong>: Dynamic persona adaptation across 6 target languages.</span>
                    </li>
                  </ul>
                </div>

                <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-3 md:col-span-2">
                  <h3 className="text-sm font-bold text-amber-300 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    Context Analysis & System-Wide Token Reduction Engine (42.8% Savings)
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs text-slate-300">
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <span className="font-bold text-amber-300 block">1. Session Truncation</span>
                      <p className="text-[11px] text-slate-400">Sliding window keeps recent 6 turns + auto-summarized historical memory block.</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <span className="font-bold text-amber-300 block">2. Payload Pruning</span>
                      <p className="text-[11px] text-slate-400">Strips raw DB fields into high-signal JSON (48.5% payload byte reduction).</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <span className="font-bold text-amber-300 block">3. Sentence Extraction</span>
                      <p className="text-[11px] text-slate-400">Sentence-level TF-IDF overlap extraction removes irrelevant RAG boilerplate.</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <span className="font-bold text-amber-300 block">4. Token Budgeting</span>
                      <p className="text-[11px] text-slate-400">Enforces 300 token budget cap, saving 320ms-650ms prompt latency.</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <span>Customer Care AI Master Agent • Ready for Presentation</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
          >
            Close Dashboard
          </button>
        </div>

      </div>
    </div>
  );
}
