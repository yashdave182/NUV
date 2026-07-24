import { useState } from 'react'
import { Bot, X, Send, Sparkles, Volume2, Mic, CheckCircle2, Sprout } from 'lucide-react'
import { useAppStore } from '../store/appStore'

const QUICK_PROMPTS = [
  'What fertilizer should I apply for Cotton?',
  'Check today\'s Mandi price trends in Gujarat',
  'Am I eligible for PM-KISAN scheme?',
  'How to prevent pink bollworm in Kharif?',
]

export function FloatingAIAssistant() {
  const { user, language } = useAppStore()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: `Namaste ${user?.name || 'Farmer'}! I am AgriNova AI Assistant. How can I help your farm today in ${language || 'English'}?`,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [speaking, setSpeaking] = useState(false)

  const handleSend = (textToSend?: string) => {
    const query = textToSend || input
    if (!query.trim()) return

    const userMsg = { sender: 'user' as const, text: query }
    setMessages(prev => [...prev, userMsg])
    if (!textToSend) setInput('')
    setLoading(true)

    // Simulate AI response generation with domain context
    setTimeout(() => {
      let responseText = `Based on your crop parameters, for ${query.toLowerCase().includes('mandi') ? 'Mandi prices' : 'crop advisory'}, we recommend checking modal market rates and applying balanced N-P-K (120:60:60 kg/ha).`
      if (query.toLowerCase().includes('fertilizer')) {
        responseText = `For Cotton in Kharif season, apply 120 kg N, 60 kg P2O5, and 60 kg K2O per hectare. Split Nitrogen into 3 doses at 30, 60, and 90 DAS.`
      } else if (query.toLowerCase().includes('mandi')) {
        responseText = `Ahmedabad APMC Cotton modal price is ₹6,880/quintal (Up 2.4% today). Best selling time is within 5 days.`
      } else if (query.toLowerCase().includes('pm-kisan')) {
        responseText = `Yes! Smallholder farmers with landholding under 2.0 hectares in Gujarat are 100% eligible for PM-KISAN ₹6,000 annual direct benefit transfer.`
      }

      setMessages(prev => [...prev, { sender: 'ai', text: responseText }])
      setLoading(false)
    }, 700)
  }

  const handleSpeak = (text: string) => {
    if ('speechSynthesis' in window) {
      if (speaking) {
        window.speechSynthesis.cancel()
        setSpeaking(false)
        return
      }
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.onend = () => setSpeaking(false)
      setSpeaking(true)
      window.speechSynthesis.speak(utterance)
    }
  }

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-20 right-4 lg:bottom-6 lg:right-6 z-40 w-14 h-14 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-xl hover:scale-105 active:scale-95 transition-all flex items-center justify-center cursor-pointer border-2 border-white/80"
        title="AgriNova Floating AI Assistant"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Bot className="w-7 h-7 animate-bounce" />}
        <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 border-2 border-white rounded-full"></span>
      </button>

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-36 right-4 lg:bottom-22 lg:right-6 z-50 w-[92vw] sm:w-[400px] h-[520px] max-h-[80vh] bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-emerald-100/90 flex flex-col overflow-hidden animate-slide-up">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-emerald-700 to-teal-700 text-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-md">
                <Sprout className="w-5 h-5 text-emerald-200" />
              </div>
              <div>
                <h3 className="text-sm font-bold tracking-tight">AgriNova AI Assistant</h3>
                <p className="text-[10px] text-emerald-200 font-medium">Multi-Lingual Farm Advisory</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'ai' && (
                  <div className="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold mt-1">
                    AI
                  </div>
                )}
                <div
                  className={`p-3 rounded-2xl text-xs max-w-[82%] leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-emerald-600 text-white rounded-tr-none font-medium'
                      : 'bg-white text-slate-800 rounded-tl-none border border-slate-200/80 shadow-sm'
                  }`}
                >
                  <p>{m.text}</p>
                  {m.sender === 'ai' && (
                    <button
                      onClick={() => handleSpeak(m.text)}
                      className="mt-2 flex items-center gap-1 text-[10px] font-bold text-emerald-700 hover:underline"
                    >
                      <Volume2 className="w-3 h-3" />
                      {speaking ? 'Stop Audio' : 'Listen in Audio'}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-2 items-center text-xs text-emerald-700 font-bold p-2 bg-emerald-50 rounded-xl w-fit">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>AI analyzing farm data...</span>
              </div>
            )}
          </div>

          {/* Quick Prompts */}
          <div className="p-2.5 bg-slate-100/70 border-t border-slate-200/60 overflow-x-auto flex gap-1.5 scrollbar-none">
            {QUICK_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="whitespace-nowrap text-[10px] font-semibold bg-white text-slate-700 hover:bg-emerald-50 hover:text-emerald-800 border border-slate-200 px-2.5 py-1 rounded-full transition-all flex-shrink-0"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="p-3 bg-white border-t border-slate-100 flex items-center gap-2">
            <input
              className="flex-1 text-xs bg-slate-100 px-3.5 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 font-medium"
              placeholder="Ask AI about crops, mandi prices, or schemes..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="p-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl shadow transition-all cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
