import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import ChatHeader from './components/ChatHeader';
import MessageBubble from './components/MessageBubble';
import QuickPrompts from './components/QuickPrompts';
import VendorPortal from './components/VendorPortal';
import ChatHistorySidebar from './components/ChatHistorySidebar';
import TicketModal from './components/TicketModal';
import WebsiteHomepage from './components/WebsiteHomepage';
import ChatWidget from './components/ChatWidget';
import FaqKnowledgeExplorer from './components/FaqKnowledgeExplorer';
import SystemArchitectureModal from './components/SystemArchitectureModal';
import { 
  sendChatMessage, 
  checkHealth, 
  fetchChatSessions, 
  fetchChatSession, 
  deleteChatSession 
} from './services/api';

const INITIAL_MESSAGE = {
  id: 'welcome-1',
  role: 'assistant',
  text: `Hello! I'm your Customer Support assistant.

How can I help you today?
* Track an order or shipment (\`ORD-10021\`, \`ORD-10023\`)
* Search FAQ policy & store guidelines (30-day return, warranty, international shipping)
* Troubleshoot error codes & device setup
* Return an item & generate prepaid RMA labels
* File warranty replacement claims
* Create or check vendor support tickets (\`TCK-10021-VND\`)`,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
};

export default function App() {
  const [activeTab, setActiveTab] = useState('website'); // 'website' | 'chat' | 'vendor'
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessionState, setSessionState] = useState({});
  const [isMongoOnline, setIsMongoOnline] = useState(true);

  // FAQ & Stats Modal State
  const [isFaqOpen, setIsFaqOpen] = useState(false);
  const [isStatsOpen, setIsStatsOpen] = useState(false);

  // History state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sessionsList, setSessionsList] = useState([]);

  // Ticket inspection modal state
  const [modalTicketId, setModalTicketId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadHistorySessions = async () => {
    const res = await fetchChatSessions();
    if (res && res.sessions) {
      setSessionsList(res.sessions);
    }
  };

  useEffect(() => {
    async function init() {
      const health = await checkHealth();
      setIsMongoOnline(health.mongodb_connected);
      await loadHistorySessions();
    }
    init();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeTab === 'chat') {
      scrollToBottom();
    }
  }, [messages, loading, activeTab]);

  useEffect(() => {
    if (activeTab === 'chat') {
      inputRef.current?.focus();
    }
  }, [activeTab]);

  const handleSendMessage = async (textToSend = null) => {
    const messageText = (textToSend || input).trim();
    if (!messageText || loading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const data = await sendChatMessage(messageText, sessionId);
      
      if (data.session_id) {
        setSessionId(data.session_id);
      }
      if (data.session_state) {
        setSessionState(data.session_state);
      }

      const botMessage = data.bot_turn || {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        text: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        token_metrics: data.token_metrics
      };

      setMessages((prev) => {
        const updated = [...prev];
        if (data.user_turn && updated.length > 0 && updated[updated.length - 1].role === 'user') {
          updated[updated.length - 1] = data.user_turn;
        }
        return [...updated, botMessage];
      });
      await loadHistorySessions();
    } catch (err) {
      const errorMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        text: `Error connecting to assistant: ${err.message}. Please check that the server is running.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleSelectSession = async (sId) => {
    try {
      setLoading(true);
      const data = await fetchChatSession(sId);
      if (data && data.session) {
        setSessionId(data.session.session_id);
        setSessionState(data.session.state || {});
        if (data.session.messages && data.session.messages.length > 0) {
          setMessages(data.session.messages);
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    } finally {
      setLoading(false);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    }
  };

  const handleDeleteSession = async (sId) => {
    try {
      await deleteChatSession(sId);
      if (sId === sessionId) {
        handleResetChat();
      }
      await loadHistorySessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleResetChat = () => {
    setMessages([INITIAL_MESSAGE]);
    setSessionId(null);
    setSessionState({});
    setInput('');
  };

  return (
    <div className="flex h-screen w-full flex-col bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
      
      {/* App Header with Navigation & Mode Switcher */}
      <ChatHeader
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onResetChat={handleResetChat}
        sessionState={sessionState}
        isMongoOnline={isMongoOnline}
        messageCount={messages.length}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onOpenFaqExplorer={() => setIsFaqOpen(true)}
        onOpenSystemStats={() => setIsStatsOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden relative">
        
        {/* VIEW 1: Website Homepage with Bottom-Right Floating Chatbot Widget */}
        {activeTab === 'website' && (
          <div className="flex-1 overflow-y-auto relative">
            <WebsiteHomepage
              onOpenChat={() => setIsWidgetOpen(true)}
              onSelectPrompt={(promptText) => {
                setIsWidgetOpen(true);
                handleSendMessage(promptText);
              }}
              onSwitchTab={(tab) => setActiveTab(tab)}
              onOpenFaqExplorer={() => setIsFaqOpen(true)}
              onOpenSystemStats={() => setIsStatsOpen(true)}
            />

            {/* Bottom-Right Floating Chatbot Widget Launcher & Popup */}
            <ChatWidget
              isOpen={isWidgetOpen}
              onToggleOpen={() => setIsWidgetOpen((prev) => !prev)}
              messages={messages}
              input={input}
              setInput={setInput}
              loading={loading}
              handleSendMessage={handleSendMessage}
              handleResetChat={handleResetChat}
              onOpenTicket={(tId) => setModalTicketId(tId)}
              onExpandToFullScreen={() => {
                setIsWidgetOpen(false);
                setActiveTab('chat');
              }}
              isMongoOnline={isMongoOnline}
            />
          </div>
        )}

        {/* VIEW 2: Full-Screen Workspace Chat Interface */}
        {activeTab === 'chat' && (
          <div className="flex flex-1 overflow-hidden">
            
            {/* Collapsible Chat History Sidebar */}
            <ChatHistorySidebar
              isOpen={sidebarOpen}
              onClose={() => setSidebarOpen(false)}
              sessions={sessionsList}
              currentSessionId={sessionId}
              onSelectSession={handleSelectSession}
              onNewChat={handleResetChat}
              onDeleteSession={handleDeleteSession}
            />

            {/* Conversation Window */}
            <div className="flex flex-1 flex-col overflow-hidden bg-zinc-950">
              
              {/* Messages Feed */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3.5 max-w-3xl w-full mx-auto">
                {messages.map((msg) => (
                  <MessageBubble 
                    key={msg.id} 
                    message={msg} 
                    onOpenTicket={(tId) => setModalTicketId(tId)}
                  />
                ))}

                {loading && (
                  <div className="flex items-center gap-2 text-xs text-zinc-500 py-1">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-zinc-400" />
                    <span>Assistant is thinking...</span>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Quick Suggestion Pills */}
              <div className="max-w-3xl w-full mx-auto">
                <QuickPrompts 
                  onSelectPrompt={(prompt) => handleSendMessage(prompt)} 
                  disabled={loading} 
                />
              </div>

              {/* Input Bar */}
              <div className="border-t border-zinc-800 bg-zinc-900/90 p-3">
                <form 
                  onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                  className="flex items-center gap-2 max-w-3xl mx-auto"
                >
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about an order, return, warranty, or ticket..."
                    disabled={loading}
                    className="flex-1 rounded-lg border border-zinc-800 bg-zinc-950 px-3.5 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:border-zinc-700 focus:outline-none"
                  />

                  <button
                    type="submit"
                    disabled={!input.trim() || loading}
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-40"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
              </div>

            </div>

          </div>
        )}

        {/* VIEW 3: Vendor Desk Portal */}
        {activeTab === 'vendor' && (
          <VendorPortal />
        )}

      </div>

      {/* Ticket Details Inspection Modal */}
      {modalTicketId && (
        <TicketModal
          ticketId={modalTicketId}
          onClose={() => setModalTicketId(null)}
        />
      )}

      {/* FAQ Knowledge Base Explorer Modal */}
      <FaqKnowledgeExplorer
        isOpen={isFaqOpen}
        onClose={() => setIsFaqOpen(false)}
        onSelectQuestionToChat={(faqQuestion) => {
          setActiveTab('chat');
          handleSendMessage(faqQuestion);
        }}
      />

      {/* AI System Architecture Dashboard Modal */}
      <SystemArchitectureModal
        isOpen={isStatsOpen}
        onClose={() => setIsStatsOpen(false)}
      />

    </div>
  );
}
