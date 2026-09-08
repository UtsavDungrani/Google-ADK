import React, { useState, useEffect } from 'react';
import {
  X,
  Sparkles,
  Search,
  BookOpen,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ChevronRight,
  ChevronDown,
  Tag,
  ShieldCheck,
  Zap,
  RefreshCw,
  FileText,
  Copy,
  ExternalLink
} from 'lucide-react';
import {
  fetchFewShotExemplarsApi,
  searchFewShotExemplarsApi,
  addFewShotExemplarApi,
  deleteFewShotExemplarApi
} from '../services/api';

const SAMPLE_QUERIES = [
  { label: 'Hospital Return Exception', query: 'I missed the 30 day return cutoff because I was in hospital for surgery' },
  { label: 'Error TV-NET-502 Diagnostics', query: 'My TV keeps disconnecting from Eero Wi-Fi mesh showing TV-NET-502' },
  { label: 'Headphones Multipoint Setup', query: 'How to pair ProSound headphones to both iPhone and MacBook at same time?' },
  { label: 'Espresso Descaling & Low Pressure', query: 'BaristaPro orange blinking light is on and extraction pressure dropped below 5 bars' },
  { label: 'Delayed Shipping De-escalation', query: 'ORD-10023 is 4 days late and nobody updated me, I need this immediately!' },
  { label: 'Screen Lines Warranty Replacement', query: 'Black horizontal lines appeared across the lower screen of my Smart TV' }
];

const CATEGORIES = [
  'All',
  'Returns & Warranty',
  'Product Diagnostics',
  'Escalations & Courtesy Credits'
];

