import React, { useState, useEffect } from 'react';
import {
  X,
  Globe,
  Languages,
  ShieldCheck,
  Search,
  Sparkles,
  Zap,
  CheckCircle2,
  Tag,
  ArrowRight,
  BookOpen,
  RefreshCw,
  Cpu,
  MessageSquare
} from 'lucide-react';
import {
  detectLanguageApi,
  crossLingualSearchApi,
  fetchSupportedLanguagesApi
} from '../services/api';

const SAMPLE_MULTILINGUAL_QUERIES = [
  {
    flag: '🇪🇸',
    lang: 'Spanish',
    label: 'Spanish Return Exception',
    text: '¿Cómo puedo devolver mi televisor si estuve en el hospital 7 días?'
  },
  {
    flag: '🇮🇳',
    lang: 'Hindi',
    label: 'Hindi TV Wi-Fi Error',
    text: 'मेरे 65 इंच टीवी पर एरर कोड TV-NET-502 आ रहा है और वाईफाई डिस्कनेक्ट हो रहा है'
  },
  {
    flag: '🇮🇳',
    lang: 'Hinglish',
    label: 'Hinglish Delay De-escalation',
    text: 'Mera order ORD-10023 4 days se delay hai, delivery status track kardo please'
  },
  {
    flag: '🇩🇪',
    lang: 'German',
    label: 'German Screen Defect',
    text: 'Mein Fernseher hat schwarze horizontale Linien auf dem Bildschirm'
  },
  {
    flag: '🇫🇷',
    lang: 'French',
    label: 'French Shipping Refund',
    text: 'Bonjour, mon colis a du retard et je voudrais un remboursement pour la commande ORD-10021'
  },
  {
    flag: '🇯🇵',
    lang: 'Japanese',
    label: 'Japanese Headphones Multipoint',
    text: 'ヘッドホンをMacBookとiPhoneに同時に接続する方法を教えてください'
  }
];

