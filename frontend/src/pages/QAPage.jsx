import React, { useState } from 'react';
import api from '../lib/api';
import { Search, ChevronRight, FileText, Loader2 } from 'lucide-react';

const QAPage = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await api.post('/ask', { question });
      setResult(response.data);
    } catch (error) {
      console.error('Failed to get answer', error);
      alert('Failed to get answer. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row gap-8 animate-fade-in-up">
      {/* Left Column: Q&A Interaction */}
      <div className="flex-1">
        <div className="glass-card rounded-3xl overflow-hidden shadow-xl border border-white/10">
          <div className="p-8 border-b border-gray-700/50 bg-white/5">
            <h2 className="text-3xl font-extrabold text-white flex items-center tracking-tight">
              <Search className="mr-3 text-brand-400" size={32} />
              Query Intelligence
            </h2>
            <p className="text-base text-gray-400 mt-2 font-medium">
              Ask specific questions and our AI will extract exact answers directly from your uploaded corpus.
            </p>
          </div>
          
          <div className="p-8">
            <form onSubmit={handleAsk} className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-6 w-6 text-gray-400 group-focus-within:text-brand-400 transition-colors" />
              </div>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="E.g., What is the termination notice period?"
                className="w-full pl-12 pr-16 py-5 rounded-2xl border-2 border-transparent bg-white/10 text-white shadow-sm focus:bg-white/20 focus:ring-0 focus:border-brand-500 text-lg font-medium transition-all duration-300 outline-none placeholder-gray-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 top-2 bottom-2 bg-brand-600 text-white rounded-xl px-5 hover:bg-brand-500 hover:shadow-lg hover:shadow-brand-500/30 transition-all duration-300 flex items-center justify-center disabled:opacity-50"
              >
                {loading ? <Loader2 className="animate-spin" size={24} /> : <ChevronRight size={28} strokeWidth={3} />}
              </button>
            </form>

            {result && (
              <div className="mt-10 animate-fade-in-up">
                <div className="bg-gradient-to-br from-brand-900/40 to-white/5 border border-brand-500/30 p-8 rounded-3xl shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1.5 h-full bg-brand-400"></div>
                  <h3 className="text-xs font-bold text-brand-300 uppercase tracking-widest mb-3 flex items-center">
                    <span className="w-2 h-2 rounded-full bg-brand-400 mr-2 animate-pulse"></span>
                    AI Generated Answer
                  </h3>
                  <p className="text-xl text-gray-200 leading-relaxed font-medium">
                    {result.answer}
                  </p>
                  {result.confidence !== undefined && (
                    <div className="mt-6 flex items-center">
                      <div className="text-xs text-brand-300 font-bold bg-brand-900/50 px-4 py-1.5 rounded-full shadow-sm border border-brand-500/30">
                        Confidence Score: {(result.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Column: Citations */}
      {result && result.citations && result.citations.length > 0 && (
        <div className="w-full md:w-1/3 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <div className="glass-card rounded-3xl p-8 sticky top-28 border border-white/10 shadow-xl">
            <h3 className="text-xl font-extrabold text-white mb-6 flex items-center">
              <FileText className="mr-2 text-indigo-400" size={24} />
              Verifiable Sources
            </h3>
            <div className="space-y-5 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              {result.citations.map((cite, idx) => (
                <div key={idx} className="p-5 bg-white/5 rounded-2xl border border-white/10 hover:border-indigo-500/50 hover:bg-white/10 transition-all duration-300 group">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-sm font-bold text-gray-300 truncate pr-2 group-hover:text-indigo-300 transition-colors" title={cite.document}>
                      {cite.document}
                    </span>
                    <span className="text-xs font-bold bg-indigo-900/50 text-indigo-300 px-3 py-1 rounded-full whitespace-nowrap border border-indigo-500/30">
                      Pg {cite.page}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 italic leading-relaxed relative">
                    <span className="absolute -left-2 -top-1 text-2xl text-gray-600 font-serif">"</span>
                    {cite.excerpt}
                    <span className="absolute -bottom-3 text-2xl text-gray-600 font-serif">"</span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QAPage;