export default function FewShotExemplarExplorer({ isOpen, onClose }) {
  const [exemplars, setExemplars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [promptPreview, setPromptPreview] = useState(null);
  const [showPromptModal, setShowPromptModal] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  // Add form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Returns & Warranty');
  const [newSituation, setNewSituation] = useState('');
  const [newInquiry, setNewInquiry] = useState('');
  const [newThought, setNewThought] = useState('');
  const [newResponse, setNewResponse] = useState('');
  const [newCitation, setNewCitation] = useState('');
  const [newTags, setNewTags] = useState('');
  const [savingExemplar, setSavingExemplar] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    loadExemplars();
  }, [isOpen, selectedCategory]);

  async function loadExemplars() {
    setLoading(true);
    try {
      const data = await fetchFewShotExemplarsApi(selectedCategory);
      if (data && data.exemplars) {
        setExemplars(data.exemplars);
        if (data.exemplars.length > 0 && !expandedId) {
          setExpandedId(data.exemplars[0].exemplar_id);
        }
      }
    } catch (err) {
      console.error('Failed to fetch exemplars:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(queryText = searchQuery) {
    if (!queryText || !queryText.trim()) {
      setSearchResults(null);
      setPromptPreview(null);
      return;
    }
    setIsSearching(true);
    try {
      const data = await searchFewShotExemplarsApi(queryText, selectedCategory, 3);
      if (data && data.matches) {
        setSearchResults(data.matches);
        setPromptPreview(data.prompt_preview);
      }
    } catch (err) {
      console.error('Failed to search exemplars:', err);
    } finally {
      setIsSearching(false);
    }
  }

  function handleClearSearch() {
    setSearchQuery('');
    setSearchResults(null);
    setPromptPreview(null);
  }

  async function handleAddExemplar(e) {
    e.preventDefault();
    if (!newTitle.trim() || !newInquiry.trim() || !newResponse.trim()) return;

    setSavingExemplar(true);
    try {
      const tagsArray = newTags.split(',').map(t => t.trim().toLowerCase()).filter(Boolean);
      await addFewShotExemplarApi({
        title: newTitle.trim(),
        category: newCategory,
        situation: newSituation.trim() || 'General Customer Care Scenario',
        customer_inquiry: newInquiry.trim(),
        expert_thought: newThought.trim() || 'Provide structured resolution following customer care standards.',
        expert_response: newResponse.trim(),
        policy_citation: newCitation.trim() || '*Source: Official Customer Care Manual*',
        tags: tagsArray
      });

      // Reset form
      setNewTitle('');
      setNewSituation('');
      setNewInquiry('');
      setNewThought('');
      setNewResponse('');
      setNewCitation('');
      setNewTags('');
      setShowAddForm(false);
      await loadExemplars();
    } catch (err) {
      console.error('Failed to add exemplar:', err);
      alert('Error saving exemplar. Please check backend connection.');
    } finally {
      setSavingExemplar(false);
    }
  }

  async function handleDeleteExemplar(exemplarId) {
    if (!window.confirm(`Delete precedent ${exemplarId}?`)) return;
    try {
      await deleteFewShotExemplarApi(exemplarId);
      await loadExemplars();
      if (searchResults) {
        setSearchResults(prev => prev ? prev.filter(ex => ex.exemplar_id !== exemplarId) : null);
      }
    } catch (err) {
      console.error('Failed to delete exemplar:', err);
      alert('Could not delete exemplar.');
    }
  }

  function copyPromptToClipboard() {
    if (!promptPreview) return;
    navigator.clipboard.writeText(promptPreview);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  }

  if (!isOpen) return null;

  const displayList = searchResults || exemplars;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto p-2 sm:p-4 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl h-[92vh] max-h-[92vh] flex flex-col overflow-hidden text-slate-800 my-auto">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-violet-600 via-indigo-600 to-indigo-700 text-white flex items-center justify-between shadow-md shrink-0">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 shrink-0">
              <Sparkles className="w-6 h-6 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold tracking-tight">Dynamic Few-Shot RAG Precedents</h2>
                <span className="text-xs bg-amber-400 text-slate-900 font-semibold px-2 py-0.5 rounded-full shadow-sm">
                  In-Context Learning
                </span>
              </div>
              <p className="text-xs text-indigo-100 mt-0.5">
                Semantic retrieval of gold-standard human supervisor resolutions dynamically injected into Gemini agent context.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/80 hover:text-white shrink-0"
            title="Close Explorer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Dynamic Semantic Tester Banner (Hidden when curation form is open) */}
        {!showAddForm && (
          <div className="bg-slate-50 border-b border-slate-200 p-3 sm:p-4 shrink-0 animate-fadeIn">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="w-4 h-4 text-indigo-600 shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Interactive Hybrid Semantic Search & Relevance Tester
              </span>
              {searchResults && (
                <span className="text-xs bg-indigo-100 text-indigo-800 font-medium px-2 py-0.5 rounded-full">
                  {searchResults.length} {searchResults.length === 1 ? 'Match' : 'Matches'} Found
                </span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter customer message or symptom (e.g., 'Hospitalization missed 30 day return', 'error TV-NET-502')..."
                  className="w-full pl-9 pr-8 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
                />
                {searchQuery && (
                  <button
                    onClick={handleClearSearch}
                    className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              <button
                onClick={() => handleSearch()}
                disabled={isSearching || !searchQuery.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-all shadow-sm flex items-center space-x-1.5 shrink-0"
              >
                {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                <span>Test Match</span>
              </button>
              {promptPreview && (
                <button
                  onClick={() => setShowPromptModal(true)}
                  className="px-3.5 py-2 bg-violet-100 hover:bg-violet-200 text-violet-800 rounded-lg text-sm font-medium transition-all flex items-center space-x-1.5 shrink-0"
                  title="View Prompt Injected into Gemini"
                >
                  <FileText className="w-4 h-4 text-violet-600" />
                  <span>Gemini Prompt</span>
                </button>
              )}
            </div>

            {/* Quick Query Sample Chips */}
            <div className="flex flex-wrap items-center gap-1.5 mt-2">
              <span className="text-xs text-slate-500 font-medium">Quick Test:</span>
              {SAMPLE_QUERIES.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSearchQuery(sq.query);
                    handleSearch(sq.query);
                  }}
                  className="text-xs bg-white hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-full transition-colors shadow-2xs font-normal"
                >
                  {sq.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Category Filter Tabs & Actions Bar */}
        <div className="px-6 py-2.5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2 bg-white shrink-0">
          {!showAddForm ? (
            <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => {
                    setSelectedCategory(cat);
                    setSearchResults(null);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-900">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Curation Mode: Add New Gold-Standard Precedent</span>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg flex items-center space-x-1 shadow-sm transition-all ${
                showAddForm
                  ? 'bg-slate-700 hover:bg-slate-800 text-white'
                  : 'bg-emerald-600 hover:bg-emerald-700 text-white'
              }`}
            >
              {showAddForm ? (
                <>
                  <X className="w-3.5 h-3.5" />
                  <span>Back to Records</span>
                </>
              ) : (
                <>
                  <Plus className="w-3.5 h-3.5" />
                  <span>Curate Precedent</span>
                </>
              )}
            </button>
            {!showAddForm && (
              <button
                onClick={loadExemplars}
                className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                title="Refresh Store"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            )}
          </div>
        </div>

        {/* Main Scrollable Content Area */}
        <div className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 space-y-4">
          {showAddForm ? (
            /* Precedent Curation Studio (Exclusively focused: other records hidden) */
            <form onSubmit={handleAddExemplar} className="bg-emerald-50/80 border-2 border-emerald-300 rounded-xl p-5 sm:p-6 shadow-md animate-fadeIn space-y-4 max-w-4xl mx-auto">
              <div className="flex items-center justify-between pb-3 border-b border-emerald-200">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 bg-emerald-600 text-white rounded-lg shadow-xs">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-emerald-950 uppercase tracking-wider">
                      Curate New Gold-Standard Exemplar
                    </h4>
                    <p className="text-xs text-emerald-700 mt-0.5">
                      Enter human expert demonstration. Synchronously saved to MongoDB and local JSON fallback store.
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="text-xs text-slate-500 hover:text-slate-800 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-2xs transition-colors flex items-center space-x-1"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Cancel & View Records</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Precedent Title *</label>
                  <input
                    type="text"
                    required
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Smart Watch Bluetooth Heart-Rate Re-sync"
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category *</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  >
                    <option value="Returns & Warranty">Returns & Warranty</option>
                    <option value="Product Diagnostics">Product Diagnostics</option>
                    <option value="Escalations & Courtesy Credits">Escalations & Courtesy Credits</option>
                    <option value="Shipping & Courier Logistics">Shipping & Courier Logistics</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Customer Inquiry (User Query) *</label>
                  <textarea
                    required
                    rows={3}
                    value={newInquiry}
                    onChange={(e) => setNewInquiry(e.target.value)}
                    placeholder="Customer's verbatim inquiry, symptom, or complaint..."
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Situation Context</label>
                  <textarea
                    rows={3}
                    value={newSituation}
                    onChange={(e) => setNewSituation(e.target.value)}
                    placeholder="Operational background context, constraints, customer history..."
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Expert Thought Process (Chain-of-Thought)</label>
                  <textarea
                    rows={4}
                    value={newThought}
                    onChange={(e) => setNewThought(e.target.value)}
                    placeholder="Supervisor reasoning: policy rules, empathy anchors, diagnosis rationale..."
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Gold-Standard Agent Response *</label>
                  <textarea
                    required
                    rows={4}
                    value={newResponse}
                    onChange={(e) => setNewResponse(e.target.value)}
                    placeholder="The ideal, empathetic, structured response to guide Gemini..."
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Policy Citation</label>
                  <input
                    type="text"
                    value={newCitation}
                    onChange={(e) => setNewCitation(e.target.value)}
                    placeholder="e.g. *Source: Official Store Policy - Section 4.2*"
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Tags (comma-separated for BM25/TF-IDF)</label>
                  <input
                    type="text"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                    placeholder="e.g. return, exception, medical, grace, refund"
                    className="w-full text-xs p-2.5 bg-white border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 text-slate-800 shadow-2xs"
                  />
                </div>
              </div>

              <div className="flex justify-end items-center space-x-2 pt-3 border-t border-emerald-200">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-md text-xs font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingExemplar}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-md text-xs font-medium flex items-center space-x-1.5 shadow-sm transition-all"
                >
                  {savingExemplar ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                  <span>Save to Knowledge Base</span>
                </button>
              </div>
            </form>
          ) : loading ? (
            <div className="py-16 text-center text-slate-400">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-indigo-500" />
              <p className="text-sm">Loading gold-standard exemplars from MongoDB...</p>
            </div>
          ) : displayList.length === 0 ? (
            <div className="py-16 text-center text-slate-400">
              <BookOpen className="w-10 h-10 mx-auto mb-2 text-slate-300" />
              <p className="text-sm font-medium text-slate-600">No matching exemplars found</p>
              <p className="text-xs text-slate-400 mt-1">Try another search query or clear the filter.</p>
            </div>
          ) : (
            displayList.map((ex) => {
              const isExpanded = expandedId === ex.exemplar_id;
              const hasScore = typeof ex.relevance_score === 'number';
              const relPercent = hasScore ? Math.round(ex.relevance_score * 100) : null;

              return (
                <div
                  key={ex.exemplar_id}
                  className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                    hasScore
                      ? 'border-indigo-300 bg-indigo-50/20 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300 shadow-2xs'
                  }`}
                >
                  {/* Card Title Row */}
                  <div
                    onClick={() => setExpandedId(isExpanded ? null : ex.exemplar_id)}
                    className="p-4 cursor-pointer flex items-center justify-between bg-white hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`p-2 rounded-lg ${
                          ex.category?.includes('Warranty') || ex.category?.includes('Returns')
                            ? 'bg-amber-100 text-amber-700'
                            : ex.category?.includes('Escalation')
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-indigo-100 text-indigo-700'
                        }`}
                      >
                        <BookOpen className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono font-bold text-slate-500">{ex.exemplar_id}</span>
                          <span className="text-xs bg-slate-100 text-slate-600 font-medium px-2 py-0.5 rounded">
                            {ex.category}
                          </span>
                          {hasScore && (
                            <span
                              className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                                relPercent >= 70
                                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                                  : relPercent >= 40
                                  ? 'bg-indigo-100 text-indigo-800 border border-indigo-300'
                                  : 'bg-amber-100 text-amber-800 border border-amber-300'
                              }`}
                            >
                              {relPercent}% Semantic Match
                            </span>
                          )}
                        </div>
                        <h3 className="text-sm font-semibold text-slate-900 mt-0.5 break-words">{ex.title}</h3>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0 ml-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteExemplar(ex.exemplar_id);
                        }}
                        className="p-1.5 text-slate-300 hover:text-rose-600 rounded-md transition-colors"
                        title="Delete Precedent"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Precedent Details */}
                  {isExpanded && (
                    <div className="p-4 border-t border-slate-100 space-y-3 bg-slate-50/50">
                      {/* Customer Inquiry */}
                      <div className="bg-white p-3 rounded-lg border border-slate-200">
                        <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center space-x-1.5">
                          <HelpCircle className="w-3.5 h-3.5 text-blue-500" />
                          <span>Customer Inquiry</span>
                        </div>
                        <p className="text-xs text-slate-800 italic">"{ex.customer_inquiry}"</p>
                      </div>

                      {/* Situation Context */}
                      {ex.situation && (
                        <div className="bg-white p-3 rounded-lg border border-slate-200">
                          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                            Operational Context
                          </div>
                          <p className="text-xs text-slate-700">{ex.situation}</p>
                        </div>
                      )}

                      {/* Expert Thought Process */}
                      <div className="bg-amber-50/70 p-3 rounded-lg border border-amber-200">
                        <div className="text-xs font-bold uppercase tracking-wider text-amber-800 mb-1 flex items-center space-x-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                          <span>Expert Supervisor Thought Process</span>
                        </div>
                        <p className="text-xs text-amber-900 leading-relaxed">{ex.expert_thought}</p>
                      </div>

                      {/* Gold-Standard Response */}
                      <div className="bg-emerald-50/70 p-3 rounded-lg border border-emerald-200">
                        <div className="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-1 flex items-center space-x-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Gold-Standard Resolution Response</span>
                        </div>
                        <div className="text-xs text-emerald-950 font-normal whitespace-pre-line leading-relaxed break-words">
                          {ex.expert_response}
                        </div>
                        {ex.policy_citation && (
                          <p className="text-[11px] font-semibold text-emerald-700 mt-2">
                            {ex.policy_citation}
                          </p>
                        )}
                      </div>

                      {/* Tags */}
                      {ex.tags && ex.tags.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1 pt-1">
                          <Tag className="w-3 h-3 text-slate-400 mr-1" />
                          {ex.tags.map((t, tidx) => (
                            <span
                              key={tidx}
                              className="text-[11px] bg-slate-200/80 text-slate-700 px-2 py-0.5 rounded-full font-mono"
                            >
                              #{t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-100 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <div className="flex items-center space-x-2">
            <span className={`inline-block w-2 h-2 rounded-full ${showAddForm ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
            {showAddForm ? (
              <span className="text-slate-600 font-medium">Curation Studio • Fields with * are required for in-context prompt injection</span>
            ) : (
              <>
                <span className="hidden sm:inline">Dynamic Few-Shot RAG: Sublinear TF-IDF Cosine + BM25 Lexical Overlap</span>
                <span className="sm:hidden font-medium">Few-Shot In-Context RAG</span>
              </>
            )}
          </div>
          <button
            onClick={() => {
              if (showAddForm) {
                setShowAddForm(false);
              } else {
                onClose();
              }
            }}
            className="px-5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-medium transition-colors shadow-xs"
          >
            {showAddForm ? 'Back to Records' : 'Done'}
          </button>
        </div>
      </div>

      {/* Gemini In-Context Prompt Modal */}
      {showPromptModal && promptPreview && (
        <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-md animate-fadeIn">
          <div className="bg-slate-900 text-slate-100 rounded-xl border border-slate-700 w-full max-w-3xl h-[80vh] max-h-[80vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="px-5 py-3 bg-slate-800 border-b border-slate-700 flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-violet-400" />
                <h4 className="text-sm font-semibold">Gemini In-Context Few-Shot Injection Preview</h4>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={copyPromptToClipboard}
                  className="text-xs bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded flex items-center space-x-1"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{copiedPrompt ? 'Copied!' : 'Copy'}</span>
                </button>
                <button
                  onClick={() => setShowPromptModal(false)}
                  className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed bg-slate-950 flex-1 min-h-0">
              {promptPreview}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
