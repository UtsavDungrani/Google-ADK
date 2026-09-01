import React, { useState, useEffect } from 'react';
import { Search, BookOpen, PlusCircle, CheckCircle, Sparkles, Filter, X, FileText, Database } from 'lucide-react';
import { searchFaqApi, addFaqApi, fetchFaqCategoriesApi } from '../services/api';

const DEFAULT_CATEGORIES = ['All', 'Shipping', 'Returns', 'Warranty', 'Billing', 'Troubleshooting', 'Security'];

export default function FaqKnowledgeExplorer({ isOpen, onClose, onSelectQuestionToChat }) {
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  // Add FAQ Modal State
  const [showAddForm, setShowAddForm] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [newCategory, setNewCategory] = useState('Shipping');
  const [adding, setAdding] = useState(false);
  const [addSuccessMsg, setAddSuccessMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      handleSearch('shipping return warranty', 'All');
      loadStats();
    }
  }, [isOpen]);

  const loadStats = async () => {
    const data = await fetchFaqCategoriesApi();
    setStats(data);
  };

  const handleSearch = async (searchQuery = query, cat = selectedCategory) => {
    const searchTerm = searchQuery.trim() || 'policy delivery return warranty';
    setLoading(true);
    try {
      const data = await searchFaqApi(searchTerm, cat, 6);
      if (data && data.faq_results) {
        setResults(data.faq_results);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (cat) => {
    setSelectedCategory(cat);
    handleSearch(query, cat);
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!newQuestion.trim() || !newAnswer.trim()) return;
    setAdding(true);
    setAddSuccessMsg('');
    try {
      const res = await addFaqApi(newQuestion, newAnswer, newCategory);
      setAddSuccessMsg(res.message || 'Successfully indexed new FAQ into live RAG store!');
      setNewQuestion('');
      setNewAnswer('');
      setShowAddForm(false);
      await loadStats();
      handleSearch(newQuestion, 'All');
    } catch (err) {
      alert(err.message || 'Failed to add FAQ');
    } finally {
      setAdding(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                FAQ Knowledge Base Explorer
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium">
                  Hybrid RAG Vector Search
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                {stats ? `${stats.total_chunks} Knowledge Chunks indexed in Vector Store` : 'Loading RAG Vector Index...'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-600/20"
            >
              <PlusCircle className="w-4 h-4" />
              Add Dynamic FAQ
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Add FAQ Form Modal Drawer */}
        {showAddForm && (
          <div className="p-5 bg-slate-800/90 border-b border-slate-700 animate-slide-down">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-blue-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Dynamic FAQ Ingestion (Live Vector Re-Indexing)
              </h3>
              <button onClick={() => setShowAddForm(false)} className="text-xs text-slate-400 hover:text-slate-200">
                Cancel
              </button>
            </div>
            <form onSubmit={handleFormSubmit} className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">Question / Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Can I update my delivery address after placing an order?"
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    {DEFAULT_CATEGORIES.filter(c => c !== 'All').map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Detailed Policy Answer</label>
                <textarea
                  required
                  rows={3}
                  placeholder="e.g. Yes, delivery address changes are accepted within 2 hours of order placement..."
                  value={newAnswer}
                  onChange={(e) => setNewAnswer(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="submit"
                  disabled={adding}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
                >
                  {adding ? 'Indexing Vector Chunk...' : 'Index Into RAG Store'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Success Alert */}
        {addSuccessMsg && (
          <div className="px-6 py-2 bg-emerald-900/40 border-b border-emerald-700/50 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            {addSuccessMsg}
          </div>
        )}

        {/* Search Bar & Category Filters */}
        <div className="p-5 border-b border-slate-800 space-y-3 bg-slate-900/40">
          <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
              <input
                type="text"
                placeholder="Ask any policy, shipping, return, warranty, or device question..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs rounded-xl transition-all shadow-md shadow-blue-600/20"
            >
              {loading ? 'RAG Searching...' : 'Search Knowledge'}
            </button>
          </form>

          {/* Category Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            <span className="text-xs text-slate-400 flex items-center gap-1 shrink-0 font-medium">
              <Filter className="w-3.5 h-3.5" /> Topics:
            </span>
            {DEFAULT_CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategoryClick(cat)}
                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-slate-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* FAQ Results Grid */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 max-h-[55vh]">
          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs font-medium">Executing BM25 & TF-IDF Dense Cosine Retrieval...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="py-12 text-center text-slate-400">
              <FileText className="w-10 h-10 mx-auto text-slate-600 mb-2" />
              <p className="text-sm font-semibold text-slate-300">No FAQ entries matched query</p>
              <p className="text-xs text-slate-500">Try adjusting your search terms or select a different category filter.</p>
            </div>
          ) : (
            results.map((faq, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 hover:border-blue-500/50 transition-all space-y-2 group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="p-1 rounded bg-blue-500/20 text-blue-300 text-xs font-mono font-bold">
                      #{idx + 1}
                    </span>
                    <h3 className="text-sm font-bold text-slate-100 group-hover:text-blue-300 transition-colors">
                      {faq.topic}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-amber-300 border border-slate-700">
                      RRF Score: {faq.relevance_score || '0.032'}
                    </span>
                    {onSelectQuestionToChat && (
                      <button
                        onClick={() => {
                          onSelectQuestionToChat(faq.topic);
                          onClose();
                        }}
                        className="px-2.5 py-1 text-xs font-medium bg-blue-600/30 hover:bg-blue-600 text-blue-200 hover:text-white rounded-lg transition-colors flex items-center gap-1"
                      >
                        Ask Agent <Sparkles className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line border-l-2 border-slate-700 pl-3 py-1 bg-slate-900/40 rounded-r">
                  {faq.answer}
                </p>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <span className="flex items-center gap-1.5 font-medium text-slate-300 text-xs">
                    <Database className="w-3.5 h-3.5 text-blue-400" /> Category: {faq.source}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <span>Powered by Google ADK Hybrid RAG (Dense-Sparse RRF Fusion)</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
          >
            Close Explorer
          </button>
        </div>

      </div>
    </div>
  );
}
