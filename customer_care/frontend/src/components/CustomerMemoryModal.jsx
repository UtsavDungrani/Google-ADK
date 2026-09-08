import React, { useState, useEffect } from 'react';
import { 
  X, 
  Brain, 
  User, 
  Clock, 
  Calendar, 
  Plus, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Tv, 
  Headphones, 
  Coffee, 
  Package, 
  Ticket, 
  ShieldCheck, 
  Loader2,
  RefreshCw,
  Database,
  ArrowRight
} from 'lucide-react';
import { 
  fetchCustomerProfilesApi, 
  fetchCustomerProfileApi, 
  addCustomerNoteApi 
} from '../services/api';

export default function CustomerMemoryModal({ 
  isOpen, 
  onClose, 
  activeUserId, 
  onSelectUser 
}) {
  const [profiles, setProfiles] = useState([]);
  const [selectedId, setSelectedId] = useState(activeUserId || 'CUST-9921');
  const [currentProfile, setCurrentProfile] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [savingNote, setSavingNote] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    async function loadProfiles() {
      setLoading(true);
      try {
        const data = await fetchCustomerProfilesApi();
        if (isMounted && data && data.profiles) {
          setProfiles(data.profiles);
          // If activeUserId matches one, select it
          const initial = data.profiles.find(p => p.customer_id === activeUserId) 
            ? activeUserId 
            : (data.profiles[0]?.customer_id || 'CUST-9921');
          setSelectedId(initial);
        }
      } catch (err) {
        console.error('Failed to load profiles:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadProfiles();
    return () => { isMounted = false; };
  }, [isOpen, activeUserId]);

  const loadProfileDetail = async (cid) => {
    setLoading(true);
    try {
      const data = await fetchCustomerProfileApi(cid);
      if (data && data.profile) {
        setCurrentProfile(data.profile);
        setEpisodes(data.episodes || []);
      }
    } catch (err) {
      console.error('Failed to fetch profile detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedId && isOpen) {
      loadProfileDetail(selectedId);
    }
  }, [selectedId, isOpen]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim() || savingNote) return;

    setSavingNote(true);
    try {
      await addCustomerNoteApi(selectedId, newNote.trim());
      setNewNote('');
      await loadProfileDetail(selectedId);
    } catch (err) {
      console.error('Failed to add note:', err);
    } finally {
      setSavingNote(false);
    }
  };

  const getDeviceIcon = (itemName = '') => {
    const nameLow = itemName.toLowerCase();
    if (nameLow.includes('tv')) return <Tv className="w-4 h-4 text-blue-400" />;
    if (nameLow.includes('headphone')) return <Headphones className="w-4 h-4 text-purple-400" />;
    if (nameLow.includes('espresso') || nameLow.includes('coffee')) return <Coffee className="w-4 h-4 text-amber-400" />;
    return <Package className="w-4 h-4 text-emerald-400" />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto p-2 sm:p-4 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative flex flex-col w-full max-w-4xl h-[90vh] max-h-[90vh] bg-zinc-900 border border-zinc-700/70 rounded-2xl shadow-2xl overflow-hidden my-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/60 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 shrink-0">
              <Brain className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-zinc-100">Cross-Session Long-Term Memory</h2>
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Cognitive AI Architecture
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Persistent Semantic Knowledge Graph & Chronological Episodic Memory across past conversations
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded-lg transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Persona Switcher Bar */}
        <div className="flex items-center gap-2 px-6 py-3 bg-zinc-950/40 border-b border-zinc-800 overflow-x-auto shrink-0">
          <span className="text-xs font-medium text-zinc-400 whitespace-nowrap flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-purple-400" /> Switch Persona:
          </span>
          {profiles.map((p) => {
            const isSelected = selectedId === p.customer_id;
            const isActive = activeUserId === p.customer_id;
            return (
              <button
                key={p.customer_id}
                onClick={() => setSelectedId(p.customer_id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isSelected 
                    ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20 border border-purple-400' 
                    : 'bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700/80 border border-zinc-700/50'
                }`}
              >
                <span>{p.customer_name}</span>
                <span className="opacity-70 text-[10px]">({p.customer_id})</span>
                {isActive && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm" title="Currently Active Chat Persona" />
                )}
              </button>
            );
          })}
        </div>

        {/* Modal Body */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6 space-y-6">
          {loading && !currentProfile ? (
            <div className="flex flex-col items-center justify-center py-16 text-zinc-400 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
              <p className="text-sm">Recalling long-term memory graph...</p>
            </div>
          ) : currentProfile ? (
            <>
              {/* Persona Overview Header Card */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-zinc-950 border border-zinc-800/80 gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
                    {currentProfile.customer_name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-semibold text-zinc-100">{currentProfile.customer_name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono">
                        {currentProfile.customer_id}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400">{currentProfile.customer_email} • {currentProfile.customer_phone}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                  <div className="text-right">
                    <span className="text-[10px] uppercase tracking-wider text-zinc-500 block">Churn Risk Trajectory</span>
                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border inline-block ${
                      currentProfile.churn_risk > 0.6 
                        ? 'bg-red-500/10 text-red-400 border-red-500/30' 
                        : currentProfile.churn_risk > 0.3 
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' 
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    }`}>
                      {currentProfile.churn_risk_level || 'Low Risk'} ({Math.round(currentProfile.churn_risk * 100)}%)
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] uppercase tracking-wider text-zinc-500 block">Preferred Tone</span>
                    <span className="text-xs font-medium text-zinc-200">
                      {currentProfile.preferred_tone || 'Standard'}
                    </span>
                  </div>

                  {activeUserId !== currentProfile.customer_id && (
                    <button
                      onClick={() => {
                        onSelectUser(currentProfile.customer_id);
                        onClose();
                      }}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded-lg transition-colors shadow-sm ml-2"
                    >
                      <span>Start Chat as {currentProfile.customer_name.split(' ')[0]}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {/* Grid: Devices & Tickets */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Registered Owned Devices */}
                <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                      <Package className="w-3.5 h-3.5 text-blue-400" /> Owned Products & Devices
                    </h4>
                    <span className="text-[10px] text-zinc-500">{currentProfile.owned_devices?.length || 0} registered</span>
                  </div>
                  <div className="space-y-2">
                    {currentProfile.owned_devices && currentProfile.owned_devices.length > 0 ? (
                      currentProfile.owned_devices.map((dev, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 flex items-start gap-3">
                          <div className="p-2 rounded-lg bg-zinc-800/80 border border-zinc-700/50 mt-0.5">
                            {getDeviceIcon(dev.item_name)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium text-zinc-200 truncate">{dev.item_name}</p>
                            <p className="text-[11px] text-zinc-400 font-mono">Order: {dev.order_id} • S/N: {dev.serial_number}</p>
                            <p className="text-[10px] text-zinc-500">Purchased: {dev.purchase_date} • Delivery: {dev.delivery_date || 'In Transit'}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-zinc-500 italic py-2">No registered devices on record.</p>
                    )}
                  </div>
                </div>

                {/* Active Support Tickets */}
                <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                      <Ticket className="w-3.5 h-3.5 text-amber-400" /> Cross-Session Support Tickets
                    </h4>
                    <span className="text-[10px] text-zinc-500">{currentProfile.active_tickets?.length || 0} active</span>
                  </div>
                  <div className="space-y-2">
                    {currentProfile.active_tickets && currentProfile.active_tickets.length > 0 ? (
                      currentProfile.active_tickets.map((tid, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-amber-400">{tid}</span>
                            <span className="text-[10px] text-zinc-400">Vendor Support Case</span>
                          </div>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
                            Persistent
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 text-center">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                        <p className="text-xs text-zinc-400">No unresolved tickets</p>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* Chronological Episodic Interaction Timeline */}
              <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-purple-400" /> Episodic Memory Timeline (Past Sessions)
                    </h4>
                    <p className="text-[11px] text-zinc-500">Historical interaction milestones recalled across conversation sessions</p>
                  </div>
                  <span className="text-xs text-purple-400 font-mono">{episodes.length} Episodes</span>
                </div>

                <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-zinc-800">
                  {episodes.map((ep, idx) => (
                    <div key={ep.episode_id || idx} className="relative">
                      {/* Timeline dot */}
                      <div className={`absolute -left-6 top-1.5 w-3 h-3 rounded-full border-2 ${
                        ep.resolved 
                          ? 'bg-emerald-500 border-emerald-950' 
                          : 'bg-purple-500 border-purple-950'
                      }`} />
                      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800/80 space-y-1.5">
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <span className="text-xs font-medium text-zinc-300 flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-zinc-500" /> {ep.timestamp}
                          </span>
                          <div className="flex items-center gap-1.5">
                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${
                              ep.resolved 
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            }`}>
                              {ep.resolved ? 'Resolved' : 'In Progress'}
                            </span>
                            <span className="text-[10px] text-zinc-500 font-mono">{ep.episode_id}</span>
                          </div>
                        </div>
                        <p className="text-xs text-zinc-300 leading-relaxed">{ep.summary}</p>
                        {ep.topics && ep.topics.length > 0 && (
                          <div className="flex items-center gap-1.5 pt-1 flex-wrap">
                            {ep.topics.map((t, tIdx) => (
                              <span key={tIdx} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50">
                                {t}
                              </span>
                            ))}
                            {ep.sentiment_at_conclusion && (
                              <span className="text-[10px] text-purple-400 italic ml-auto">
                                Concluding Valence: {ep.sentiment_at_conclusion}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Persistent Notes & Facts */}
              <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-yellow-400" /> Learned Customer Facts & Traits
                  </h4>
                  <span className="text-[10px] text-zinc-500">Autonomous & Manual Memory Notes</span>
                </div>

                <div className="space-y-1.5">
                  {currentProfile.persistent_notes && currentProfile.persistent_notes.length > 0 ? (
                    currentProfile.persistent_notes.map((note, nIdx) => (
                      <div key={nIdx} className="flex items-start gap-2 p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300">
                        <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 mt-0.5 shrink-0" />
                        <span>{note}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-zinc-500 italic">No notes recorded yet.</p>
                  )}
                </div>

                {/* Add New Fact Input */}
                <form onSubmit={handleAddNote} className="flex items-center gap-2 pt-2 border-t border-zinc-800">
                  <input
                    type="text"
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Teach the agent a new persistent fact about this customer (e.g. 'Prefers SMS updates')..."
                    className="flex-1 px-3 py-1.5 text-xs rounded-lg bg-zinc-900 border border-zinc-700 focus:outline-none focus:border-purple-500 text-zinc-200"
                  />
                  <button
                    type="submit"
                    disabled={!newNote.trim() || savingNote}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium transition-colors disabled:opacity-50"
                  >
                    {savingNote ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}
                    <span>Save to Memory</span>
                  </button>
                </form>
              </div>

              {/* Architecture Educational Card */}
              <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-800/30 flex items-start gap-3">
                <Database className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                <div className="text-xs text-zinc-300 leading-relaxed">
                  <strong className="text-purple-300">How Cross-Session Memory Works in Google ADK:</strong> While standard LLMs lose context between sessions, our architecture persists a <strong className="text-zinc-100">Semantic Graph</strong> and <strong className="text-zinc-100">Episodic Timeline</strong> in MongoDB. Upon session initialization, the agent synthesizes the customer's past tickets, owned devices, and preferences, greeting returning users with complete awareness.
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-zinc-800 bg-zinc-950/80 shrink-0">
          <span className="text-[11px] text-zinc-500 font-mono">
            Database: MongoDB customer_care_db • Memory Collections: customer_profiles & customer_episodes
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