export default function MultilingualExplorerModal({ isOpen, onClose }) {
  const [inputText, setInputText] = useState(SAMPLE_MULTILINGUAL_QUERIES[0].text);
  const [analysis, setAnalysis] = useState(null);
  const [clirResults, setClirResults] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('tester'); // 'tester' | 'languages'

  useEffect(() => {
    if (!isOpen) return;
    loadLanguages();
    analyzeInput(inputText);
  }, [isOpen]);

  async function loadLanguages() {
    try {
      const data = await fetchSupportedLanguagesApi();
      if (data && data.languages) {
        setSupportedLanguages(data.languages);
      }
    } catch (err) {
      console.error('Failed to load supported languages:', err);
    }
  }

  async function analyzeInput(textToAnalyze) {
    if (!textToAnalyze || !textToAnalyze.trim()) {
      setAnalysis(null);
      setClirResults(null);
      return;
    }
    setLoading(true);
    try {
      // 1. Detect Language & Pragmatic Politeness
      const lidData = await detectLanguageApi(textToAnalyze);
      if (lidData && lidData.analysis) {
        setAnalysis(lidData);
      }

      // 2. Perform Cross-Lingual Search Alignment
      const searchData = await crossLingualSearchApi(textToAnalyze);
      if (searchData) {
        setClirResults(searchData);
      }
    } catch (err) {
      console.error('Failed to analyze multilingual text:', err);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto p-2 sm:p-4 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl h-[92vh] max-h-[92vh] flex flex-col overflow-hidden text-slate-800 my-auto">
        
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-teal-600 via-emerald-600 to-indigo-700 text-white flex items-center justify-between shadow-md shrink-0">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 shrink-0">
              <Globe className="w-6 h-6 text-teal-200" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold tracking-tight">Multilingual NLP & Cross-Lingual RAG</h2>
                <span className="text-xs bg-amber-400 text-slate-900 font-semibold px-2 py-0.5 rounded-full shadow-sm">
                  Global Pipeline
                </span>
              </div>
              <p className="text-xs text-teal-100 mt-0.5">
                Sub-millisecond LID, Devanagari & Kanji script detection, Hinglish code-mixing, and Cross-Lingual Information Retrieval (CLIR).
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

        {/* View Mode Navigation Tabs */}
        <div className="px-6 py-2.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('tester')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
                activeTab === 'tester'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Interactive NLP Sandbox</span>
            </button>
            <button
              onClick={() => setActiveTab('languages')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
                activeTab === 'languages'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
              }`}
            >
              <Languages className="w-3.5 h-3.5 text-emerald-500" />
              <span>Supported Language Matrix</span>
            </button>
          </div>

          <span className="text-xs text-slate-500 font-mono hidden sm:inline">
            Sub-millisecond LID & CLIR Engine
          </span>
        </div>

        {/* Content Body */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6 space-y-5">
          {activeTab === 'tester' ? (
            <>
              {/* Input Box & Quick Samples */}
              <div className="space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                  Enter Multilingual Inquiry (Spanish, Hindi, Hinglish, German, French, Japanese)
                </label>
                <div className="flex items-start space-x-2">
                  <div className="relative flex-1">
                    <textarea
                      rows={2}
                      value={inputText}
                      onChange={(e) => {
                        setInputText(e.target.value);
                        analyzeInput(e.target.value);
                      }}
                      placeholder="Type a customer inquiry in any language..."
                      className="w-full text-xs p-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:outline-none shadow-xs text-slate-800"
                    />
                  </div>
                  <button
                    onClick={() => analyzeInput(inputText)}
                    disabled={loading || !inputText.trim()}
                    className="px-4 py-3 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-xs font-medium rounded-xl flex items-center space-x-1.5 shadow-sm transition-all"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                    <span>Analyze NLP</span>
                  </button>
                </div>

                {/* Quick Test Samples */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-xs text-slate-500 font-medium">Try Preset:</span>
                  {SAMPLE_MULTILINGUAL_QUERIES.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputText(item.text);
                        analyzeInput(item.text);
                      }}
                      className="text-xs bg-slate-100 hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-full transition-colors flex items-center space-x-1"
                    >
                      <span>{item.flag}</span>
                      <span className="font-medium">{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Analysis Results Grid */}
              {analysis && analysis.analysis && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fadeIn">
                  
                  {/* Card 1: Language & Script Identification */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-slate-700">
                        <Cpu className="w-4 h-4 text-teal-600" />
                        <span>Language Identification</span>
                      </div>
                      <span className="text-lg">{analysis.analysis.flag}</span>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500">Detected Language:</span>
                        <span className="font-bold text-slate-800">
                          {analysis.analysis.name} ({analysis.analysis.language})
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500">Unicode Script:</span>
                        <span className="font-medium text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded text-[11px]">
                          {analysis.analysis.script}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500">Code-Mixed / Hinglish:</span>
                        <span
                          className={`font-semibold px-2 py-0.5 rounded text-[11px] ${
                            analysis.analysis.is_code_mixed
                              ? 'bg-amber-100 text-amber-800 border border-amber-300'
                              : 'bg-slate-200 text-slate-600'
                          }`}
                        >
                          {analysis.analysis.is_code_mixed ? 'Yes (Hinglish/Code-Mixed)' : 'Monolingual'}
                        </span>
                      </div>
                      <div className="pt-2">
                        <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                          <span>Confidence Score:</span>
                          <span className="font-bold font-mono text-teal-700">
                            {Math.round(analysis.analysis.confidence * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-teal-600 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${Math.round(analysis.analysis.confidence * 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2: mNER & Slot Preservation */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-slate-700">
                        <ShieldCheck className="w-4 h-4 text-emerald-600" />
                        <span>mNER Entity Shielding</span>
                      </div>
                      <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">
                        Zero Entity Loss
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-500 leading-relaxed">
                      Protects Order IDs, RMA numbers, error codes, and serials from translation distortion.
                    </p>

                    {clirResults?.alignment?.entities && Object.keys(clirResults.alignment.entities).length > 0 ? (
                      <div className="space-y-1.5">
                        {Object.entries(clirResults.alignment.entities).map(([slot, val]) => (
                          <div
                            key={slot}
                            className="p-1.5 rounded bg-white border border-slate-200 flex items-center justify-between text-xs font-mono"
                          >
                            <span className="text-slate-500 text-[10px]">{slot}</span>
                            <span className="font-bold text-emerald-700">{val}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="py-3 text-center text-xs text-slate-400 italic">
                        No tracking or ticket IDs found in current prompt
                      </div>
                    )}
                  </div>

                  {/* Card 3: Cultural Pragmatics & Honorifics */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-slate-700">
                        <Sparkles className="w-4 h-4 text-violet-600" />
                        <span>Cultural Pragmatics</span>
                      </div>
                      <span className="text-xs bg-violet-100 text-violet-800 font-medium px-2 py-0.5 rounded">
                        Politeness Tier
                      </span>
                    </div>

                    <div className="bg-white p-2.5 rounded-lg border border-slate-200 max-h-36 overflow-y-auto">
                      <div className="text-[11px] font-mono text-slate-700 whitespace-pre-wrap leading-relaxed">
                        {analysis.politeness_directive || 'Default polite professional English'}
                      </div>
                    </div>
                  </div>

                </div>
              )}

              {/* Cross-Lingual RAG Retrieval Bridge */}
              {clirResults && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-50/70 to-slate-50 border border-indigo-200 space-y-3 animate-fadeIn">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Search className="w-4 h-4 text-indigo-600" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900">
                        Cross-Lingual Information Retrieval (CLIR) Bridge
                      </h4>
                    </div>
                    <span className="text-xs bg-indigo-100 text-indigo-800 font-semibold px-2.5 py-0.5 rounded-full">
                      Foreign Query ➔ English Manual Concepts
                    </span>
                  </div>

                  {/* Visual Alignment Flow */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-white p-3 rounded-lg border border-slate-200 text-xs">
                    <div>
                      <span className="text-slate-500 font-semibold block mb-1">
                        Original Customer Query ({clirResults.alignment?.source_language?.toUpperCase() || 'SRC'}):
                      </span>
                      <p className="text-slate-800 italic bg-slate-50 p-2 rounded border border-slate-100">
                        "{clirResults.original_query}"
                      </p>
                    </div>

                    <div>
                      <span className="text-indigo-600 font-semibold block mb-1 flex items-center space-x-1">
                        <span>Aligned English Concept Search Vector:</span>
                        <ArrowRight className="w-3.5 h-3.5 text-indigo-500" />
                      </span>
                      <p className="text-indigo-950 font-mono bg-indigo-50/60 p-2 rounded border border-indigo-100 font-medium">
                        "{clirResults.effective_search_query}"
                      </p>
                    </div>
                  </div>

                  {/* Matched English Knowledge / Precedents */}
                  <div className="space-y-2 pt-1">
                    <span className="text-xs font-semibold text-slate-700 block">
                      Retrieved English Precedents from MongoDB ({clirResults.matches_count} Matches):
                    </span>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {clirResults.exemplars && clirResults.exemplars.map((ex) => (
                        <div
                          key={ex.exemplar_id}
                          className="p-3 bg-white rounded-lg border border-slate-200 space-y-1.5 shadow-2xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-mono font-bold text-indigo-600">
                              {ex.exemplar_id}
                            </span>
                            <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-medium">
                              {ex.category}
                            </span>
                          </div>
                          <h5 className="text-xs font-semibold text-slate-800">{ex.title}</h5>
                          <p className="text-[11px] text-slate-600 line-clamp-2">
                            {ex.expert_thought}
                          </p>
                          {ex.policy_citation && (
                            <div className="text-[10px] text-emerald-700 font-medium">
                              {ex.policy_citation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              )}
            </>
          ) : (
            /* Supported Language Matrix Tab */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fadeIn">
              {Object.entries(supportedLanguages).map(([code, meta]) => (
                <div
                  key={code}
                  className="p-4 rounded-xl border border-slate-200 bg-white hover:border-teal-300 hover:shadow-sm transition-all space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{meta.flag}</span>
                      <div>
                        <h4 className="text-sm font-bold text-slate-900">{meta.name}</h4>
                        <span className="text-xs text-slate-500">{meta.native_name}</span>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded uppercase font-semibold">
                      {code}
                    </span>
                  </div>

                  <div className="space-y-1 text-xs border-t border-slate-100 pt-2 text-slate-600">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Script:</span>
                      <span className="font-medium text-slate-800">{meta.script}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Honorific Tier:</span>
                      <span className="font-medium text-teal-700">{meta.default_honorific}</span>
                    </div>
                  </div>

                  <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Native Greeting Pattern
                    </span>
                    <p className="text-xs text-slate-700 italic">"{meta.sample_greeting}"</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-100 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <div className="flex items-center space-x-2">
            <span className="inline-block w-2 h-2 rounded-full bg-teal-500"></span>
            <span>Active NLP: Sub-ms LID + Unicode Script Profiler + Cross-Lingual Concept Bridge</span>
          </div>
          <button
            onClick={onClose}
            className="px-5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-medium transition-colors shadow-xs"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
}
