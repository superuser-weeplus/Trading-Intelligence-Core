'use client';

import React, { useState, useRef, useEffect } from 'react';
import { DashboardLayout } from '../../components/DashboardLayout';
import { aiService } from '../../services/api';
import { 
  MessageSquare, 
  Send, 
  BrainCircuit, 
  User,
  ShieldAlert
} from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  time: string;
}

export default function AIChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your AI Strategy Advisor. How can I help you refine your technical strategy, optimize risk management settings, or explain technical indicators today?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input;
    setInput('');
    
    // Add user message
    const userMsg: ChatMessage = {
      sender: 'user',
      text: userText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    
    setLoading(true);

    try {
      // Query backend FastAPI + Gemini LLM advisor endpoint
      const res = await aiService.chat(userText);
      
      const assistantMsg: ChatMessage = {
        sender: 'assistant',
        text: res.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error(err);
      const errMsg: ChatMessage = {
        sender: 'assistant',
        text: "Sorry, I encountered an error connecting to the LLM backend server. Please verify your FastAPI backend is running and the Gemini API key is configured.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="border-b border-[#1e1e24] pb-6">
        <h1 className="text-3xl font-bold tracking-tight">AI Strategy Advisor</h1>
        <p className="text-zinc-400 text-sm">Interactive LLM assistant to design rules, analyze risk factors, and optimize backtests.</p>
      </div>

      <div className="card-premium h-[600px] flex flex-col justify-between overflow-hidden">
        {/* Chat History Viewport */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#09090b]/20">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === 'user';
            return (
              <div 
                key={idx} 
                className={`flex space-x-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse space-x-reverse' : ''}`}
              >
                {/* Avatar Icon */}
                <div className={`h-8 w-8 rounded-full shrink-0 flex items-center justify-center border ${
                  isUser 
                    ? 'bg-blue-600/10 text-blue-500 border-blue-500/20' 
                    : 'bg-zinc-800 text-zinc-400 border-[#1e1e24]'
                }`}>
                  {isUser ? <User className="h-4 w-4" /> : <BrainCircuit className="h-4 w-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`p-4 rounded-xl border space-y-1 ${
                  isUser 
                    ? 'bg-blue-600/10 border-blue-500/20 text-zinc-100 rounded-tr-none' 
                    : 'bg-[#0c0c0f] border-[#1e1e24] text-zinc-300 rounded-tl-none'
                }`}>
                  <p className="text-sm leading-relaxed whitespace-pre-line">{msg.text}</p>
                  <span className="block text-[10px] text-zinc-500 text-right">{msg.time}</span>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex space-x-3 max-w-md">
              <div className="h-8 w-8 rounded-full bg-zinc-800 border border-[#1e1e24] flex items-center justify-center text-zinc-400">
                <BrainCircuit className="h-4 w-4" />
              </div>
              <div className="p-4 rounded-xl border bg-[#0c0c0f] border-[#1e1e24] text-zinc-400 rounded-tl-none">
                <div className="flex items-center space-x-1">
                  <div className="h-2 w-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="h-2 w-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="h-2 w-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input box */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-[#1e1e24] bg-[#0c0c0f] flex space-x-3">
          <input
            type="text"
            placeholder="Ask anything about indicators, AI signals, or risk..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-[#09090b] border border-[#1e1e24] rounded-lg px-4 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex items-center justify-center p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-all"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>

      <div className="bg-[#0c0c0f] border border-[#1e1e24] rounded-xl p-4 flex items-start space-x-3 text-xs text-zinc-500 mt-6">
        <ShieldAlert className="h-4 w-4 text-zinc-400 shrink-0 mt-0.5" />
        <p>
          Risk Disclaimer: The AI Advisor represents logical technical heuristics and does not constitute financial advice. Simulate strategies extensively in the Backtesting Lab prior to live deployment.
        </p>
      </div>
    </DashboardLayout>
  );
}
