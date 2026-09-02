import React, { useState, useEffect } from 'react';
import { Search, BookOpen, Plus, Check, Filter, X, FileText, Database, ArrowRight } from 'lucide-react';
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
      const data = await searchFaqApi(searchTerm, cat, 8);
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
      setAddSuccessMsg(res.message || 'New FAQ article saved successfully.');
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-4xl max-h-[88vh] shadow-2xl flex flex-col overflow-hidden text-zinc-100 font-sans">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-zinc-800 flex items-center justify-between bg-zinc-950">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-zinc-100">
                FAQ Knowledge Base
              </h2>
              <p className="text-xs text-zinc-400">
                {stats ? `${stats.total_chunks} support articles indexed in database` : 'Knowledge base search'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add FAQ Article</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Add FAQ Form Drawer */}
        {showAddForm && (
          <div className="p-4 bg-zinc-950/90 border-b border-zinc-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold text-zinc-200">
                Create New FAQ Article
              </h3>
              <button onClick={() => setShowAddForm(false)} className="text-xs text-zinc-500 hover:text-zinc-300">
                Cancel
              </button>
            </div>
            <form onSubmit={handleFormSubmit} className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="md:col-span-2">
                  <label className="block text-[11px] font-medium text-zinc-400 mb-1">Question / Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Can I update my delivery address after placing an order?"
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    className="w-full px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-zinc-400 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-zinc-700"
                  >
                    {DEFAULT_CATEGORIES.filter(c => c !== 'All').map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-medium text-zinc-400 mb-1">Policy / Troubleshooting Answer</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Provide official policy details or step-by-step resolution..."
                  value={newAnswer}
                  onChange={(e) => setNewAnswer(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="submit"
                  disabled={adding}
                  className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition-colors"
                >
                  {adding ? 'Saving...' : 'Save Article'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Success Alert */}
        {addSuccessMsg && (
          <div className="px-5 py-2 bg-emerald-950/40 border-b border-emerald-800/50 text-emerald-300 text-xs flex items-center gap-2">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            {addSuccessMsg}
          </div>
        )}

        {/* Search Bar & Category Filters */}
        <div className="p-4 border-b border-zinc-800 space-y-3 bg-zinc-900/40">
          <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-zinc-400" />
              <input
                type="text"
                placeholder="Search policies, shipping, returns, warranty, or device error codes..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs font-medium rounded-lg transition-colors"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>

          {/* Category Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            <span className="text-xs text-zinc-500 flex items-center gap-1 shrink-0 font-medium mr-1">
              <Filter className="w-3 h-3" /> Category:
            </span>
            {DEFAULT_CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategoryClick(cat)}
                className={`px-2.5 py-1 rounded-md text-xs transition-colors ${
                  selectedCategory === cat
                    ? 'bg-zinc-800 text-zinc-100 font-medium border border-zinc-700'
                    : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* FAQ Results Grid */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[50vh]">
          {loading ? (
            <div className="py-10 text-center text-zinc-500 text-xs">
              Searching knowledge base articles...
            </div>
          ) : results.length === 0 ? (
            <div className="py-10 text-center text-zinc-500">
              <FileText className="w-8 h-8 mx-auto text-zinc-600 mb-2" />
              <p className="text-xs font-medium text-zinc-300">No articles matched your search</p>
              <p className="text-[11px] text-zinc-500 mt-0.5">Try adjusting keywords or selecting another category.</p>
            </div>
          ) : (
            results.map((faq, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800/80 hover:border-zinc-700 transition-all space-y-2"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-zinc-500">
                      #{idx + 1}
                    </span>
                    <h3 className="text-xs font-semibold text-zinc-200">
                      {faq.topic}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                      {faq.source || 'General'}
                    </span>
                    {onSelectQuestionToChat && (
                      <button
                        onClick={() => {
                          onSelectQuestionToChat(faq.topic);
                          onClose();
                        }}
                        className="px-2.5 py-1 text-[11px] font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded border border-zinc-700 transition-colors flex items-center gap-1"
                      >
                        <span>Ask Support</span>
                        <ArrowRight className="w-3 h-3 text-zinc-400" />
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-xs text-zinc-300 leading-relaxed whitespace-pre-line pl-2.5 border-l-2 border-zinc-800 py-0.5">
                  {faq.answer}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-950 flex items-center justify-between text-xs text-zinc-500">
          <span>Customer Support Knowledge Base</span>
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
